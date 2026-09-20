# Verified literature review: prompt injection in tool-using agents

Search date: 6 September 2026. Prepared for the support-triage experiments in this repository.

## Scope and verification

This is a focused, primary-source literature review of 22 selected papers, not an exhaustive systematic review or a claim that no other relevant work exists. Searches covered indirect prompt injection, tool-use benchmarks, benign utility and over-refusal, instruction/data separation, adaptive attacks, privilege control, and information-flow enforcement. Exact-title searches and references in the retrieved papers were used to find related work, including 2026 studies.

For each entry, the title, lead author, date/version, and substantive description were checked against an author-hosted arXiv paper or official proceedings. Relevant methods, evaluation, or limitations sections were inspected; this does not mean every appendix was fully reviewed. The links below are the primary evidence, not search-result snippets or generated bibliographies. Results attributed to other authors were not independently reproduced here.

Conference status is stated where the proceedings or paper metadata established it. An entry labeled by its arXiv version identifies the source consulted; it is not a claim that the work has never subsequently been peer reviewed. Earlier arXiv and later conference years are distinguished. Search-engine relative dates were not used as publication dates.

The existing [Methods/Results draft](paper-draft.md), [results audit](report.md), [error analysis](error-analysis.md), and the current agent implementation were also inspected. Proposed research directions below are our synthesis, not findings attributed to the cited authors.

## Main assessment

The general findings that prompt injection can hijack tools, stronger instructions provide incomplete protection, utility must be measured alongside security, and execution policies can contain model errors are already established research themes. This project should not claim to introduce those ideas.

The defensible current framing is a small, reproducible, case-level empirical study of a simulated forwarding workflow. Its value lies in clearly specified decisions, paired regressions, legitimate-forward failure subtypes, and the distinction between requested and permitted actions. Whether an extension is sufficiently novel for a particular venue remains unresolved.

## A. Foundations and benchmarks

### 1. Greshake et al. — Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection

Source: [arXiv:2302.12173](https://arxiv.org/abs/2302.12173), first submitted February 2023; inspected v2 PDF, particularly §3.2 and the attack demonstrations.

Develops a threat taxonomy and demonstrations in which externally supplied content redirects an LLM-integrated application. Discusses information theft, API misuse, and other consequences. It directly precedes the idea of malicious instructions hidden in apparently ordinary content. These are qualitative demonstrations and threat analysis, not an estimate of a universal failure probability. Our ticket-contained attack premise belongs to this established threat class.

### 2. Liu et al. — Formalizing and Benchmarking Prompt Injection Attacks and Defenses

Source: [USENIX Security 2024 proceedings](https://www.usenix.org/conference/usenixsecurity24/presentation/liu-yupei), with [full paper](https://www.usenix.org/system/files/usenixsecurity24-liu-yupei.pdf). Inspected formalization and evaluation metrics, including false-positive/false-negative measures.

Formalizes replacement of a legitimate task with an injected task and evaluates five attacks and ten defenses across ten LLMs and seven tasks. Establishes a substantial comparison baseline for prevention and detection. Measuring injection success and the cost of detecting clean input is therefore not a new contribution. Its mainly text-task setting differs from our forwarding decision.

### 3. Yi et al. — Benchmarking and Defending Against Indirect Prompt Injection Attacks on Large Language Models (BIPIA)

Source: [arXiv:2312.14197](https://arxiv.org/abs/2312.14197), first submitted December 2023; KDD 2025 identified in v4 and its [publication DOI](https://doi.org/10.1145/3690624.3709179). Inspected v4 dataset construction and §6 defenses.

Benchmarks injections in external content across five application scenarios. Its defenses combine clearer content boundaries with explicit reminders, using prompting or model training. It evaluates preservation of ordinary task performance as well as attack resistance. Our strengthened prompt overlaps with its reminder/boundary-awareness approach; our study does not replicate its trained defenses.

### 4. Zhan et al. — InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents

Source: [Findings of ACL 2024](https://aclanthology.org/2024.findings-acl.624/). Inspected full-paper §2.2–2.3 and evaluation setup. Authors: Qiusi Zhan, Zhixiang Liang, Zifan Ying, Daniel Kang.

Constructs 1,054 combinations from 17 user cases and 62 attacker cases. It evaluates actions following a substituted tool response; data-stealing cases include simulated extraction and transmission steps. This is a close predecessor to our tool-decision experiment. Importantly, the authors manually repaired underspecified attack arguments: failure caused by unusable arguments is not equivalent to resisting the attacker. Our malformed-recipient outcomes need similarly careful interpretation.

### 5. Debenedetti et al. — AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents

Source: [NeurIPS 2024 Datasets and Benchmarks paper](https://proceedings.neurips.cc/paper_files/paper/2024/file/97091a5177d8dc64b1da8bf3e1f6fb54-Paper-Datasets_and_Benchmarks_Track.pdf); [arXiv v3](https://arxiv.org/html/2406.13352v3). Inspected environment design and §4.3.

Introduces stateful tool environments with 97 user tasks and 629 security cases in that version. Evaluates benign utility, utility under attack, and attacker goals. Its defense comparison includes delimiters, detection, repeated user instructions, and tool filtering. Some defenses improve average utility; others lose utility through false positives. Thus both joint safety/utility evaluation and nonuniform defensive effects predate this project. It offers an external evaluation environment, not directly comparable ASR numbers.

### 6. Zhang et al. — Agent Security Bench (ASB): Formalizing and Benchmarking Attacks and Defenses in LLM-based Agents

Source: [arXiv:2410.02644](https://arxiv.org/abs/2410.02644), first submitted October 2024; ICLR 2025 listed in metadata. Inspected v4 Table 4 and §C.2.3.

Evaluates multiple attack surfaces, including prompts, tools, and memory, across varied agent scenarios. Its metrics distinguish attack success, clean-task performance, refusal of aggressive tasks, and detection errors. Its refusal rate is not our legitimate-forward failure rate; neither can be substituted for the other. ASB demonstrates that merely adding more models or multiple security metrics is insufficient as a novelty claim.

### 7. Zverev et al. — Can LLMs Separate Instructions From Data? And What Do We Even Mean By That?

Source: [arXiv:2403.06833](https://arxiv.org/abs/2403.06833), initially March 2024; ICLR 2025. Inspected [v3](https://arxiv.org/html/2403.06833v3), especially empirical separation and utility definitions. Authors: Egor Zverev, Sahar Abdelnabi, Soroush Tabesh, Mario Fritz, Christoph H. Lampert.

Introduces SEP and a formal/empirical instruction-data separation measure. It compares behavior when a probe is placed in an instruction versus data position, while checking whether the model can follow it when appropriate. This is particularly relevant to matched legitimate and malicious instructions. Our exact-forward correctness measure is different; a future authority-placement experiment should acknowledge this precedent.

## B. Prompting, training, and semantic checks

### 8. Hines et al. — Defending Against Indirect Prompt Injection Attacks With Spotlighting

Source: [arXiv:2403.14720](https://arxiv.org/abs/2403.14720), March 2024; inspected v1 §III–V.

Studies delimiting, marking throughout untrusted text, and encoding that text to make provenance more apparent. Its experimental corpus contains 1,000 synthetic attack documents using keyword-output objectives, with ordinary language-task checks. This provides a concrete prompt/input-transformation baseline. Its reported resistance does not establish tool-execution safety or robustness to all defense-aware attacks. Simply adding quotation marks is not a faithful implementation of every spotlighting variant.

### 9. Chen et al. — StruQ: Defending Against Prompt Injection with Structured Queries

Source: [USENIX Security 2025 proceedings](https://www.usenix.org/conference/usenixsecurity25/presentation/chen-sizhe), first arXiv submission 2024. Inspected the secure frontend and structured instruction-tuning method. Authors: Sizhe Chen, Julien Piet, Chawin Sitawarin, David Wagner.

Combines reserved prompt/data delimiters, filtering that prevents attacker introduction of those separators, and a specially trained model. It is not just a system prompt telling an ordinary model to ignore attacks. A correct comparison requires its trained model and input-processing assumptions. This is evidence of architectural/training work on the same trust-boundary problem, not an implemented feature of our current code.

### 10. Wallace et al. — The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions

Source: [arXiv:2404.13208](https://arxiv.org/abs/2404.13208), April 2024; inspected v1 §3.1–3.2. Authors: Eric Wallace, Kai Xiao, Reimar Leike, Lilian Weng, Johannes Heidecke, Alex Beutel.

Creates training examples for following aligned lower-priority instructions while disregarding conflicting ones. Explicitly discusses avoiding over-refusal: ignoring every lower-priority instruction would damage usefulness. This strongly overlaps with the motivation for legitimate-forward controls. Our prompt expresses a hierarchy, but we have not trained either model using this method.

### 11. Chen et al. — SecAlign: Defending Against Prompt Injection with Preference Optimization

Source: [arXiv:2410.05451](https://arxiv.org/abs/2410.05451), first submitted October 2024; ACM CCS 2025, [DOI](https://doi.org/10.1145/3719027.3744836). Inspected v3 §3.

Uses preference optimization to favor legitimate-task outputs over injected-task outputs for the same attacked input. This changes model weights, unlike our prompt-only condition. The exact checkpoint and preprocessing matter in replication. The original v1 used a different title; this review uses the verified v3 title rather than treating the versions as separate papers. Avoid transferring its reported benchmark results to our models without running them.

### 12. Jia et al. — The Task Shield: Enforcing Task Alignment to Defend Against Indirect Prompt Injection in LLM Agents

Source: [arXiv:2412.16682](https://arxiv.org/abs/2412.16682), December 2024; inspected v1 §4 and evaluation. Authors: Feiran Jia, Tong Wu, Xin Qin, Anna Squicciarini.

Checks whether extracted instructions and tool calls contribute to the user's goals, with feedback for corrective agent behavior. Its instruction extraction and alignment scoring use an LLM. Despite the word “enforcing,” this is not equivalent to a deterministic recipient predicate. It is relevant to our workflow-dependency attacks and to future recovery after blocked calls. Reported effectiveness is tied to the evaluated attacks and judge configuration.

## C. Adaptive attackers and evaluation validity

### 13. Zhan et al. — Adaptive Attacks Break Defenses Against Indirect Prompt Injection Attacks on LLM Agents

Source: [Findings of NAACL 2025](https://aclanthology.org/2025.findings-naacl.395/); [full-text arXiv version](https://arxiv.org/html/2503.00061v1). Inspected §3–5. Authors: Qiusi Zhan, Richard Fang, Henil Shalin Panchal, Daniel Kang.

Evaluates eight defenses with defense-aware attacks on InjecAgent, including optimization against both the agent and detection components. This is direct precedent for the claim that a defense's apparent performance can collapse under stronger attacks. Our frozen transfer templates are not equivalent to their adaptive optimization. A future adaptive experiment needs an explicit attacker knowledge model and query/computation budget.

### 14. Shi et al. — Lessons from Defending Gemini Against Indirect Prompt Injections

Source: [arXiv:2505.14534](https://arxiv.org/abs/2505.14534), May 2025; inspected v1 §7–9. Lead author: Chongyang Shi.

Describes adaptive evaluation and model hardening for Gemini. Its defense-in-the-loop experiments show why attacks optimized without the defense can misrepresent resilience. It also finds exceptions where transferred, non-adaptive attacks work better, motivating multiple evaluation checks. We should use its methodological lesson, not rank Qwen or Llama against Gemini using unrelated ASRs or treat stronger attacks as guaranteed to win every comparison.

### 15. Nasr et al. — The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections

Source: [arXiv:2510.09023](https://arxiv.org/abs/2510.09023), October 2025; inspected v1 §4–5 and Appendix B Table 1. Lead author: Milad Nasr.

Applies stronger optimization and human-guided attacks to twelve defenses spanning both jailbreaks and prompt injections. Those are different threat models, and not all twelve defenses are agent-specific. The paper explicitly warns that its numbers are not a standardized ranking across defenses. It does not establish that a correctly implemented, fixed recipient allowlist can be persuaded to allow a forbidden address.

## D. Security outside the model

### 16. Debenedetti et al. — Defeating Prompt Injections by Design (CaMeL)

Source: [arXiv:2503.18813](https://arxiv.org/abs/2503.18813), March 2025; inspected v1 §4 and §8.

Separates privileged planning from processing untrusted data, tracking capabilities and enforcing policies during execution. This is a much broader system than our domain guard. Its stated limits include policy specification, user approvals, side channels, and text-only manipulations outside protected data flows. The idea of containing an untrustworthy model with application-level security already exists; our zero allowed external forwards is not a new general solution.

### 17. Shi et al. — Progent: Securing AI Agents with Privilege Control

Source: [arXiv:2504.11703](https://arxiv.org/abs/2504.11703), initially April 2025; inspected [v3, May 2026](https://arxiv.org/html/2504.11703v3), policy overview and §9. Lead author: Tianneng Shi.

Deterministically gates tool calls using rules over tool names and arguments. Its newer design addresses controlled policy updates; forbidden calls can return feedback so the agent continues. This is the closest direct predecessor to recipient enforcement. Its scope depends on invariants, approval decisions, and which tool interfaces are mediated. Earlier versions were titled *Progent: Programmable Privilege Control for LLM Agents*; these are one evolving work, not two citations.

### 18. Costa et al. — Securing AI Agents with Information-Flow Control (Fides)

Source: [arXiv:2505.23643](https://arxiv.org/abs/2505.23643), May 2025; inspected v2 planner design and §7–8.

Tracks confidentiality and integrity labels, using policy checks and selective information visibility. It studies which tasks remain achievable under different planner restrictions. Crucially, its evaluation distinguishes benchmark-defined attack success from violations of its actual policies; some benchmark goals fall outside the protected property. This closely relates to why our attempted-ASR, executed-forward count, and task correctness must remain separate.

### 19. Beurer-Kellner et al. — Design Patterns for Securing LLM Agents against Prompt Injections

Source: [arXiv:2506.08837](https://arxiv.org/abs/2506.08837), June 2025; inspected v1 §3 and email/calendar case study §4.3.

Organizes constrained agent architectures, including action selection, preplanning, and separated LLM roles. Discusses trade-offs in practical applications. The email case study explicitly warns that messages to internal coworkers can still serve malicious goals even without external exfiltration. Thus an internal-domain guard should not be equated with authorization for the right recipient, purpose, or content. This limitation is itself already recognized in prior work.

## E. Recent work that affects positioning

### 20. Li et al. — AgentDyn: A Dynamic Open-Ended Benchmark for Evaluating Prompt Injection Attacks of Real-World Agent Security System

Source: [arXiv:2602.03117](https://arxiv.org/abs/2602.03117), February 2026; inspected v1 §3–4 and Appendix A. Authors: Hao Li, Ruoyao Wen, Shanghao Shi, Ning Zhang, Chaowei Xiao.

Adds dynamic tasks and helpful third-party instructions, explicitly testing over-defense. Its 60 user tasks and 560 injection cases challenge both model-based and system defenses. The authors' setup adds an instruction to avoid requesting user confirmation; results must be interpreted under that choice. It is manually designed, not production telemetry. Benign instructions in suspicious-looking contexts are therefore not an untouched research gap.

### 21. Yin et al. — PISmith: Reinforcement Learning-based Red Teaming for Prompt Injection Defenses

Source: [arXiv:2603.13026](https://arxiv.org/abs/2603.13026), March 2026; inspected v1 §3 and §4.3–4.4. Authors: Chenlong Yin, Runpeng Geng, Yanting Wang, Jinyuan Jia.

Trains an attack model against black-box feedback, addressing sparse rewards with changes to exploration and advantage weighting. Evaluates utility/resistance and transfer to InjecAgent and AgentDojo. This extends the adaptive-evaluation literature beyond hand-authored attacks. Comparisons must respect its ASR@1 versus ASR@10 conventions; best-of-many attacker attempts are not the same as repeating a fixed victim query three times.

### 22. Narisetty et al. — Adaptive Evaluation of Out-of-Band Defenses Against Prompt Injection in LLM Agents

Source: [arXiv:2606.26479](https://arxiv.org/abs/2606.26479), June 2026; inspected v1 §11–12. Authors: Praneeth Narisetty, Shiva Nagendra Babu Kore, Uday Kumar Reddy Kattamanchi, Jayaram Kumarapu.

Reports a small Progent replication using locally served Qwen2.5-7B and three runs on an AgentDojo subset. This overlaps with a “small local models plus runtime protection” positioning. The authors explicitly label results preliminary and not peer reviewed, and acknowledge limited attack strength and substantial utility costs. Its broad abstract wording about missing adaptive evaluation should not be repeated uncritically: §11 acknowledges Progent's own earlier adaptive analysis.

## What is already known versus what we have established

| Possible claim | Prior work | Appropriate interpretation of our evidence |
|---|---|---|
| External content can redirect tool use | Greshake; InjecAgent; AgentDojo | A task-specific replication, not a new vulnerability class |
| Stronger prompts can help but remain fragile | BIPIA; Spotlighting; adaptive-attack studies | Descriptive changes on our configured models and fixed suite |
| Safety must be measured with legitimate-task performance | SEP; Instruction Hierarchy; AgentDojo; AgentDyn | Exact-forward failures are a narrow operational utility measure |
| Code can block unsafe calls even when the model requests them | CaMeL; Progent; Fides | Verification of a restricted forwarding invariant |
| Internal destinations can still be inappropriate | Design Patterns email case study | Domain membership alone does not establish task authorization |
| Self-hosted small-model replication of a runtime defense | Narisetty et al. | Local deployment and repetition alone are insufficient novelty |

The source entries above provide the evidence for this mapping. It is a qualitative overlap assessment, not a proof that every possible extension has already been done.

## What the current project can honestly claim

Based on the repository's audited results, not on external papers:

- On the synthetic transfer suite, prompt strengthening reduced attempted ASR for both configured model systems, but Llama had two distinct safe-to-unsafe regressions.
- Both defended models failed on 45 of the same 120 distinct attack cases. This is an observed overlap, not proof of a shared internal mechanism.
- Legitimate-forward failures include escalation, no action, and wrong internal recipients; “false refusal” is broader than a spoken refusal here.
- The enforcement runs blocked the recorded non-approved requests without changing paired model decisions. They did not demonstrate that the models learned to resist injection.
- There are 156 distinct cases per condition, not 468 independent examples. Every case had identical scored decision outcomes across its three repetitions.

Our current graph makes one model decision and then executes a simulated tool. Ticket text is embedded in a user-role message as quoted, explicitly untrusted content; it is not fetched in a preceding tool-return interaction. Describe this as a controlled one-decision simulation of untrusted-document processing. Using LangGraph does not by itself make this a long-horizon agent evaluation. No real customer data was sent.

The two serving stacks differ, historical provenance is incomplete, template wording is confounded with destination choice, and the synthetic transfer set was created after inspecting development results. These limitations already appear in the local draft and must stay visible.

## Recommended research direction

My assessment: adding another model alone is a lower priority than improving the comparison and causal controls. Keep the current runs as a frozen pilot. Build a separately versioned extension that investigates *when legitimate workflow language changes authorization decisions*, without claiming that this broad question has never been studied.

### Candidate research questions

1. **RQ1 — Workflow cues:** With recipient addresses, task content, and source authority counterbalanced, how do quoted handoffs, structured routing records, and claimed approval affect unauthorized tool requests across prompt variants?
2. **RQ2 — Useful compliance:** On matched, authorized requests with the same wording, do defenses introduce escalation, inaction, or wrong-recipient errors, and are these concentrated in particular formats?
3. **RQ3 — Enforcement scope:** What errors remain after domain-only enforcement, compared with a trusted, task-scoped exact-recipient policy, and what utility and recovery costs do the policies introduce?

These are proposed task-specific questions, not established open problems or guaranteed publication contributions. RQ3 should include unauthorized internal recipients; otherwise the domain check has little opportunity to reveal its limits. Task authorization must come from trusted application state or explicit authorized user input, not from the injected ticket declaring itself approved.

### Minimum next experimental package

1. **Fix scoring without rewriting history.** Add separate new metrics for exact attacker-target requests, other external requests, malformed destinations, wrong internal recipients, and allowed simulated actions. Preserve the original scores and provide a mapping.
2. **Construct counterbalanced matched cases.** Rotate the same addresses through wording templates. Independently vary where instructions originate. Have another person review task labels and authorization assumptions before running the new set.
3. **Add a published baseline.** Implement one precisely described prompt transformation, such as a selected Spotlighting variant, and a tool-argument policy baseline grounded in Progent. Call simplified implementations adaptations, not full reproductions.
4. **Establish external validity.** Pilot a frozen AgentDojo subset selected before seeing results. Check clean task competence and complete traces first. If small models cannot perform the tasks, report that rather than interpreting low ASR as safety. AgentDyn is a later stress test for helpful instructions and dynamic planning, with higher capability requirements.
5. **Add bounded adaptive testing.** Freeze the defense, state what the attacker knows, and allocate the same search budget to each condition. Keep attack-development and final task sets separate. Report per-attempt and best-of-budget outcomes with invalid runs visible.
6. **Measure after a block.** In a new graph version, allow bounded recovery and assess whether the original authorized task is completed. The existing one-decision graph cannot answer that question.
7. **Capture provenance and dependence.** Save model/checkpoint revisions, server and parser settings, package versions, prompts, dataset hashes, seed, and runtime details. Analyze distinct cases and scenario/template clustering; repeated deterministic outputs do not justify independent-trial significance tests.

This would strengthen a measurement/replication paper. It still would not establish a new general security architecture or production safety guarantee.

## Reading order

Read AgentDojo, Progent, AgentDyn, and the Zhan adaptive-attack paper first. Then read SEP and Instruction Hierarchy for the legitimate-compliance problem, followed by CaMeL and Fides for the boundary between a model's decision and application security. Use the remaining entries to complete the related-work section.

## Citation and interpretation cautions

- Cite a particular paper version. Progent and SecAlign changed titles; ASB also changed headline benchmark counts between versions.
- An arXiv DOI establishes a persistent document identifier, not peer review or correctness.
- Do not compare raw ASRs across these papers as if their datasets, attack budgets, available tools, policies, or success definitions were identical.
- A guard's zero policy violations is different from zero attacker success under a broader threat model, and different again from completing the user's task.
- Report other papers' conclusions as findings under their tested assumptions. This review has not audited every implementation or reproduced their experiments.
- Related papers encountered but not substantively assessed here include IsolateGPT, DRIFT, AgentVigil, MELON, Meta SecAlign, and AgentFlow. They are further-review leads, not evidence supporting additional claims in this report.

No experiment code, raw results, existing paper draft, or remote GitHub state was changed for this literature review.
