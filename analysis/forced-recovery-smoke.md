# Forced recovery smoke test

Run: `20260907T184554485697Z_local` under results/forced-recovery-llama-smoke.
Model: meta-llama/Llama-3.1-8B-Instruct. Protocol: forced-block-recovery-v1.

- 12/12 episodes valid; all start with an experimenter-supplied blocked forward.
- Nine episodes permit model recovery, and all nine complete safely.
- Zero model retries, cross-tool migration attempts, or committed disclosures.
- Three stop controls permit no model call and have zero task completion by design.
- Generic and explicit feedback have identical observed outcomes on this workflow.

This verifies that the pipeline reaches denial and records model continuation.
It does not demonstrate a feedback effect, natural attack success, or general
safety. There is only one workflow with three ticket variants, not nine independent
workflows. Keep this smoke run separate from a subsequent multi-workflow pilot.

Implementation verification: all 47 automated tests pass. Existing natural-attack
code and results were not modified. New runs include exact source snapshots.
No full forced-recovery experiment or Git push was performed.
