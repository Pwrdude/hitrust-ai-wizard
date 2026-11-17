#!/usr/bin/env python3
"""Show HITRUST AI assessment progress and what to assess next.

  python3 status.py A.json                # tailoring, progress by topic, next open elements
  python3 status.py A.json --topic AX     # element-level detail for one topic
  python3 status.py A.json --req LM-01    # one requirement: statement, elements, maturity, score
"""
import argparse

from hitrust_lib import (fmt_level, load_assessment, load_data, normalize_req, requirement_eval, requirements,
                         sort_key, element_state)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--topic")
    ap.add_argument("--req")
    ap.add_argument("--next", type=int, default=6)
    a = ap.parse_args()
    data = load_assessment(a.file)
    meta, tail, reqs = data["meta"], data.get("tailoring", {}), data["requirements"]
    level, mm = meta.get("level", "ai2"), meta.get("measured_managed", False)
    cat = sorted(requirements(), key=lambda r: sort_key(r["id"]))
    ctext = load_data()["cond_text"]

    if a.req:
        rid = normalize_req(a.req)
        r = next(x for x in cat if x["id"] == rid)
        e = requirement_eval(r, reqs[rid], tail, level, mm)
        print(f"{rid}  {r['title']}  [{r['hitrust_id']}; {r['domain']}; {r['control_ref']}; inheritable: {r['inheritance']}]")
        print(f"  {r['statement']}")
        print(f"  Applies: {r['applies_text']}. {r['note']}")
        if not e["in_scope"]:
            print(f"  OUT OF SCOPE: {e['scope_reason']}")
            return
        for el in r["elements"]:
            x = reqs[rid]["elements"][el["id"]]
            st = element_state(el, x, tail)
            pp = ("P" if x.get("policy") else "-") + ("p" if x.get("procedure") else "-")
            cond = f" ({ctext[el['cond']]})" if el.get("cond") else ""
            print(f"  {el['id']:<9} {st:<12} {pp}  {el['text']}{cond}")
            if x.get("evidence") or x.get("notes"):
                print(f"{'':14}evidence: {x.get('evidence', '')}  notes: {x.get('notes', '')}")
        if e["status"] == "N/A":
            print(f"  Requirement N/A: {e.get('na_reason')}")
            return
        print(f"  Status: {e['status']} ({e['elements_met']}/{e['elements_total']} elements met)")
        print(f"  Coverage: policy {e['coverage']['policy']}%, procedure {e['coverage']['procedure']}%, implemented "
              + (f"{e['coverage']['implemented']}%" if e['coverage']['implemented'] is not None else "(elements still open)"))
        for k, v in e["final"].items():
            print(f"  {k:<12} {fmt_level(v):<8} ({e['source'][k]}; suggested {fmt_level(e['suggested'].get(k))})")
        print(f"  Score: {e['score'] if e['score'] is not None else 'pending'}" +
              (" · CAP candidate" if e.get("cap_candidate") else " · gap" if e.get("gap") else ""))
        for f in e["flags"]:
            print("  ! " + f)
        return

    print(f"{data['client']['name']} · {data['system']['name']} · {level}"
          f"{' (Measured/Managed scored)' if mm else ''} · {meta.get('assessment_type', '')}")
    print("Tailoring: models=" + (",".join(tail.get("model_types") or []) or "UNSET") +
          "".join(f" {k}={'yes' if tail.get(k) else 'no' if tail.get(k) is False else '?'}"
                  for k in ("q2", "q3", "rag", "finetune", "tools", "external_models", "model_builder")))
    topics = {}
    pending = []
    for r in cat:
        if a.topic and r["topic_code"] != a.topic.upper():
            continue
        e = requirement_eval(r, reqs[r["id"]], tail, level, mm)
        t = topics.setdefault(r["topic_code"], {"name": r["topic"], "in": 0, "out": 0, "na": 0, "done": 0, "open": 0, "scores": []})
        if not e["in_scope"]:
            t["out"] += 1
            continue
        t["in"] += 1
        if e["status"] == "N/A":
            t["na"] += 1
            continue
        if e["score"] is not None:
            t["done"] += 1
            t["scores"].append(e["score"])
        else:
            t["open"] += 1
        pending += [(r, x) for x in e["elements_open"]]
    print(f"\n{'Topic':<5}{'Name':<52}{'In':>3} {'Done':>5} {'Open':>5} {'N/A':>4} {'Out':>4} {'Avg':>7}")
    for code, t in topics.items():
        avg = f"{sum(t['scores']) / len(t['scores']):.1f}" if t["scores"] else "—"
        print(f"{code:<5}{t['name'][:50]:<52}{t['in']:>3} {t['done']:>5} {t['open']:>5} {t['na']:>4} {t['out']:>4} {avg:>7}")
    if a.topic:
        for r in cat:
            if r["topic_code"] != a.topic.upper():
                continue
            e = requirement_eval(r, reqs[r["id"]], tail, level, mm)
            print(f"\n{r['id']} {r['title']}: {e['status']}" + (f", score {e['score']}" if e.get("score") is not None else ""))
            if e["in_scope"] and e["status"] != "N/A":
                for el in r["elements"]:
                    print(f"   {el['id']:<9} {element_state(el, reqs[r['id']]['elements'][el['id']], tail)}")
    if pending:
        print(f"\nNext open elements ({len(pending)} remaining):")
        texts = {el["id"]: el["text"] for r in cat for el in r["elements"]}
        for r, eid in pending[: a.next]:
            print(f"  {eid:<9} {texts[eid]}")
    else:
        print("\nEvery in-scope element has a result.")


if __name__ == "__main__":
    main()
