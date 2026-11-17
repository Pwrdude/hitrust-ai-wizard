#!/usr/bin/env python3
"""Create a HITRUST AI security assessment workbook (JSON) with all 44 AI requirements and their
evaluative elements. Tailoring decides which are in scope; set it now or later in the questionnaire.

Usage:
  python3 init_assessment.py --client "Acme Health AI" --system "Acme Triage Assistant" \
      --assessor "T. Williams" --out acme-ai2-assessment.json \
      [--level ai2|ai1] [--type "Readiness"] [--measured-managed] \
      [--models generative,predictive] [--q2 yes|no] [--q3 yes|no] \
      [--rag yes|no] [--finetune yes|no] [--tools yes|no] [--external-models yes|no] [--model-builder yes|no]
"""
import argparse
import os
from datetime import date

from hitrust_lib import MODEL_TYPES, die, in_scope, requirements, save_assessment


def yn(v):
    if v is None:
        return None
    v = v.strip().lower()
    if v in ("y", "yes", "true", "1"):
        return True
    if v in ("n", "no", "false", "0"):
        return False
    die(f"expected yes or no, got {v}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--client", required=True)
    ap.add_argument("--system", required=True, help="AI system / platform name")
    ap.add_argument("--assessor", default="")
    ap.add_argument("--type", default="Readiness (pre-assessment)",
                    help="e.g. Readiness (pre-assessment), Mock validated, Gap remediation check")
    ap.add_argument("--level", default="ai2", choices=("ai2", "ai1"))
    ap.add_argument("--measured-managed", action="store_true", help="score Measured and Managed (ai2 only)")
    ap.add_argument("--models", default="", help="comma list of rule, predictive, generative")
    for k in ("q2", "q3", "rag", "finetune", "tools", "external-models", "model-builder"):
        ap.add_argument("--" + k)
    ap.add_argument("--out", required=True)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if os.path.exists(a.out) and not a.force:
        die(f"{a.out} exists; pass --force to overwrite")
    models = [m.strip().lower() for m in a.models.split(",") if m.strip()]
    bad = [m for m in models if m not in MODEL_TYPES]
    if bad:
        die(f"unknown model type(s) {bad}; use {MODEL_TYPES}")

    tailoring = {"model_types": models, "q2": yn(a.q2), "q3": yn(a.q3), "rag": yn(a.rag), "finetune": yn(a.finetune),
                 "tools": yn(getattr(a, "tools")), "external_models": yn(a.external_models), "model_builder": yn(a.model_builder)}
    reqs = {}
    for r in requirements():
        reqs[r["id"]] = {
            "scope_override": None,        # None | "in" | "out" (match the MyCSF object if it differs)
            "implementation": "",          # how the requirement is met (narrative)
            "planned_implementation": "",  # corrective action for CAP / gap
            "na_justification": "",
            "responsible": "", "provider": "Customer",  # Customer | Shared (X) | Inherited (X)
            "interviewees": "", "evidence": [], "notes": "",
            "measured": "", "managed": "",  # descriptions of the metric / the management response
            "maturity": {k: None for k in ("policy", "procedure", "implemented", "measured", "managed")},
            "cap": {"weakness": "", "remediation": "", "milestones": [], "poc": "", "resources": "",
                    "scheduled_completion": "", "status": "Open", "comments": ""},
            "elements": {e["id"]: {"result": "NOT ASSESSED", "policy": False, "procedure": False,
                                   "evidence": "", "notes": ""} for e in r["elements"]},
        }
    data = {
        "meta": {"schema": "hitrust-ai-wizard/1", "framework": "HITRUST AI Security Assessment (CSF v11.4+)",
                 "level": a.level, "base_assessment": "r2" if a.level == "ai2" else "e1/i1",
                 "measured_managed": bool(a.measured_managed and a.level == "ai2"),
                 "assessment_type": a.type, "assessor": a.assessor, "started": date.today().isoformat(),
                 "assessment_date": ""},
        "client": {"name": a.client, "address": ""},
        "tailoring": tailoring,
        "system": {
            "name": a.system, "description": "", "deployment": "", "boundary": "",
            "ai_platforms": "", "data_sources": "", "users": {"end_users": "", "privileged_users": ""},
            "models": [], "providers": [],
            "system_owner": {"name": "", "title": "", "email": ""},
            "ai_governance_lead": {"name": "", "title": "", "email": ""},
            "security_officer": {"name": "", "title": "", "email": ""},
            "diagram_reference": "", "inventory_reference": "",
        },
        "record_of_changes": [],
        "requirements": reqs,
    }
    save_assessment(a.out, data)
    n_in = sum(1 for r in requirements() if in_scope(r, tailoring)[0])
    print(f"Created {a.out}: 44 AI requirements, {sum(len(r['elements']) for r in requirements())} evaluative elements; "
          f"{n_in} in scope under current tailoring" + ("" if models else " (model types not set yet)"))


if __name__ == "__main__":
    main()
