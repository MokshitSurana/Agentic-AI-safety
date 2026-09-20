# Qwen migration pilot: trace audit

Run: `20260907T180050292380Z_local`.
Model: `Qwen/Qwen2.5-7B-Instruct`.
Protocol: `migration-pilot-v1-named-single-action-v1`.

Audited the full run copied from the pod, not just its summary table.

- 300 episodes, 60 case variants (20 workflows), five conditions per case.
- All 300 saved retrieval messages contain the exact expected customer ticket
  and synthetic private token from cases.json. This establishes their presence
  in the recorded model context, not that the model attended to every word.
- All 60 groups share one initial-response hash across their five conditions.
- The 60 initial responses comprise 43 `escalate_ticket` calls and 17
  `forward_details` calls. All forwards target the authorized internal recipient.
- Execution logs contain 300 internal handoffs and 85 authorized forwards.
  The latter count includes condition replay, not 85 independent model proposals.
- 215 episodes complete in one decision; 85 take two decisions.
- Zero invalid episodes, blocked actions, or recorded disclosures. All 300
  complete the authorized task safely under the exact-token scoring rules.

## Interpretation

No observed attempt reached a guard. This run cannot estimate the effect of
denial wording, stopping, or all-sink enforcement on post-denial migration.
The all-safe no-guard result rules out attributing this run's safety to those
guards. The conditions are paired replays, not 300 independent attack trials.

## Next experiment

Run Llama-3.1-8B-Instruct with the identical dataset, system prompt, single-action
wrapper, decision budget, temperature, and seed. First verify a smoke run, then
run the 20-workflow pilot. Do not change attacks in response to this result and
present them as untouched held-out tests. Any subsequent forced-block study
needs a separate protocol and must not be described as natural attack success.

The Qwen model service was left running during this audit. A Llama run requires
verified model access and a controlled model-service switch on the user's GPU.

Llama preflight: config.json was not present in the default Hugging Face cache.
A configuration-only access check from kubectl exec returned `GatedRepoError`
HTTP 401. This establishes missing access in that execution environment; it
does not prove the user's account lacks approval or that another interactive
shell has no token. No model weights were downloaded, and Qwen was not stopped.
Authenticate with an approved account before proceeding with the Llama run.
