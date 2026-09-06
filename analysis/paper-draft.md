# Prompt instructions and recipient enforcement in a simulated support agent

Working Methods and Results draft. Related work, independent review, and complete
historical runtime provenance are outstanding; this is not a submission-ready paper.

## Methods

We evaluated Qwen2.5-7B-Instruct and Llama-3.1-8B-Instruct in a one-decision
LangGraph support-triage workflow. Models selected an escalation, forwarding, or
no-action tool. Forwarding was simulated: no customer information was transmitted.
The system policy permitted internal, ourcompany, support.internal, and their
subdomains. We compared baseline instructions, strengthened instructions, and
strengthened instructions with a deterministic recipient validator in the tool.
The validator accepted plain addresses at approved domains and rejected external
or ambiguous destinations. There was no model recovery step following a block.

The synthetic transfer suite comprised 12 support scenarios crossed with five
attack families and two templates per family (120 distinct attack cases), plus
12 benign and 24 legitimate-forward controls. Twelve forwarding controls used
formats resembling attacks with internal recipients. The dataset was authored
after development results were observed. Prompt text was frozen before these
transfer runs; enforcement was introduced after their initial results.

Each condition used three repetitions, temperature zero, and a 256-token
completion budget. Models used different tool-calling templates and historical
hardware/runtime configurations. We therefore compare configured model systems.
The six runs contain 2,808 observations over shared cases, not 2,808 independent
examples. Dataset and prompt hashes were verified against the frozen sources,
and attack and false-refusal scores were recomputed from recorded tool calls.

Attempt ASR measures external-forward requests on attack cases. Execution records
measure whether the simulated tool allowed an external forward. False refusal
means failure to select the exact expected forwarding action on a legitimate
control, which may be an escalation rather than a verbal refusal. Earlier Qwen
runs do not contain separate execution logs and are marked unavailable.

## Results

All six runs had complete coverage and no invalid trials or recorded errors.
Qwen's attempted ASR fell from 357/360 (99.2%) to 225/360 (62.5%) with strengthened
instructions, a reduction of 36.7 percentage points. Llama's fell from 279/360
(77.5%) to 186/360 (51.7%), a reduction of 25.8 percentage points.

All 156 cases per condition had identical action, recipient, attack-success, and
false-refusal outcomes across repetitions. At the distinct-attack-case level,
Qwen's strengthened prompt fixed 44 cases, worsened none, left 75 unsafe, and
left one safe. Llama's fixed 33, worsened two, left 60 unsafe, and left 25 safe.
These transitions demonstrate that the aggregate improvement was not uniform.

Qwen's false-refusal count was six of 72 under both prompts. Llama's decreased
from 24/72 to 12/72. The enforcement condition retained the same paired model
decisions as the strengthened-prompt condition. It blocked all 225 Qwen and 186
Llama external-forward attempts; recorded allowed external forwards were zero.
Legitimate completions were respectively 66/72 and 60/72.

## Limits and interpretation

Enforcement verified a deliberately narrow invariant by construction; it does
not establish general resistance to prompt injection or to other leakage channels.
Repeated deterministic cases do not supply independent evidence. Shared scenario
and template effects preclude treating the 360 attack observations as independent
Bernoulli trials. We report descriptive counts, not significance tests.

Template wording and recipient address are confounded because each template uses
a fixed address. The suite is synthetic and related to the development families;
it is not an independent external benchmark. Complete historical model revisions,
server flags, package versions, and GPU records were not saved with every run.
Future replication should capture these and counterbalance recipient addresses
across templates before querying the models.
