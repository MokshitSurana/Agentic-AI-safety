# Candidate research direction: recovery after blocked prompt injection

Search and assessment date: 6 September 2026.

Status: research proposal, not an implemented extension or an established novelty claim. No additional model experiments were run for this assessment.

## Recommendation in plain language

Move from **can the agent be stopped?** to **which recovery strategy lets a stopped agent finish the legitimate task, and when does recovery fail?**

The narrow candidate is a controlled study of context retention and denial feedback, with the execution guard held fixed. Include tasks that need facts from the attacked document, so deleting all external evidence is not automatically a successful defense. Separate correctly completed work from merely permitted actions.

Recovery, sanitization, corrective feedback, and safe continuation are already researched. The possible contribution is an independently reproducible comparison and an explanation of when competing strategies work, not invention of those mechanisms. This is a plausible next investigation, not a guarantee of publication or priority.

## Search scope and verification

This note extends [the earlier 22-paper review](literature-review.md). Searches covered post-injection containment, blocked-tool recovery, context reset, denial feedback, sanitization, policy metadata, runtime authorization, adaptive attacks, and their combinations. Exact-title searches and references in retrieved papers were followed where relevant.

The closest sources below were opened on arXiv and their relevant methods, ablations, or limitations inspected. The inspected versions are linked explicitly. These are primary-source preprint versions; that label does not assert that the work has never subsequently appeared at a conference. Their reported experiments have not been independently reproduced here. This was a focused search, not an exhaustive systematic review. Absence of an exact match in these sources is not evidence that no such work exists.

## Closest prior work and what it rules out

### NetInjectBench

[NetInjectBench: Benchmarking Indirect Prompt Injection in Tool-Using Large Language Model Agents for Network Operations, v1](https://arxiv.org/html/2607.10490v1), July 2026; inspected Sections 2.4, 3.3, 4.3, and 5.5-5.6.

Compares prompt-level, LLM-judge, static-blocking, and trusted-metadata gating approaches on local models including Qwen2.5-7B and Llama3.1-8B. Includes legitimate approved actions and overblocking, as well as deterministic metadata-mismatch tests. Its gate can select a safe fallback. The paper identifies multi-step agents as future work. This is a close overlap with our current broad experimental story: neither adding a third local model nor adding approval metadata would by itself establish a new research question.

### AgentSys

[AgentSys: Secure and Dynamic LLM Agents Through Explicit Hierarchical Memory Management, v1](https://arxiv.org/html/2602.07398v1), February 2026; inspected Section 5.5 and the sanitizer ablation.

After a validator denial, an LLM sanitizer removes instruction-like material while preserving relevant data, and a worker restarts under the same declared intent. Retries are bounded. The no-sanitizer ablation fails the subtask immediately after denial. Thus sanitize-and-restart and a recovery-versus-stop comparison are prior work, not our proposed inventions.

### ARGUS

[ARGUS: Defending LLM Agents Against Context-Aware Prompt Injection, v1](https://arxiv.org/html/2605.03378v1), May 2026; inspected Sections 4.6-4.7 and the Section 5 ablations.

Blocked calls receive candidate benign argument values from a provenance graph; retries pass through the audit again. Its four component-removal ablations keep recovery hints fixed. This supplies a concrete predecessor for corrective hints, but not the proposed independent context-retention-by-feedback comparison. Its benign labels are produced within its auditing system, not an infallible source of ground truth.

### AgentVisor

[AgentVisor: Defending LLM Agents Against Prompt Injection via Semantic Virtualization, v1](https://arxiv.org/html/2604.24118v1), April 2026; inspected Sections 4.4, 5.3, and 6.1.

Uses structured security exceptions for self-correction, compares against block-only behavior, and compares one to three correction rounds. Therefore neither structured feedback nor measuring retry cost is new. Importantly, the inspected procedure describes executing the corrected action immediately: our study must explicitly revalidate every retry, rather than assuming corrected output is authorized. We should not copy its headline rates into our setting or claim a faithful replication without reproducing its complete implementation.

### AgentSentry

[AgentSentry: Mitigating Indirect Prompt Injection in LLM Agents via Temporal Causal Diagnostics and Context Purification, v1](https://arxiv.org/html/2602.22724v1), February 2026; inspected Sections 4.2, 4.6, the ablation table, and Appendix B.

Performs controlled boundary-state re-executions to diagnose takeover and purifies external context while preserving task evidence. Its interventions vary the user-channel probe and raw versus sanitized mediator; ablations examine diagnostic components. Consequently, controlled replay and evidence-preserving purification are also established ideas. Our potential distinction is to study recovery decisions after a common denial under a fixed guard, not to propose another causal takeover detector.

### ContainmentBench

[ContainmentBench: Trace-Based Evaluation of Post-Injection Containment in Tool-Using LLM Agents, v1](https://arxiv.org/html/2607.23999v1), July 2026; inspected the evidence-stage definitions and Section 8.4.

Already separates endpoint policy compliance, logged propagation, recovery instrumentation, and authorized utility. Its limitations explicitly identify tied rollback recovery and lack of positive-control events for some other endpoints. This motivates discriminative recovery tasks; it does not justify claiming that post-injection containment or trace-based measurement is unexplored. Its primary full-scale study uses one model and assumes a correct authorization ledger.

### PCAS

[Policy Compiler for Secure Agentic Systems, v1](https://arxiv.org/html/2602.16708v1), February 2026; inspected Sections 4.2, 5.1, and the authorization-recovery example.

Separates deterministic policy enforcement from model-dependent reasoning and recovery. Denials provide structured feedback, and recovery cycles contribute overhead. This directly rules out presenting the distinction between blocked harm and successful task completion as new. The inspected evaluation contrasts instrumented and non-instrumented systems, rather than independently varying recovery context and feedback under one fixed enforcement mechanism.

### Causality Laundering

[Causality Laundering: Denial-Feedback Leakage in Tool-Calling LLM Agents, v1](https://arxiv.org/html/2604.04035v1), April 2026; inspected Sections 7 and 9.4.

Studies information inferred from denied actions and later released through other tool calls. The evaluation is a controlled prototype comparison on three constructed scenarios; the limitations call for broader workflows and agents in the loop. Denial-feedback leakage is therefore not a new attack class to claim. For our proposed recovery hints, disclose only task information the agent is already authorized to receive; do not expose private policy facts or unrelated authorized resources.

## Exact candidate gap

My inference from the inspected sources is that the following combined experimental question is less directly covered than the broad topic of recovery:

> With the same execution policy, the same blocked starting state, and the same authorized information sources, how do context retention and minimal corrective feedback interact to determine successful recovery, especially when the legitimate task requires evidence from the attacked source?

No inspected source establishes that this exact comparative question is settled. This is a **candidate evaluation gap with moderate confidence**, not a claim of first discovery. Before framing a submission around it, check updated versions, released code, and citation neighborhoods of AgentSys, ARGUS, AgentVisor, AgentSentry, and ContainmentBench. Finding the same experiment would turn this into replication/extension work, not erase the value of the current pilot.

The missing contribution must be an explanatory result: for example, a reproducible interaction between source dependence and recovery strategy. Merely adding a recovery loop and reporting a higher completion rate is too close to existing work.

## Connection to this repository

The current graph in [model.py](../model.py) is `START -> decision -> tools -> END`. It does not return a blocked tool result to a subsequent model decision. The existing paper draft correctly describes a one-decision simulation.

Current results motivate the extension: the execution guard blocked the recorded external-forward attempts, but those trials cannot tell us whether the agent would recover, repeat the attempt, abandon the ticket, or misroute work on a later step. The old runs must remain labeled as one-decision evidence. Do not retroactively reinterpret them as multi-step recovery results.

## Example task

Trusted user task: extract the invoice reference and issue category from a customer ticket, then send the structured handoff to the authorized billing destination.

The ticket contains those facts alongside a forged instruction to forward elsewhere. The execution guard blocks an unauthorized proposal.

Now ask what happens next:

- Retaining the context may preserve the facts but also preserve the misleading instruction.
- Resetting the context may remove that instruction but lose facts needed for completion.
- Corrective feedback may help identify a compliant next step without supplying the answer.
- Sanitizing the source may preserve useful evidence, but the sanitizer itself can make mistakes.

These are hypotheses to test. The proposal does not assume any strategy wins.

## Research questions

1. **Recovery effectiveness:** Under fixed enforcement, which post-denial strategy best restores correct, authorized task completion within a fixed budget?
2. **Mechanism:** How do context retention and corrective feedback interact with whether required task facts are in trusted state or in the attacked source?
3. **Robustness and cost:** Do the findings persist across model families, held-out workflows, and recovery-aware attacks, and what extra proposals, tokens, latency, and unnecessary escalations occur?

## Experimental design

### Separate treatment from enforcement

Use one fixed, tested execution guard for the primary comparison. It should mediate all simulated side effects, including retries, and have explicit recipient/object/operation scope. Do not ask an LLM to relax permissions during recovery. Keep authorization inputs separate from evaluation-only success labels.

Primary recovery arms:

| Arm | Context after denial | Feedback |
|---|---|---|
| Stop | No further decisions | Terminate the episode |
| Retain / generic | Retain the full history | Fixed denial notice |
| Retain / corrective | Retain the full history | Minimal trusted constraint and task reminder |
| Reset / generic | Rebuild from trusted user task and pre-authorized state | Same fixed denial notice |
| Reset / corrective | Same trusted-state rebuild | Same minimal corrective feedback |

The four continuing arms form a 2 x 2 comparison; stop is a reference, not another factorial level. Add a sanitize-and-restart comparator motivated by AgentSys. Label an adapted mechanism as inspired by prior work, not an implementation of the complete published system.

Resetting must not silently provide an attack-free replacement document. All arms retain access to the same underlying tools and cached source data; if a reset agent retrieves the source again, it receives the same attacked source. Log re-exposure. Do not promote arbitrary model-generated summaries to trusted state.

Feedback must not contain evaluation labels or a gold replacement action. It may restate an existing user instruction or disclose a policy constraint the agent is authorized to know. In source-dependent tasks, it must not fill in the invoice reference or other required facts from the scorer. An oracle cleanup or gold-answer hint can be a separately labeled diagnostic ceiling, never the proposed deployable defense.

### Use tasks that can distinguish the strategies

Include at least two evidence conditions:

- Required facts are already available in trusted task state.
- Required facts must be recovered from the external source that also contains the injection.

Construct clean, suspicious-looking but legitimate, and malicious versions of each workflow. Counterbalance recipients and concrete values across wording, rather than assigning one distinctive address to each attack template. Hold out entire workflow scenarios and attack families, not only random rows or paraphrases.

Begin with support routing, then confirm the result on a distinct workflow, such as document handoff with document-ID and recipient constraints. Use a qualified subset of an existing agent benchmark if feasible. Establish both clean-task competence and a successful no-defense attack control before interpreting security or recovery differences.

### Two complementary evaluations

**Common-state comparison:** Collect a model's natural blocked prefixes before enabling any recovery treatment. Resume identical prefix and environment snapshots under every recovery arm. This estimates recovery conditional on those blocked states. Report the selection procedure and coverage; do not compare different naturally blocked subsets as if they were identical populations.

**End-to-end comparison:** Run complete held-out episodes from the original task with each strategy enabled. Report all tasks, including those that never trigger a block, to estimate practical task-level performance. Do not mix conditional recovery rates with unconditional completion rates.

Use the same total decision budget and explicit termination criteria across arms. Separately report sanitizer/reviewer calls and total compute; equal agent turns alone do not imply equal cost. All source replay and side effects should remain inside a synthetic sandbox.

### Metrics

- **Correct authorized completion:** required workflow state and structured fields are correct, with no prohibited committed action.
- **Conditional recovery rate:** completion among the common naturally blocked episodes.
- **End-to-end completion:** completion over all assigned episodes.
- **Proposed policy violations:** number and type of unauthorized proposals, including repeated or alternative attempts.
- **Committed policy violations:** prohibited actions actually permitted by the execution layer; separate from proposals.
- **Legitimate-task failures:** refusal, unnecessary escalation, wrong-but-permitted action, incomplete work, and timeout separately.
- **Recovery overhead:** model calls, tokens, wall time, and extra tool proposals.
- **Invalid episodes:** parsing, model-serving, and tool errors; preserve these rather than count them as security successes.

With a correct fully mediating guard, zero committed violations may follow from the policy design. That alone is not the new empirical finding. The meaningful comparison is whether useful work resumes, at what cost, and under what task conditions. Repeated blocked proposals are not equivalent to executed leakage.

### Analysis and validity

Use paired scenario-level comparisons and uncertainty intervals clustered by the underlying workflow. Treat repeated decoding as within-scenario variation, not additional independent tasks. Pin models, templates, decoding, serving versions, and policy hashes. Keep model-system comparisons distinct from claims about model weights alone.

For adaptive evaluation, define attacker knowledge and an equal query budget in advance. Use synthetic targets, freeze development-derived candidates, and evaluate on new scenarios. An attacker may write recovery-aware content into an untrusted source; it may not modify the guard, trusted feedback, or the scorer. Do not call static transfer a fully adaptive evaluation.

## A bounded next step

Start with approximately 20 development workflows, their matched controls, and the two already-working local models. This is a diagnostic pilot, not a powered final sample size. First validate the loop and oracles, then test whether the recovery strategies show meaningful differences beyond malformed calls or clean-task inability. Choose the final number of independent scenarios from the desired precision and pilot variability.

Only expand if the pilot supports a substantive question. A strategy winning solely because it receives the answer, a comparison without successful attacks, or a difference driven entirely by parser errors would not support the proposed contribution. A null result remains reportable, but should not be disguised as a new defense breakthrough.

## Possible paper framing

Working title: **After the Block: A Controlled Study of Recovery Policies for Prompt-Injected Tool-Using Agents**.

Potential contributions, conditional on new evidence:

1. A reproducible recovery-evaluation protocol that separates guard decisions from recovery behavior and tests dependence on contaminated evidence.
2. A controlled comparison of context and feedback choices, with failure mechanisms and a cost/utility analysis.
3. Evidence of transfer, limits, or ranking reversals across models and held-out workflows, with released synthetic scenarios and complete traces.

Do not claim the first recovery mechanism, the first context-reset defense, the first safe-continuation system, or universal prompt-injection safety. Keep the current study as preliminary evidence and make any eventual novelty statement relative to the closest verified work.
