# Assessment method: judging AI requirements

## Methods
- **Examine**: AI policies and standards, procedures and runbooks, the AI system inventory, threat register and threat model, red-team and pen-test reports, model cards, data inventories and source catalogs, change tickets and release notes, log schemas and sample log lines, guardrail and filter configuration, provider agreements, SRMs and HITRUST letters, training records, backup job reports.
- **Interview**: the people who do the work: ML/data science lead, application owner, platform engineer, SecOps analyst, AI governance lead, procurement or vendor management.
- **Test**: send a prompt-injection string and watch the input filter fire; request output that should be redacted; exceed the rate limit; try to reach the model endpoint without the right role; pull a log entry and check it carries user, origin and model version; restore a model or metaprompt from backup.

External assessors expect corroboration: examine plus interview or test. "We do that" with no artifact is not met.

## Evaluative elements
Each requirement is split into evaluative elements. Rate every element for **Implemented** (MET / NOT MET / N/A) and tick whether the organization's **policy** and **procedure** address it.
- Elements tagged "if RAG", "if fine-tuning", "if agents/plugins" or "if external models" are N/A automatically when the tailoring panel says the system does not do that. Recording a result overrides that.
- Frequency elements ("at least semiannually", "at least monthly", "before deployment") need dated proof of the last two cycles, not a calendar reminder.
- "Before deployment" elements need evidence tied to an actual deployment (ticket, approval, release record).

## PRISMA maturity levels (ai2)
- **Policy** (15%): a management-approved, mandatory statement covering the element. Judge coverage (share of elements addressed) and strength (is it a "must", is the scope and frequency stated, is it current and approved). An AI acceptable-use page is not a security administration policy.
- **Procedure** (20%): the how: who does it, steps, frequency, tools, records produced. A wiki page with no owner or date is weak.
- **Implemented** (40%): operating across the in-scope AI platforms and models. Coverage across platforms matters: logging on the chat app but not on the batch API is partial.
- **Measured** (10%, optional): a metric or independent check that the control operates (e.g. monthly count of blocked prompt injections reviewed by SecOps).
- **Managed** (15%, optional): documented corrective action when the metric shows a problem. Cannot be rated above Measured.

The tool suggests Policy, Procedure and Implemented ratings from element coverage using the HITRUST rubric bands (under 11% NC, 11-32 SC, 33-65 PC, 66-89 MC, 90-100 FC). Override after judging strength; the coverage number alone does not decide it.

## Inheritance and shared responsibility
- HITRUST marks each AI requirement as fully inheritable, partially inheritable, or not inheritable. Not-inheritable ones are either the AI application provider's sole job or a dual responsibility that each party performs independently (threat identification, policies, inventory, legal review, incident response).
- Inherit only from a provider with a current HITRUST certification that includes the AI requirements, through MyCSF inheritance, and check the provider's shared responsibility matrix. Record the provider in the requirement's Responsibility field: Customer, Shared (provider) or Inherited (provider).
- Typical splits: model encryption at rest, dataset sanitization and model access are often the platform's or model creator's; input/output filtering, rate limiting, logging and least privilege for agents are usually shared; human intervention, output specificity and the model card review are the application provider's.

## Frequent findings
- **TM-01 / TM-02**: a one-time threat model done at launch; no semiannual refresh and nothing after model upgrades.
- **TM-03**: a generic web pen test with no AI-specific testing (prompt injection, data poisoning, model inversion).
- **GV-02**: AI covered in an acceptable-use policy only; BC/DR and data governance policies silent on models, embeddings and metaprompts.
- **DV-04**: model version bumps from the provider (e.g. a hosted model alias moving) go live without change tickets or release-note review.
- **DV-08**: open-weight models and packages pulled from public hubs with no hash or signature check.
- **AX-03**: agents run with a service identity that can read every SharePoint site or database the integration touches.
- **LM-01**: prompts and outputs logged, but not the model version or request origin; logs keep PHI with no sanitization rule.
- **LM-02 / LM-03**: no monthly review; guardrails never tested after configuration changes.
- **IN-01**: the AI inventory is a slide; no owner, risk category or semiannual review.
- **RS-01**: IR plan unchanged; tabletop never included an AI scenario; AI app logs not in the SIEM.
- **RS-02**: model artifacts backed up but metaprompts, vector stores and agent code are not.

## Interview approach
Ask them to show, not describe:
- "Open the inventory entry for this model. Who owns it and when was it last reviewed?"
- "Show me the change ticket for the last model version change."
- "Send this prompt through the app and show me the log line it produced."
- "What happens if the agent tries to email a patient? Show me where a human approves it."
Record who was interviewed (role) on the requirement.
