#!/usr/bin/env python3
"""Score a HITRUST AI security assessment workbook.

  python3 score.py A.json              # readable summary
  python3 score.py A.json --json       # machine-readable
  python3 score.py A.json --md out.md  # also write a Markdown readiness report

ai2: requirement score = Policy 15% + Procedure 20% + Implemented 40% (+ Measured 10% + Managed 15% when scored);
     certification threshold: average of in-scope AI requirement scores >= 62 (and the r2 itself must certify).
ai1: requirement score = Implemented rating; threshold 83.
CAP candidates: requirement score below 71 (ai2) / 83 (ai1) and Implemented below Fully compliant. HITRUST's
final CAP call also depends on the control-reference average across the whole r2 object, which this tool
cannot see; treat the list as the ones to plan for.
"""
import argparse
import json
from datetime import date

from hitrust_lib import cap_ids, fmt_level, load_assessment, score


def report_md(data, s):
    ids = cap_ids(data)
    t = data.get("tailoring", {})
    yn = lambda v: "Yes" if v else "No" if v is False else "Not answered"  # noqa: E731
    lines = [f"# HITRUST AI security readiness ({s['level']}): {data['client']['name']}", "",
             f"AI system: {data['system']['name']}  ",
             f"Assessment type: {data['meta'].get('assessment_type', '')}  ",
             f"Assessor: {data['meta'].get('assessor', '')}  ",
             f"Calculated: {date.today().isoformat()}", "",
             "## Tailoring", "",
             f"- AI model types: {', '.join(t.get('model_types') or []) or 'Not answered'}",
             f"- Q2 sensitive data used to train/tune/RAG: {yn(t.get('q2'))}",
             f"- Q3 confidential model architecture: {yn(t.get('q3'))}",
             f"- RAG: {yn(t.get('rag'))} · Fine-tuning: {yn(t.get('finetune'))} · Agents/plugins: {yn(t.get('tools'))} · "
             f"External models: {yn(t.get('external_models'))} · Builds models: {yn(t.get('model_builder'))}", "",
             "## Result", "",
             f"**Average AI requirement score: {s['average'] if s['average'] is not None else 'n/a'}** "
             f"(threshold {s['threshold']}; Measured/Managed {'scored' if s['measured_managed'] else 'not scored, so 75 is the per-requirement ceiling'})", "",
             s["verdict"], "",
             "| | Count |", "|---|---|",
             f"| In scope | {s['in_scope']} |", f"| Scored | {s['scored']} |", f"| Still open | {s['pending']} |",
             f"| N/A | {s['na']} |", f"| Out of scope by tailoring | {s['out_of_scope']} |",
             f"| CAP candidates | {len(s['cap_candidates'])} |", f"| Gaps (not CAP) | {len(s['gaps'])} |", ""]
    if s["domain_averages"]:
        lines += ["## Average by HITRUST domain", "", "| Domain | Average |", "|---|---|"]
        lines += [f"| {d} | {v} |" for d, v in s["domain_averages"].items()]
        lines.append("")
    lines += ["## Requirements", "", "| ID | Requirement | Status | Pol | Proc | Impl | Meas | Mgd | Score |", "|---|---|---|---|---|---|---|---|---|"]
    for x in s["rows"]:
        if not x["in_scope"]:
            continue
        f = x.get("final", {})
        lines.append(f"| {x['id']} | {x['title']} | {x['status']} | " + " | ".join(fmt_level(f.get(k)) if k in f else "" for k in
                     ("policy", "procedure", "implemented", "measured", "managed")) + f" | {x['score'] if x.get('score') is not None else ''} |")
    lines.append("")
    if s["cap_candidates"]:
        lines += ["## CAP candidates", "", "| CAP | Requirement | Score | Elements not met | Planned fix |", "|---|---|---|---|---|"]
        for x in s["cap_candidates"]:
            plan = data["requirements"][x["id"]].get("planned_implementation", "").replace("|", "/").replace("\n", " ")
            lines.append(f"| {ids[x['id']]} | {x['id']} {x['title']} | {x['score']} | {', '.join(x.get('not_met', []))} | {plan} |")
        lines.append("")
    if s["gaps"]:
        lines += ["## Gaps (below full marks, no CAP expected)", ""]
        lines += [f"- {x['id']} {x['title']}: {x['score']}" for x in s["gaps"]]
        lines.append("")
    out = [x for x in s["rows"] if not x["in_scope"]]
    if out:
        lines += ["## Out of scope under this tailoring", ""] + [f"- {x['id']} {x['title']}: {x['scope_reason']}" for x in out] + [""]
    lines += ["_Readiness estimate only. HITRUST scores in MyCSF and its QA decides certification and CAPs._", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--md")
    a = ap.parse_args()
    data = load_assessment(a.file)
    s = score(data)
    if a.json:
        print(json.dumps({k: v for k, v in s.items() if k != "rows"}, indent=2, default=str))
    else:
        print(f"{s['level']} average: {s['average'] if s['average'] is not None else 'n/a'} (threshold {s['threshold']})")
        print(f"In scope {s['in_scope']} · scored {s['scored']} · open {s['pending']} · N/A {s['na']} · out of scope {s['out_of_scope']}")
        print(s["verdict"])
        if s["cap_candidates"]:
            print("\nCAP candidates:")
            for x in s["cap_candidates"]:
                print(f"  {x['id']:<7} {x['score']:>6}  {x['title']}  [{', '.join(x.get('not_met', []))}]")
        if s["gaps"]:
            print("\nGaps: " + ", ".join(f"{x['id']} ({x['score']})" for x in s["gaps"]))
    if a.md:
        with open(a.md, "w", encoding="utf-8") as f:
            f.write(report_md(data, s))
        print(f"\nWrote {a.md}")


if __name__ == "__main__":
    main()
