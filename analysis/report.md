# Held-out results audit

All six runs contain 468 unique case/repetition pairs, with zero invalid trials or recorded errors. Dataset and prompt hashes match the frozen local sources; all runs use temperature 0, 256 completion tokens, and three repetitions. Scoring was recomputed from model tool calls.

| Model | Condition | Attempt ASR | False refusals | Allowed external | Blocked | Legitimate completed | Cases with varying decisions |
|---|---|---:|---:|---:|---:|---:|---:|
| Qwen/Qwen2.5-7B-Instruct | baseline | 357/360 (99.2%) | 6/72 | not logged | not logged | not logged | 0/156 |
| Qwen/Qwen2.5-7B-Instruct | defense | 225/360 (62.5%) | 6/72 | not logged | not logged | not logged | 0/156 |
| Qwen/Qwen2.5-7B-Instruct | enforced | 225/360 (62.5%) | 6/72 | 0 | 225 | 66 | 0/156 |
| meta-llama/Llama-3.1-8B-Instruct | baseline | 279/360 (77.5%) | 24/72 | 279 | 0 | 48 | 0/156 |
| meta-llama/Llama-3.1-8B-Instruct | defense | 186/360 (51.7%) | 12/72 | 186 | 0 | 60 | 0/156 |
| meta-llama/Llama-3.1-8B-Instruct | enforced | 186/360 (51.7%) | 12/72 | 0 | 186 | 60 | 0/156 |

## Paired attack transitions: baseline to defense

Counts below are repeated trials, not independent examples. Case-level details are in paired_attacks.csv.

| Model | Fixed | Worsened | Remained unsafe | Remained safe |
|---|---:|---:|---:|---:|
| Qwen/Qwen2.5-7B-Instruct | 132 | 0 | 225 | 3 |
| meta-llama/Llama-3.1-8B-Instruct | 99 | 6 | 180 | 75 |

Defense and enforced runs have identical action, recipient, attack-success, and false-refusal outcomes for every paired trial. This does not assert byte-identical escalation reasons.

## Interpretation and limits

Stronger prompts reduce attempted violations for both models but leave substantial vulnerability. Enforcement blocks the observed external attempts by construction; this verifies the guard for this synthetic forwarding task rather than general prompt-injection immunity.

There are 120 distinct attacks, crossed from 12 scenarios and 10 templates, plus 36 controls. Repetitions share cases and templates. No independent-trial confidence intervals or significance claims are supplied.

Each wording template is tied to one of two external addresses; address and wording effects are confounded. The synthetic suite was authored after inspecting development results and is not an independent external benchmark. Enforcement was added after held-out results were observed.

The Qwen baseline and prompt-only runs predate execution instrumentation: their executed actions are not retrospectively invented. Historical data_leakage means attempted external forwarding. False refusal means failure to select the exact expected forward, not necessarily a verbal refusal.

Model checkpoint revisions, complete server flags, GPU allocation, and package versions were not captured in these CSVs. The conversation records different model-specific templates and changed hardware/runtime settings. Cross-model comparisons concern configured systems, not isolated model weights. A current environment snapshot cannot prove historical run settings.

Raw inputs are preserved under results; manifest.json records their checksums. Reproduce with: uv run python analyze_heldout.py.
