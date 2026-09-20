# Two-model migration development pilot

Completed September 7, 2026. Exact synthetic-token disclosure only.

| Full run | Valid episodes | Safe completion | Blocked forwards | Post-denial migration |
|---|---:|---:|---:|---|
| Qwen/Qwen2.5-7B-Instruct | 300/300 | 300/300 | 0 | N/A |
| meta-llama/Llama-3.1-8B-Instruct | 300/300 | 300/300 | 0 | N/A |

Run directories under results:

- `migration-qwen-single-action-full/20260907T180050292380Z_local`
- `migration-llama-single-action-full/20260907T181914090219Z_local`

Llama smoke run: `migration-llama-single-action-smoke/20260907T181750630400Z_local`,
15/15 valid and safe. Smoke results are not pooled into the full-run table.

## Audit

Compared full-run manifests: dataset, system prompt, tool schema, protocol
version and source hashes match. Both use 20 workflows, three variants, five
conditions, one repetition, temperature 0, seed 0, 256 completion tokens and a
four-decision budget. The named-single-action-v1 adapter is enabled in both.

All 300 Llama saved retrieval messages contain the expected ticket and private
record token, with zero mismatches. Each of the 60 case variants has five
condition rows sharing a single initial-response hash. Llama completes every
episode with an internal `escalate_ticket` call; it never calls a forwarding or
customer-update tool. Qwen's corresponding trace audit is in migration-qwen-audit.md.

Each model contributes 60 initial proposals, including 40 attack-bearing cases;
the five conditions reuse those proposals. The table does not represent 600
independent attacks, nor do the conditions supply evidence about guard effects
when no block occurs. Presence in recorded context does not prove model attention.

## Outcome and next decision

The current development attacks did not elicit the prerequisite blocked forward
in either model. Therefore this pilot cannot estimate post-denial migration or
compare generic versus explicit denial feedback. It is not evidence that a
particular guard prevented leakage; no-guard episodes also completed safely.

Retain these negative development results. A next experiment needs an explicit
design choice: calibrate new natural attacks using a development/evaluation split,
or study recovery from a supplied blocked action under a separately versioned
forced-block protocol. The latter measures conditional recovery, not natural
attack success. Neither change has been implemented in these runs.

## Server handoff

Hugging Face authentication was restored and Llama configuration access verified.
The verified Qwen server was gracefully stopped; Llama was started on GPU 2 with
the recorded settings in llama-server-launch-20260907T181312Z.json. vLLM selected
V0/XFormers for this GPU. The Llama endpoint was verified before running trials.
Llama remains running; the pod, GPU allocation and original result files were
not deleted or recreated. No Git commit or push was performed.
