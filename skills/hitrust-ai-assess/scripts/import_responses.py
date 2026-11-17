#!/usr/bin/env python3
"""Import answers from the HITRUST AI questionnaire into the workbook.

    python3 import_responses.py A.json <answers folder or .json> [--dry-run] [--only LM-01,AX-03]

answers may be a folder saved from the page database (responses/<id>.json and scope/system.json),
the page's "Copy all answers as JSON" export ({"format": "hitrust-ai-questionnaire/1", ...}), a list of
{"path"|"id", "data"} documents, or a single document.

The form is the source of truth for every requirement document it holds: element results, policy and
procedure coverage, evidence, notes, methods, maturity ratings and narrative fields replace the
workbook's. Requirements without a document are untouched. The scope document updates tailoring,
level and system fields.

Prints what changed, review flags, and the provisional AI score.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hitrust_lib import (MODEL_TYPES, RATING_ABBR, RESULTS, load_assessment, normalize_req, reqs_by_id,  # noqa: E402
                         requirement_eval, save_assessment, score, sort_key, element_applicable)

REQ_TEXT = ("interviewees", "implementation", "planned_implementation", "na_justification", "responsible", "provider",
            "notes", "measured", "managed")
SCALAR_SCOPE = ("description", "deployment", "boundary", "ai_platforms", "data_sources", "diagram_reference", "inventory_reference")
PEOPLE = ("system_owner", "ai_governance_lead", "security_officer")
TAIL_KEYS = ("q2", "q3", "rag", "finetune", "tools", "external_models", "model_builder")
DEFINED_RE = re.compile(r"\b(polic|defined|documented|register|inventory|catalog|card|agreement|plan|playbook|roles)\w*", re.I)


def collect(raw):
    responses, scope = {}, None

    def take(path, body):
        nonlocal scope
        if not isinstance(body, dict):
            return
        path = (path or "").strip("/")
        if path.endswith("scope/system") or path == "system" or (not path and "tailoring" in body and "elements" not in body):
            scope = body
            return
        try:
            rid = normalize_req(body.get("req") or path.split("/")[-1])
        except ValueError:
            return
        responses[rid] = body

    if isinstance(raw, dict) and isinstance(raw.get("responses"), dict):
        for rid, body in raw["responses"].items():
            take("responses/" + rid, body)
        if isinstance(raw.get("scope"), dict):
            scope = raw["scope"]
        return responses, scope
    items = raw
    if isinstance(raw, dict):
        for k in ("documents", "docs", "items", "results", "data"):
            if isinstance(raw.get(k), list):
                items = raw[k]
                break
        else:
            if "elements" in raw or "tailoring" in raw:
                take(raw.get("path", ""), raw.get("data", raw))
                return responses, scope
            items = [{"path": k, "data": v} for k, v in raw.items()]
    for it in items if isinstance(items, list) else []:
        if not isinstance(it, dict):
            continue
        body = it.get("data") if isinstance(it.get("data"), dict) else it
        path = it.get("path") or it.get("name") or (("responses/" + it["id"]) if it.get("id") and "elements" in body else it.get("id", ""))
        take(path, body)
    return responses, scope


def tri(v):
    return v if v in (True, False) else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("assessment")
    ap.add_argument("answers")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only")
    a = ap.parse_args()

    data = load_assessment(a.assessment)
    reqs, cat = data["requirements"], reqs_by_id()
    if os.path.isdir(a.answers):
        items = []
        for coll in ("responses", "scope"):
            d = os.path.join(a.answers, coll)
            for name in sorted(os.listdir(d)) if os.path.isdir(d) else []:
                if name.endswith(".json"):
                    with open(os.path.join(d, name), encoding="utf-8") as f:
                        items.append({"path": f"{coll}/{name[:-5]}", "data": json.load(f)})
        responses, scope = collect(items)
    else:
        with open(a.answers, encoding="utf-8") as f:
            responses, scope = collect(json.load(f))
    if a.only:
        keep = {normalize_req(x) for x in a.only.split(",") if x.strip()}
        responses = {k: v for k, v in responses.items() if k in keep}
    if not responses and scope is None:
        print("No questionnaire answers found.", file=sys.stderr)
        sys.exit(1)

    # Scope first: tailoring changes what is in scope for every requirement.
    scope_changed = []
    if scope is not None:
        meta, sysm = data["meta"], data.setdefault("system", {})
        if scope.get("level") in ("ai1", "ai2") and meta.get("level") != scope["level"]:
            scope_changed.append("level")
            meta["level"] = scope["level"]
            meta["base_assessment"] = "r2" if scope["level"] == "ai2" else "e1/i1"
        if "measured_managed" in scope:
            mm = bool(scope["measured_managed"]) and meta.get("level") == "ai2"
            if bool(meta.get("measured_managed")) != mm:
                scope_changed.append("measured_managed")
            meta["measured_managed"] = mm
        if isinstance(scope.get("tailoring"), dict):
            t, src = data.setdefault("tailoring", {}), scope["tailoring"]
            if isinstance(src.get("model_types"), list):
                mt = [m for m in src["model_types"] if m in MODEL_TYPES]
                if mt != t.get("model_types"):
                    scope_changed.append("tailoring.model_types")
                t["model_types"] = mt
            for k in TAIL_KEYS:
                if k in src and tri(src[k]) != t.get(k):
                    scope_changed.append("tailoring." + k)
                    t[k] = tri(src[k])
        for k in SCALAR_SCOPE:
            if k in scope:
                v = str(scope[k] or "").strip()
                if sysm.get(k, "") != v:
                    scope_changed.append(k)
                sysm[k] = v
        users = sysm.setdefault("users", {})
        for k in ("end_users", "privileged_users"):
            if k in scope:
                v = str(scope[k] or "").strip()
                if str(users.get(k, "")) != v:
                    scope_changed.append("users." + k)
                users[k] = v
        for p in PEOPLE:
            if isinstance(scope.get(p), dict):
                dst = sysm.setdefault(p, {})
                for k in ("name", "title", "email"):
                    if k in scope[p]:
                        v = str(scope[p][k] or "").strip()
                        if dst.get(k, "") != v:
                            scope_changed.append(f"{p}.{k}")
                        dst[k] = v
        for lst, keys in (("models", ("name", "version", "type", "source", "provider", "owner")),
                          ("providers", ("name", "service", "role", "hitrust", "srm"))):
            if isinstance(scope.get(lst), list):
                new = [{k: str(x.get(k, "") or "").strip() for k in keys} for x in scope[lst]
                       if isinstance(x, dict) and str(x.get("name", "")).strip()]
                if new != sysm.get(lst, []):
                    scope_changed.append(lst)
                sysm[lst] = new

    meta, tail = data["meta"], data.get("tailoring", {})
    level, mm = meta.get("level", "ai2"), meta.get("measured_managed", False)
    before = {rid: requirement_eval(cat[rid], reqs[rid], tail, level, mm) for rid in reqs}
    changes, flags, skipped = [], [], []
    for rid in sorted(responses, key=sort_key):
        if rid not in reqs:
            skipped.append(rid)
            continue
        doc, r, c = responses[rid], reqs[rid], cat[rid]
        n_el = n_rq = 0
        for eid, e in (doc.get("elements") or {}).items():
            if eid not in r["elements"] or not isinstance(e, dict):
                continue
            res = str(e.get("result", "NOT ASSESSED")).upper().strip()
            if res not in RESULTS:
                flags.append(f"{eid}: unknown result '{e.get('result')}' ignored")
                continue
            dst = r["elements"][eid]
            new = {"result": res, "policy": bool(e.get("policy")), "procedure": bool(e.get("procedure")),
                   "evidence": (e.get("evidence") or "").strip(), "notes": (e.get("notes") or "").strip()}
            methods = [m for m in (e.get("methods") or []) if m in ("Examine", "Interview", "Test")]
            touched = any(dst.get(k) != v for k, v in new.items()) or dst.get("methods", []) != methods
            dst.update(new)
            if methods:
                dst["methods"] = methods
            else:
                dst.pop("methods", None)
            n_el += touched
        for k in REQ_TEXT:
            if k in doc and doc[k] is not None:
                v = str(doc[k]).strip() or ("Customer" if k == "provider" else "")
                n_rq += r.get(k, "") != v
                r[k] = v
        if "evidence" in doc:
            ev = doc["evidence"]
            lst = [x.strip() for x in (ev if isinstance(ev, list) else re.split(r"[;\n]", ev or "")) if x and x.strip()]
            n_rq += lst != r.get("evidence", [])
            r["evidence"] = lst
        if isinstance(doc.get("maturity"), dict):
            mat = r.setdefault("maturity", {})
            for k, v in doc["maturity"].items():
                if k in ("policy", "procedure", "implemented", "measured", "managed"):
                    try:
                        v = int(v) if v not in (None, "") else None
                    except (TypeError, ValueError):
                        v = None
                    if v is not None and v not in RATING_ABBR:
                        flags.append(f"{rid}: {k} rating {v} is not 0/25/50/75/100, ignored")
                        v = None
                    n_rq += mat.get(k) != v
                    mat[k] = v
        if "scope_override" in doc:
            v = doc["scope_override"] if doc["scope_override"] in ("in", "out") else None
            n_rq += r.get("scope_override") != v
            r["scope_override"] = v
        after = requirement_eval(c, r, tail, level, mm)
        if n_el or n_rq:
            b = before[rid]
            fmt = lambda x: f"{x['status']}" + (f" {x['score']}" if x.get("score") is not None else "")  # noqa: E731
            changes.append(f"{rid:<6} {fmt(b):>18} -> {fmt(after):<18} ({n_el} element(s), {n_rq} field(s))")

        if not after["in_scope"] or after["status"] == "N/A":
            continue
        for el in c["elements"]:
            x = r["elements"][el["id"]]
            if x["result"] == "MET" and not x.get("evidence"):
                flags.append(f"{el['id']}: MET with no evidence" + (" (needs a written artifact)" if DEFINED_RE.search(el["text"]) else ""))
            if x["result"] == "MET" and x.get("methods") and len(x["methods"]) < 2:
                flags.append(f"{el['id']}: MET on one method only ({x['methods'][0]}); external assessors expect corroboration")
            if x["result"] == "NOT MET" and not x.get("notes"):
                flags.append(f"{el['id']}: NOT MET with no gap described")
            if x["result"] == "N/A" and not (x.get("notes") or r.get("na_justification")):
                flags.append(f"{el['id']}: N/A with no justification")
            if x["result"] == "N/A" and element_applicable(el, tail) and not el.get("cond"):
                flags.append(f"{el['id']}: marked N/A but HITRUST does not make this element conditional; confirm")
            if x["result"] == "MET" and not x.get("policy") and level == "ai2":
                flags.append(f"{el['id']}: implemented but not addressed in policy (costs Policy maturity)")
        prov = r.get("provider", "")
        if prov.startswith("Inherited") and c["inheritance"] == "No":
            flags.append(f"{rid}: marked Inherited but HITRUST says this requirement is not inheritable (dual or sole responsibility)")
        for f in after.get("flags", []):
            flags.append(f"{rid}: {f}")
        if after.get("score") is not None:
            for k, src in after["source"].items():
                if src == "suggested" and k in ("policy", "procedure"):
                    flags.append(f"{rid}: {k} rating is the coverage suggestion ({after['final'][k]}); confirm against the policy/procedure strength")
                    break
            if after.get("cap_candidate") and not r.get("planned_implementation"):
                flags.append(f"{rid}: CAP candidate (score {after['score']}) with no planned fix")
        if mm and level == "ai2" and after.get("final", {}).get("measured") and not r.get("measured"):
            flags.append(f"{rid}: Measured rated with no metric described")
        if after["status"] == "FULLY MET" and not r.get("implementation"):
            flags.append(f"{rid}: fully met with no implementation statement")

    print(f"Questionnaire import {'(dry run) ' if a.dry_run else ''}into {os.path.basename(a.assessment)}")
    print(f"  Requirement documents read: {len(responses)}" + (f" (unknown ids skipped: {', '.join(skipped)})" if skipped else ""))
    if scope is not None:
        print(f"  Scope/tailoring fields changed: {', '.join(scope_changed) if scope_changed else 'none'}")
    print(f"  Requirements changed: {len(changes)}")
    for line in changes:
        print("    " + line)
    if flags:
        print(f"\nReview flags ({len(flags)}):")
        for f in flags:
            print("  - " + f)
    s = score(data)
    print(f"\n{s['level']} provisional average: {s['average'] if s['average'] is not None else 'n/a'} (threshold {s['threshold']}). {s['verdict']}")
    if s["cap_candidates"]:
        print("CAP candidates: " + ", ".join(f"{x['id']} ({x['score']})" for x in s["cap_candidates"]))
    if not a.dry_run:
        save_assessment(a.assessment, data)
        print("Saved.")


if __name__ == "__main__":
    main()
