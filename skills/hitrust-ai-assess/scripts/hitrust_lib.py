"""Shared helpers for the HITRUST AI Wizard scripts.

Data: ../references/requirements.json (HITRUST AI Security Assessment requirements, evaluative
elements, tailoring conditions, inheritability). Scoring follows HITRUST's PRISMA maturity model:

  ai2 (with r2): Policy 15, Procedure 20, Implemented 40, Measured 10, Managed 15 (Measured and
                 Managed optional; when not scored they add 0, so a requirement tops out at 75).
                 Certification: average of the in-scope AI requirement scores >= 62.
  ai1 (with e1/i1): Implemented only. Certification: average >= 83.

Each maturity level is rated Non-compliant 0, Somewhat 25, Partially 50, Mostly 75, Fully 100.
The scripts suggest a level from evaluative-element coverage (HITRUST rubric coverage bands); the
assessor's own rating always wins.
"""
import json
import os
import re
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "references", "requirements.json")

RESULTS = ("MET", "NOT MET", "N/A", "NOT ASSESSED")
LEVELS = ("policy", "procedure", "implemented", "measured", "managed")
WEIGHTS = {"policy": 15, "procedure": 20, "implemented": 40, "measured": 10, "managed": 15}
RATINGS = {0: "Non-compliant", 25: "Somewhat compliant", 50: "Partially compliant", 75: "Mostly compliant", 100: "Fully compliant"}
RATING_ABBR = {0: "NC", 25: "SC", 50: "PC", 75: "MC", 100: "FC"}
THRESHOLD = {"ai2": 62, "ai1": 83}
CAP_LINE = {"ai2": 71, "ai1": 83}
MODEL_TYPES = ("rule", "predictive", "generative")
CHARACTERISTICS = ("rag", "finetune", "tools", "external_models", "model_builder")


def load_data():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def requirements():
    return load_data()["requirements"]


def reqs_by_id():
    return {r["id"]: r for r in requirements()}


def sort_key(rid):
    order = [t["code"] for t in load_data()["topics"]]
    m = re.match(r"([A-Z]{2})-(\d+)", rid)
    return (order.index(m.group(1)) if m and m.group(1) in order else 99, int(m.group(2)) if m else 0)


def normalize_req(s):
    """tm1, TM-01, TM.1, 17.03bAISecOrganizational.4 -> TM-01"""
    s = s.strip()
    for r in requirements():
        if s.lower() == r["hitrust_id"].lower():
            return r["id"]
    m = re.match(r"^([A-Za-z]{2})[-. ]?0*(\d+)$", s)
    if not m:
        raise ValueError(f"Not an AI requirement id: {s}")
    rid = f"{m.group(1).upper()}-{int(m.group(2)):02d}"
    if rid not in reqs_by_id():
        raise ValueError(f"Unknown AI requirement: {s}")
    return rid


def normalize_elem(s):
    """TM-01[3] / tm1[3] / TM-01.3 -> TM-01[3]"""
    m = re.match(r"^(.+?)\s*(?:\[(\d+)\]|\.(\d+))$", s.strip())
    if not m:
        raise ValueError(f"Not an element id: {s}")
    return f"{normalize_req(m.group(1))}[{int(m.group(2) or m.group(3))}]"


def load_assessment(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_assessment(path, data):
    data.setdefault("meta", {})["last_updated"] = date.today().isoformat()
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


# ---------- tailoring ----------
def in_scope(req, tailoring, override=None):
    """(bool, reason). Mirrors MyCSF tailoring from the three AI questions; override 'in'/'out' wins."""
    if override == "in":
        return True, "included by assessor override"
    if override == "out":
        return False, "excluded by assessor override"
    types = [t for t in (tailoring.get("model_types") or []) if t in MODEL_TYPES]
    if not types:
        return True, "tailoring not answered yet (model type unknown)"
    ap = req["applies"]
    if not any(t in ap["models"] for t in types):
        return False, "model type not in scope (" + ", ".join(ap["models"]) + " only)"
    q2, q3 = tailoring.get("q2"), tailoring.get("q3")
    trig = ap.get("trigger")
    if trig == "q2" and q2 is False:
        return False, "Q2 answered no (no sensitive data used for training/tuning/RAG)"
    if trig == "q3" and q3 is False:
        return False, "Q3 answered no (model architecture not confidential)"
    if trig == "q2_or_q3" and q2 is False and q3 is False:
        return False, "Q2 and Q3 both answered no"
    return True, "in scope"


def requirement_na(req, tailoring):
    """Requirement in the tailored set but not applicable to this system (e.g. no agents/plugins)."""
    need = req["applies"].get("requires")
    return bool(need) and tailoring.get(need) is False


def element_applicable(elem, tailoring):
    c = elem.get("cond")
    return not (c and tailoring.get(c) is False)


def element_state(elem, entry, tailoring):
    """Effective implemented result: a recorded result wins; otherwise N/A when tailoring rules the element out."""
    res = (entry or {}).get("result", "NOT ASSESSED")
    if res == "NOT ASSESSED" and not element_applicable(elem, tailoring):
        return "N/A"
    return res


# ---------- scoring ----------
def band(pct):
    """HITRUST rubric coverage bands -> rating."""
    if pct is None:
        return None
    if pct >= 90:
        return 100
    if pct >= 66:
        return 75
    if pct >= 33:
        return 50
    if pct >= 11:
        return 25
    return 0


def requirement_eval(req, entry, tailoring, level="ai2", mm=False, override=None):
    """Everything about one requirement: scope, status, coverage, suggested and final maturity, score."""
    scope, why = in_scope(req, tailoring, override if override is not None else (entry or {}).get("scope_override"))
    out = {"id": req["id"], "title": req["title"], "hitrust_id": req["hitrust_id"], "domain": req["domain"],
           "topic_code": req["topic_code"], "in_scope": scope, "scope_reason": why}
    if not scope:
        out.update(status="OUT OF SCOPE", score=None)
        return out
    entry = entry or {}
    elems = entry.get("elements", {})
    states = {e["id"]: element_state(e, elems.get(e["id"]), tailoring) for e in req["elements"]}
    applicable = [e for e in req["elements"] if states[e["id"]] != "N/A"]
    if requirement_na(req, tailoring) and not any(states[e["id"]] in ("MET", "NOT MET") for e in req["elements"]):
        out.update(status="N/A", score=None, na_reason="only when " + load_data()["requires_text"][req["applies"]["requires"]])
        return out
    if not applicable:
        out.update(status="N/A", score=None, na_reason="every element N/A")
        return out
    open_ = [e["id"] for e in applicable if states[e["id"]] == "NOT ASSESSED"]
    met = sum(1 for e in applicable if states[e["id"]] == "MET")
    n = len(applicable)
    cov = {
        "implemented": round(100 * met / n) if not open_ else None,
        "policy": round(100 * sum(1 for e in applicable if elems.get(e["id"], {}).get("policy")) / n),
        "procedure": round(100 * sum(1 for e in applicable if elems.get(e["id"], {}).get("procedure")) / n),
    }
    suggested = {k: band(cov[k]) for k in cov}
    suggested["implemented"] = band(cov["implemented"]) if cov["implemented"] is not None else None
    ov = entry.get("maturity", {}) or {}
    used = LEVELS if level == "ai2" and mm else (("policy", "procedure", "implemented") if level == "ai2" else ("implemented",))
    final, src = {}, {}
    for k in LEVELS:
        if k not in used:
            continue
        if ov.get(k) is not None:
            final[k], src[k] = int(ov[k]), "assessor"
        elif k in suggested and suggested[k] is not None:
            final[k], src[k] = suggested[k], "suggested"
        else:
            final[k], src[k] = None, "unrated"
    complete = not open_ and all(final[k] is not None for k in used)
    if level == "ai1":
        sc = final["implemented"] if final["implemented"] is not None else None
    else:
        sc = sum(WEIGHTS[k] * (final[k] or 0) / 100 for k in used) if complete else None
        if sc is not None:
            sc = round(sc, 2)
    status = "NOT ASSESSED" if open_ else ("FULLY MET" if met == n else "NOT MET")
    flags = []
    if mm and level == "ai2" and final.get("managed") is not None and final.get("measured") is not None and final["managed"] > final["measured"]:
        flags.append("Managed rated higher than Measured; HITRUST does not allow that")
    out.update(status=status, elements_total=n, elements_met=met, elements_open=open_,
               coverage=cov, suggested=suggested, final=final, source=src, score=sc, complete=complete, flags=flags,
               not_met=[e["id"] for e in applicable if states[e["id"]] == "NOT MET"])
    if sc is not None:
        impl = final.get("implemented")
        out["cap_candidate"] = sc < CAP_LINE[level] and (impl is None or impl < 100)
        out["gap"] = (not out["cap_candidate"]) and sc < (100 if level == "ai1" or mm else 75)
    return out


def score(data):
    meta = data.get("meta", {})
    level = meta.get("level", "ai2")
    mm = bool(meta.get("measured_managed"))
    tail = data.get("tailoring", {})
    reqs = data["requirements"]
    rows = [requirement_eval(r, reqs.get(r["id"], {}), tail, level, mm) for r in sorted(requirements(), key=lambda r: sort_key(r["id"]))]
    scoped = [x for x in rows if x["in_scope"]]
    counted = [x for x in scoped if x["status"] not in ("N/A",)]
    scored = [x for x in counted if x.get("score") is not None]
    avg = round(sum(x["score"] for x in scored) / len(scored), 2) if scored else None
    pending = [x for x in counted if x.get("score") is None]
    th = THRESHOLD[level]
    doms = {}
    for x in scored:
        doms.setdefault(x["domain"], []).append(x["score"])
    dom_avg = {d: round(sum(v) / len(v), 2) for d, v in sorted(doms.items())}
    caps = [x for x in scored if x.get("cap_candidate")]
    gaps = [x for x in scored if x.get("gap")]
    types = tail.get("model_types") or []
    if not types:
        verdict = "Tailoring not answered: set the AI model types (and Q2/Q3) before scoring means anything."
    elif not scored:
        verdict = "No requirement fully rated yet."
    elif pending:
        verdict = (f"Provisional: average {avg} over {len(scored)} of {len(counted)} requirements; "
                   f"{len(pending)} still open. {level} threshold is {th}.")
    elif avg >= th:
        verdict = (f"Meets the {level} AI threshold: average {avg} >= {th}. Certification also requires the underlying "
                   f"{'r2' if level == 'ai2' else 'e1/i1'} to certify.")
    else:
        verdict = f"Below the {level} AI threshold: average {avg} < {th}."
    return {"level": level, "measured_managed": mm, "threshold": th, "average": avg, "in_scope": len(scoped),
            "counted": len(counted), "scored": len(scored), "pending": len(pending), "na": len(scoped) - len(counted),
            "out_of_scope": len(rows) - len(scoped), "domain_averages": dom_avg, "cap_candidates": caps, "gaps": gaps,
            "verdict": verdict, "rows": rows,
            "elements": {"total": sum(x.get("elements_total", 0) for x in counted),
                         "open": sum(len(x.get("elements_open", [])) for x in counted)}}


def cap_ids(data):
    s = score(data)
    return {x["id"]: f"CAP-{i:03d}" for i, x in enumerate(s["cap_candidates"], 1)}


def fmt_level(v):
    return "—" if v is None else f"{RATING_ABBR[v]} {v}"
