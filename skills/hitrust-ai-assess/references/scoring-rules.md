# Scoring and certification rules

## Requirement score
| Level | ai2 weight | ai1 |
|---|---|---|
| Policy | 15 | not scored |
| Procedure | 20 | not scored |
| Implemented | 40 | 100% of the score |
| Measured (optional) | 10 | not scored |
| Managed (optional) | 15 | not scored |

Each level is rated Non-compliant 0, Somewhat 25, Partially 50, Mostly 75 or Fully compliant 100 (percent of that level's weight).
ai2 requirement score = sum of weight x rating. Without Measured and Managed, the ceiling is 75.

## Rubric coverage bands used for suggestions
Under 11% NC · 11-32% SC · 33-65% PC · 66-89% MC · 90-100% FC. Coverage = share of applicable evaluative elements addressed (policy, procedure) or met (implemented). HITRUST's rubric also weighs strength for Policy and Procedure and scope coverage for Implemented; the assessor rates those.

## Certification
- **ai2**: the underlying r2 must certify (every domain straight-average >= 62, AI requirements included in their domains), and the average of all AI requirement scores must be >= 62.
- **ai1**: the underlying e1/i1 must certify, and the AI average must be >= 83.
- Validity follows the base: ai1 one year, ai2 two years with the interim assessment by the one-year mark.
- N/A requirements are left out of the average.

## CAPs and gaps (estimates)
- r2 rule (HITRUST Assessment Handbook): a CAP is required where a requirement scores below 71, its Implemented level is below Fully compliant, and the control reference it belongs to averages below 71. The tool flags **CAP candidates** on the first two conditions; the control-reference average includes non-AI requirements in the r2 object, which this tool cannot see.
- ai1: the tool flags requirements below 83 as CAP candidates (Implemented below Mostly/Fully).
- Gaps: below full marks for the levels being scored but not a CAP candidate. Report them; no CAP is expected.

## Tailoring counts: known discrepancy
HITRUST publishes a count table (rule-based 27; predictive 36 / 38 / 40; generative 41 / 44 / 43 / 44). The per-requirement tailoring text in the same specification gives: rule-based 27; predictive 36, 39 with Q2 or Q3, 40 with both; generative 39, 42, 42, 43. Rule-based, predictive base and predictive with both flags agree; the others do not. The tool follows the per-requirement text. **MyCSF is authoritative**: compare the requirement count in the client's MyCSF object and use the scope override on any requirement that differs.
