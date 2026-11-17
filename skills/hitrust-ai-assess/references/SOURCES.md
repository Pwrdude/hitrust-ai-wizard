# Data sources and provenance (`requirements.json`)

| Field | Source |
|---|---|
| `id` (TM-01...) | This tool's short IDs, grouped by HITRUST's AI security topics |
| `hitrust_id`, `domain`, `control_ref` | HITRUST AI Security Assessment and Certification Specification (hitrustalliance.net/help/ai-sec-assessment), per-requirement "where it sits in the HITRUST CSF" |
| `statement`, `elements` | Same specification: requirement statements and evaluative elements, paraphrased |
| `inheritance` | Same specification, "can this requirement be inherited" per requirement. DV-01 (training) was not confirmed and is set to No |
| `applies` (models, trigger, requires) | Same specification, per-requirement tailoring notes. See `scoring-rules.md` for the count discrepancy with HITRUST's summary table |
| Scoring weights and bands | HITRUST PRISMA weights (HAA 2019-007; Assessment Handbook); rubric coverage bands |
| ai1/ai2 thresholds, domains, Measured/Managed optional | HITRUST AI Security Assessment FAQs (2024) and the specification |
| `threats.md` | Specification's threat list and cited references (OWASP, MITRE ATLAS, NIST AI 100-2 / 600-1) |

Built November 2026 against CSF v11.4+ content. HITRUST updates the AI requirements with CSF releases; re-verify requirement text, IDs and tailoring against the current specification and the client's MyCSF object before a validated assessment.
