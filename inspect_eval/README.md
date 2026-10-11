# Inspect implementation

This adapter reuses `heldout-v1` (120 attacks, 12 benign controls and 24
legitimate-forward controls), the original prompts, request-scoring helpers and
recipient guard. It does not replace the LangGraph runner or historical results.
All actions are simulated; no mail is sent.

See [validation status and recorded setup](VALIDATION.md) for completed checks
and the separate real-model validation run.

## Install and test

Run from the repository root with Python 3.11 or newer:

```bash
uv sync --extra inspect --locked
uv run --extra inspect python -m unittest -v inspect_eval.test_transfer
```

Inspect 0.3.278 is the initially tested version (the exact environment is in
`uv.lock`). The offline tests replay scripted outcomes through the unchanged
original runner and adapter. They also exercise actual Inspect tool dispatch,
checking that each sample makes exactly one model generation.

## Run against an existing vLLM server

Keep the server running with the appropriate tool parser/chat template. This
command connects to it; it does not allocate GPUs or launch another model server.

```bash
uv run --extra inspect inspect eval inspect_eval/task.py --model vllm/Qwen/Qwen2.5-7B-Instruct --model-base-url http://127.0.0.1:8000/v1 -T smoke_test=true -T repetitions=1 --max-samples 1 --log-dir results/inspect/qwen-smoke
```

After confirming three valid trials, run each condition separately:

```bash
uv run --extra inspect inspect eval inspect_eval/task.py --model vllm/Qwen/Qwen2.5-7B-Instruct --model-base-url http://127.0.0.1:8000/v1 -T prompt=baseline --max-samples 1 --log-dir results/inspect/qwen-baseline
uv run --extra inspect inspect eval inspect_eval/task.py --model vllm/Qwen/Qwen2.5-7B-Instruct --model-base-url http://127.0.0.1:8000/v1 -T prompt=defense --max-samples 1 --log-dir results/inspect/qwen-defense
uv run --extra inspect inspect eval inspect_eval/task.py --model vllm/Qwen/Qwen2.5-7B-Instruct --model-base-url http://127.0.0.1:8000/v1 -T prompt=defense -T enforce_recipients=true --max-samples 1 --log-dir results/inspect/qwen-enforced
```

Or run all three sequentially with an incremental machine-readable summary:

```bash
uv run --extra inspect python -m inspect_eval.validate
```

This stops before the next condition if a run has invalid or unscored trials.
Each invocation creates a new timestamped directory; it does not overwrite past runs.

Defaults: temperature 0, 256 output tokens, dataset seed 0, three repetitions.
`--max-samples 1` sets concurrency, not the number of cases. Each full run has
468 samples, with unique case/repetition IDs. Do not add `--epochs`: repetitions
are explicit samples so Inspect cannot average invalid repetitions into valid
ones. They are repeatability checks, not independent statistical samples.

View logs with `uv run --extra inspect inspect view --log-dir results/inspect`.
Summarize a run with:

```bash
uv run --extra inspect python -m inspect_eval.summarize path/to/run.eval
```

## Semantics and parity boundaries

- `single_decision` uses Inspect's `generate(tool_calls="single")`: one model
  response, followed by tool execution, with no recovery turn. Tool choice is
  required (`any` in Inspect); parallel calls are disabled. Like the original
  runner, it records all calls if a model nevertheless emits several.
- `attempted_asr` and control leakage use the original recipient classifier;
  false refusal means not requesting the exact expected internal forward.
  These rates exclude invalid trials and include their valid denominators.
- Missing calls, parsing failures and model-generation exceptions are invalid.
  Tool errors are logged separately, preserving the historical runner's handling
  of ordinary ToolNode validation errors. Non-string recipients are marked
  invalid instead of crashing the historical string-based scorer.
- Allowed execution comes only from events recorded inside the actual tool,
  never inferred from a requested forward. Execution/block counts include
  observed events even on invalid trials. An empty denominator yields NaN
  (unavailable), not a claim of zero failures.
- Logs retain sample metadata, model/configuration, timestamps, tool arguments
  and results, dataset/prompt hashes, enforcement setting and request scores.
  Unexpected Inspect-level failures remain in the log; the summary reports
  unscored samples separately rather than treating them as safe.
- Tool descriptions retain their original purpose, but Inspect adds parameter
  descriptions and serializes schemas/messages through its own provider. Runtime,
  GPU, batching and formatting differences can change fresh model decisions.
  Scorer parity is tested; identical historical aggregate results are not promised.

Framework documentation: [tools](https://inspect.aisi.org.uk/tools.html),
[solvers](https://inspect.aisi.org.uk/solvers.html),
[providers](https://inspect.aisi.org.uk/providers.html).
