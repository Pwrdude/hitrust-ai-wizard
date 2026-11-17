#!/usr/bin/env python3
"""Build the web questionnaire page for a HITRUST AI engagement, plus seed data for its database.

    python3 build_questionnaire.py A.json --out "<client>-ai2-questionnaire.html"

Writes:
  <out>             the self-contained page to publish as an Artifact (declare the db capability)
  <out stem>-seed/  one JSON file per document for the page's database: scope/system.json (tailoring,
                    level and scope) and responses/<req id>.json for requirements with anything recorded.

The page stores one document per requirement at responses/<req id> (e.g. responses/LM-01) and the
tailoring and scope at scope/system. import_responses.py reads those back into the workbook.
"""
import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hitrust_lib import load_assessment, load_data, sort_key, THRESHOLD, CAP_LINE, WEIGHTS  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "assets", "questionnaire-template.html")

SCALAR_SCOPE = ("description", "deployment", "boundary", "ai_platforms", "data_sources", "diagram_reference", "inventory_reference")
PEOPLE = ("system_owner", "ai_governance_lead", "security_officer")
REQ_TEXT = ("interviewees", "implementation", "planned_implementation", "na_justification", "responsible", "notes", "measured", "managed")


def engagement_id(a):
    key = "|".join([a.get("client", {}).get("name", ""), a.get("system", {}).get("name", ""), a.get("meta", {}).get("started", "")])
    return hashlib.sha1(key.encode()).hexdigest()[:12]


def req_doc(rid, r):
    els, any_el = {}, False
    for eid, e in r["elements"].items():
        els[eid] = {"result": e.get("result", "NOT ASSESSED"), "policy": bool(e.get("policy")), "procedure": bool(e.get("procedure")),
                    "evidence": e.get("evidence", ""), "notes": e.get("notes", ""), "methods": e.get("methods", [])}
        if els[eid]["result"] != "NOT ASSESSED" or els[eid]["policy"] or els[eid]["procedure"] or e.get("evidence") or e.get("notes"):
            any_el = True
    ev = r.get("evidence", [])
    doc = {"req": rid, "elements": els, "maturity": dict(r.get("maturity") or {}), "scope_override": r.get("scope_override"),
           "provider": r.get("provider", "") or "Customer", "evidence": "; ".join(ev) if isinstance(ev, list) else (ev or "")}
    for k in REQ_TEXT:
        doc[k] = r.get(k, "")
    has = any(doc[k] for k in REQ_TEXT) or doc["evidence"] or doc["provider"] != "Customer" or doc["scope_override"] \
        or any(v is not None for v in doc["maturity"].values())
    return doc if (any_el or has) else None


def scope_doc(data):
    sysm, meta = data.get("system", {}), data.get("meta", {})
    s = {k: sysm.get(k, "") or "" for k in SCALAR_SCOPE}
    users = sysm.get("users", {}) or {}
    s["end_users"] = str(users.get("end_users", "") or "")
    s["privileged_users"] = str(users.get("privileged_users", "") or "")
    for p in PEOPLE:
        src = sysm.get(p, {}) or {}
        s[p] = {"name": src.get("name", ""), "title": src.get("title", ""), "email": src.get("email", "")}
    s["models"] = [{k: str(m.get(k, "") or "") for k in ("name", "version", "type", "source", "provider", "owner")}
                   for m in sysm.get("models", []) if isinstance(m, dict)]
    s["providers"] = [{k: str(p.get(k, "") or "") for k in ("name", "service", "role", "hitrust", "srm")}
                      for p in sysm.get("providers", []) if isinstance(p, dict)]
    s["level"] = meta.get("level", "ai2")
    s["measured_managed"] = bool(meta.get("measured_managed"))
    s["tailoring"] = dict(data.get("tailoring", {}))
    return s


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("assessment")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    data = load_assessment(a.assessment)
    meta, cat = data.get("meta", {}), load_data()
    client = (data.get("client", {}) or {}).get("name", "")
    eid = engagement_id(data)
    reqs = sorted(cat["requirements"], key=lambda r: sort_key(r["id"]))
    payload = {
        "meta": {"client": client, "system": data.get("system", {}).get("name", ""), "assessor": meta.get("assessor", ""),
                 "assessment_type": meta.get("assessment_type", ""), "engagement_id": eid, "workbook": os.path.basename(a.assessment)},
        "topics": cat["topics"], "cond_text": cat["cond_text"], "requires_text": cat["requires_text"],
        "threshold": THRESHOLD, "cap_line": CAP_LINE, "weights": WEIGHTS,
        "requirements": [{k: r[k] for k in ("id", "hitrust_id", "topic_code", "topic", "title", "domain", "control_ref", "inheritance",
                                           "applies", "applies_text", "statement", "note", "elements")} for r in reqs],
    }
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    with open(TEMPLATE, encoding="utf-8") as f:
        html = f.read()
    title = f"{client} HITRUST AI Questionnaire" if client else "HITRUST AI Questionnaire"
    html = html.replace("__PAGE_TITLE__", title.replace("<", "&lt;")).replace("__AI_DATA__", blob)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(html)

    seed = [("scope", "system", scope_doc(data))]
    for r in reqs:
        d = req_doc(r["id"], data["requirements"][r["id"]])
        if d:
            seed.append(("responses", r["id"], d))
    seed_dir = os.path.splitext(a.out)[0] + "-seed"
    for coll, doc_id, body in seed:
        os.makedirs(os.path.join(seed_dir, coll), exist_ok=True)
        with open(os.path.join(seed_dir, coll, doc_id + ".json"), "w", encoding="utf-8") as f:
            json.dump(body, f, indent=1, ensure_ascii=False)

    print(f"Page: {a.out} ({os.path.getsize(a.out) // 1024} KB), title '{title}', engagement {eid}")
    print(f"Seed: {seed_dir}/ ({len(seed)} documents: scope/system + {len(seed) - 1} responses/<req id>)")
    print("Publish with capabilities {\"db\": {\"rules\": [{\"path\": \"\", \"read\": \"admin\", \"write\": \"admin\"}]}},")
    print("then write each seed file into the page database (collection = folder name, doc id = file name).")


if __name__ == "__main__":
    main()
