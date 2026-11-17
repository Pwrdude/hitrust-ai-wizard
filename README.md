# HITRUST AI Wizard v0.1

A readiness assistant for the HITRUST AI Security Assessment: **ai2** (added to an r2) and **ai1** (added to an e1 or i1). It uses the same method as the CMMC Wizard: one JSON workbook per engagement, a private questionnaire page you fill in during interviews, "sync" to import and review, and a running score.

## Skill

| Skill | Use it to | Say something like |
|---|---|---|
| **hitrust-ai-assess** | Set tailoring, build the questionnaire for the AI requirements that apply, fill it in, then import and review the answers with PRISMA scoring, the certification threshold and CAP candidates | "Start a HITRUST ai2 assessment for Gulf Coast Clinic", "Sync the AI answers", "Where are we on the clinic's AI assessment?", "Score it" |

## How it maps to the CMMC Wizard

| CMMC Wizard | HITRUST AI Wizard |
|---|---|
| 110 requirements, 320 SP 800-171A objectives | Up to 44 AI requirements, 190 evaluative elements |
| Scope & boundary | Scope & tailoring: the three MyCSF "Security for AI Systems" questions, system characteristics (RAG, fine-tuning, agents/plugins, external models, model builder), models and AI service providers |
| Objective result: MET / NOT MET / N/A | Element result (Implemented) plus "in policy" and "in procedure" ticks |
| SPRS: 110 minus 5/3/1 deductions | PRISMA: Policy 15, Procedure 20, Implemented 40, optional Measured 10 / Managed 15; average >= 62 (ai2) or >= 83 (ai1) |
| POA&M eligibility and blockers | CAP candidates (below 71 with Implemented below Fully compliant) and gaps |
| Customer / Shared / Inherited (CSP) | Customer / Shared / Inherited (AI provider), with HITRUST's inheritability per requirement enforced |
| Risk-first view | Weakest-first view |
| 14 families | 12 AI security topics |

## The questionnaire
- Scope & tailoring comes first: the answers decide which requirements appear, and elements that only apply to RAG, fine-tuning, agents/plugins or external models drop to N/A automatically.
- Each requirement card shows the HITRUST requirement ID, CSF domain and control reference, inheritability, the statement, and every evaluative element with Implemented result, policy and procedure ticks, evidence, notes and methods.
- A maturity strip per requirement suggests Policy, Procedure and Implemented ratings from element coverage (HITRUST rubric bands); you override after judging strength. Measured and Managed appear when you choose to score them.
- The header keeps the provisional AI average against the threshold, requirements rated, elements done and CAP candidates.
- Answers save as you type to the page's own database, readable and writable only by you and editors you add. Do not type PHI, PII or model secrets into it.

## Scoring caveats
- Readiness estimate only. MyCSF scoring and HITRUST QA decide certification and CAPs.
- The ai1/ai2 certificate also requires the underlying e1/i1/r2 to certify. This tool scores only the AI requirements.
- HITRUST's per-requirement tailoring text and its summary count table disagree for some generative and predictive combinations. The tool follows the per-requirement text; set a requirement's Scope to match the client's MyCSF object where they differ.

## Requirements
- Python 3.9+, standard library only.
- The questionnaire page needs Claude artifacts with the page database capability.

## Data
See `skills/hitrust-ai-assess/references/SOURCES.md`. Re-verify requirement text and tailoring against the current HITRUST specification and the client's MyCSF object before a validated assessment.

## License
MIT. See `LICENSE`. HITRUST and HITRUST CSF are trademarks of HITRUST Services Corp.; this project is independent and not endorsed by HITRUST. Requirement text is paraphrased from HITRUST's public AI Security Assessment specification.
