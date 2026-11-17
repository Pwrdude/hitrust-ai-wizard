#!/usr/bin/env python3
"""Record results in a HITRUST AI workbook without hand-editing JSON.

Element results (implemented), with policy/procedure coverage:
  python3 record.py A.json elem TM-01[1] TM-01[2] MET --policy yes --procedure yes --evidence "AI Threat Register v3" --notes "..."
  python3 record.py A.json elem LM-01 "NOT MET" --notes "No model version in logs"     # every element of LM-01
  python3 record.py A.json elem AX-04[3] N/A --notes "No RAG"

Maturity ratings (0/25/50/75/100 or NC/SC/PC/MC/FC; 'auto' clears to the suggestion):
  python3 record.py A.json maturity TM-01 --policy FC --procedure MC --implemented 75 --measured auto

Requirement fields:
  python3 record.py A.json req TM-01 --implementation "..." --responsible "CISO" --provider "Inherited (Azure OpenAI)" \
      --interviewees "ML lead; SecOps" --evidence "Threat register" --planned "..." --na "" --scope in|out|auto

Tailoring (MyCSF Security for AI Systems questions plus system characteristics):
  python3 record.py A.json tailor --models generative,predictive --q2 yes --q3 no --rag yes --finetune no \
      --tools yes --external-models yes --model-builder no
  python3 record.py A.json level ai2 [--measured-managed yes|no]

CAP fields:
  python3 record.py A.json cap LM-01 --weakness "..." --remediation "..." --poc "..." --completion 2027-03-01 \
      --milestone "2027-01-15|Add model version to log schema"

System / client fields:
  python3 record.py A.json set system.description "..."
  python3 record.py A.json append system.models '{"name":"gpt-4o","version":"2024-11-20","type":"generative","source":"External","provider":"Azure OpenAI","owner":"ML lead"}'
"""
import argparse
import json
import re
import sys

from hitrust_lib import (MODEL_TYPES, RATING_ABBR, RESULTS, die, load_assessment, normalize_elem, normalize_req,
                         reqs_by_id, requirement_eval, save_assessment, fmt_level, element_applicable)

ABBR = {v: k for k, v in RATING_ABBR.items()}


def yn(v):
    if v is None:
        return None
    v = v.strip().lower()
    if v in ("y", "yes", "true", "1"):
        return True
    if v in ("n", "no", "false", "0"):
        return False
    if v in ("unknown", "?", "none", ""):
        return "unset"
    die(f"expected yes/no/unknown, got {v}")


def rating(v):
    v = v.strip().upper()
    if v in ("AUTO", "NONE", ""):
        return None
    if v in ABBR:
        return ABBR[v]
    try:
        n = int(v)
    except ValueError:
        die(f"rating must be 0/25/50/75/100 or NC/SC/PC/MC/FC, got {v}")
    if n not in RATING_ABBR:
        die("rating must be 0, 25, 50, 75 or 100")
    return n


def show(data, rid):
    m = data["meta"]
    e = requirement_eval(reqs_by_id()[rid], data["requirements"][rid], data.get("tailoring", {}), m.get("level", "ai2"), m.get("measured_managed"))
    if not e["in_scope"]:
        return f"{rid}: out of scope ({e['scope_reason']})"
    if e["status"] == "N/A":
        return f"{rid}: N/A ({e.get('na_reason')})"
    lv = " ".join(f"{k[:4]}={fmt_level(v)}" for k, v in e["final"].items())
    return f"{rid}: {e['status']}, {e['elements_met']}/{e['elements_total']} elements met; {lv}; score {e['score'] if e['score'] is not None else 'pending'}"


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    path, mode, rest = sys.argv[1], sys.argv[2], sys.argv[3:]
    data = load_assessment(path)
    reqs = data["requirements"]
    catalog = reqs_by_id()

    if mode == "elem":
        ap = argparse.ArgumentParser(prog="record.py FILE elem")
        ap.add_argument("items", nargs="+", help="element ids or requirement ids, then the result")
        ap.add_argument("--policy")
        ap.add_argument("--procedure")
        ap.add_argument("--evidence")
        ap.add_argument("--notes")
        a = ap.parse_args(rest)
        *ids, result = a.items
        result = result.upper().replace("_", " ").strip()
        result = {"NA": "N/A", "NOTMET": "NOT MET", "NOT-MET": "NOT MET", "OPEN": "NOT ASSESSED"}.get(result, result)
        if result not in RESULTS:
            die(f"result must be one of {RESULTS}")
        targets = []
        for i in ids:
            if "[" in i or re.search(r"^[A-Za-z]{2}-\d+\.\d+$", i.strip()):
                targets.append(normalize_elem(i))
            else:
                rid = normalize_req(i)
                # A whole requirement skips elements the tailoring already rules out (name them to override).
                targets += [e["id"] for e in catalog[rid]["elements"] if element_applicable(e, data.get("tailoring", {}))]
        for t in targets:
            rid = t.split("[")[0]
            if t not in reqs[rid]["elements"]:
                die(f"{t} is not an evaluative element of {rid}")
            el = reqs[rid]["elements"][t]
            el["result"] = result
            for k in ("policy", "procedure"):
                v = yn(getattr(a, k))
                if v is not None:
                    el[k] = v is True
            if a.evidence is not None:
                el["evidence"] = a.evidence
            if a.notes is not None:
                el["notes"] = a.notes
        save_assessment(path, data)
        for rid in sorted({t.split("[")[0] for t in targets}):
            print(show(data, rid))

    elif mode == "maturity":
        ap = argparse.ArgumentParser(prog="record.py FILE maturity")
        ap.add_argument("req")
        for k in ("policy", "procedure", "implemented", "measured", "managed"):
            ap.add_argument("--" + k)
        a = ap.parse_args(rest)
        rid = normalize_req(a.req)
        mat = reqs[rid].setdefault("maturity", {})
        for k in ("policy", "procedure", "implemented", "measured", "managed"):
            v = getattr(a, k)
            if v is not None:
                mat[k] = rating(v)
        save_assessment(path, data)
        print(show(data, rid))

    elif mode == "req":
        ap = argparse.ArgumentParser(prog="record.py FILE req")
        ap.add_argument("req")
        for k in ("implementation", "planned", "na", "responsible", "provider", "notes", "interviewees", "measured", "managed", "scope"):
            ap.add_argument("--" + k)
        ap.add_argument("--evidence", action="append")
        a = ap.parse_args(rest)
        rid = normalize_req(a.req)
        r = reqs[rid]
        for k, f in (("implementation", "implementation"), ("planned", "planned_implementation"), ("na", "na_justification"),
                     ("responsible", "responsible"), ("provider", "provider"), ("notes", "notes"),
                     ("interviewees", "interviewees"), ("measured", "measured"), ("managed", "managed")):
            v = getattr(a, k)
            if v is not None:
                r[f] = v
        if a.evidence:
            r["evidence"] = r.get("evidence", []) + [e for e in a.evidence if e not in r.get("evidence", [])]
        if a.scope is not None:
            s = a.scope.lower()
            if s not in ("in", "out", "auto"):
                die("--scope must be in, out or auto")
            r["scope_override"] = None if s == "auto" else s
        if (r.get("provider") or "").startswith("Inherited") and catalog[rid]["inheritance"] == "No":
            print(f"WARNING: {rid} is not inheritable per HITRUST; record it as Customer or Shared.", file=sys.stderr)
        save_assessment(path, data)
        print(show(data, rid))

    elif mode == "tailor":
        ap = argparse.ArgumentParser(prog="record.py FILE tailor")
        ap.add_argument("--models")
        for k in ("q2", "q3", "rag", "finetune", "tools", "external-models", "model-builder"):
            ap.add_argument("--" + k)
        a = ap.parse_args(rest)
        t = data.setdefault("tailoring", {})
        if a.models is not None:
            ms = [m.strip().lower() for m in a.models.split(",") if m.strip()]
            if any(m not in MODEL_TYPES for m in ms):
                die(f"model types: {MODEL_TYPES}")
            t["model_types"] = ms
        for k in ("q2", "q3", "rag", "finetune", "tools", "external_models", "model_builder"):
            v = yn(getattr(a, k))
            if v is not None:
                t[k] = None if v == "unset" else v
        save_assessment(path, data)
        n = sum(1 for r in catalog.values() if requirement_eval(r, reqs[r["id"]], t)["in_scope"])
        print(f"Tailoring saved: {json.dumps(t)}; {n} of 44 AI requirements in scope")

    elif mode == "level":
        ap = argparse.ArgumentParser(prog="record.py FILE level")
        ap.add_argument("level", choices=("ai2", "ai1"))
        ap.add_argument("--measured-managed")
        a = ap.parse_args(rest)
        data["meta"]["level"] = a.level
        data["meta"]["base_assessment"] = "r2" if a.level == "ai2" else "e1/i1"
        if a.measured_managed is not None:
            data["meta"]["measured_managed"] = yn(a.measured_managed) is True and a.level == "ai2"
        if a.level == "ai1":
            data["meta"]["measured_managed"] = False
        save_assessment(path, data)
        print(f"Level {a.level}, Measured/Managed scored: {data['meta']['measured_managed']}")

    elif mode == "cap":
        ap = argparse.ArgumentParser(prog="record.py FILE cap")
        ap.add_argument("req")
        for k in ("weakness", "remediation", "poc", "resources", "completion", "status", "comments"):
            ap.add_argument("--" + k)
        ap.add_argument("--milestone", action="append", help="DATE|description (replaces the list)")
        a = ap.parse_args(rest)
        rid = normalize_req(a.req)
        c = reqs[rid].setdefault("cap", {})
        for k, f in (("weakness", "weakness"), ("remediation", "remediation"), ("poc", "poc"), ("resources", "resources"),
                     ("completion", "scheduled_completion"), ("status", "status"), ("comments", "comments")):
            v = getattr(a, k)
            if v is not None:
                c[f] = v
        if a.milestone:
            c["milestones"] = [{"date": d.strip(), "description": desc.strip()} for d, _, desc in (m.partition("|") for m in a.milestone)]
        save_assessment(path, data)
        print(f"{rid} CAP updated")

    elif mode in ("set", "append"):
        if len(rest) != 2:
            die(f"usage: record.py FILE {mode} dotted.path VALUE")
        keys, value = rest[0].split("."), rest[1]
        node = data
        for k in keys[:-1]:
            node = node.setdefault(k, {})
        if mode == "set":
            node[keys[-1]] = value
        else:
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass
            node.setdefault(keys[-1], []).append(value)
        save_assessment(path, data)
        print(f"{rest[0]} {'set' if mode == 'set' else 'appended'}")
    else:
        die("mode must be elem | maturity | req | tailor | level | cap | set | append")


if __name__ == "__main__":
    main()
