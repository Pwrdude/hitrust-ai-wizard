#!/usr/bin/env python3
"""Generate the HITRUST AI (ai2 / ai1) template kit from an assessment workbook.

Writes six client evidence templates (Word), the AI Security Registers workbook (Excel), and three
assessor deliverables (interview guide and readiness report in Word, evidence request list and CAP
tracker in Excel). Everything is filled from the workbook: client, system, assessor, owners, models,
providers, tailoring and, for the report and CAP tracker, the current scores.

Tailoring decides what goes in. A section, row or tab tied to a requirement or system characteristic
that tailoring rules out is left out; anything still unanswered stays in, so regenerate after the
first sync once tailoring is settled.

  python3 generate_templates.py <workbook.json> [--out DIR] [--only client|assessor] [--zip]

Needs python-docx and openpyxl (pip install python-docx openpyxl).
"""
import argparse
import os
import re
import sys
import zipfile
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

try:
    from docx_writer import DocBuilder
    import xlsx_writer
except ImportError as e:  # pragma: no cover
    sys.exit(f"ERROR: {e}. Install the dependencies: pip install python-docx openpyxl")

import hitrust_lib as hl
import templates_content as tc


# ---------------------------------------------------------------- context
class Context:
    def __init__(self, data):
        self.data = data
        self.meta = data.get("meta", {})
        self.tail = data.get("tailoring", {}) or {}
        self.sys = data.get("system", {}) or {}
        self.level = self.meta.get("level", "ai2")
        self.types = [t for t in (self.tail.get("model_types") or []) if t in hl.MODEL_TYPES]
        self.score = hl.score(data)
        self.rows = {r["id"]: r for r in self.score["rows"]}
        self.reqs = hl.reqs_by_id()

    # tri-state: True, False, or None (not answered yet)
    def flag(self, name):
        if name.startswith("req:"):
            row = self.rows.get(name[4:])
            if row is None:
                raise ValueError(f"unknown requirement in condition: {name}")
            return row["in_scope"] and row["status"] != "N/A"
        if name in hl.MODEL_TYPES:
            return (name in self.types) if self.types else None
        if name == "ml":
            return any(t in self.types for t in ("predictive", "generative")) if self.types else None
        if name in ("q2", "q3") + hl.CHARACTERISTICS:
            return self.tail.get(name)
        raise ValueError(f"unknown condition name: {name}")

    def cond(self, expr):
        """Keep content unless the expression is definitely false."""
        if not expr:
            return True
        return _eval(_tokens(expr), self.flag) is not False

    def person(self, key):
        p = self.sys.get(key) or {}
        bits = [b for b in (p.get("name"), p.get("title")) if b]
        return ", ".join(bits) if bits else "[Name, title]"

    def tokens(self):
        client = (self.data.get("client") or {}).get("name") or "[Client]"
        users = self.sys.get("users") or {}
        u = "; ".join(x for x in (users.get("end_users"), users.get("privileged_users")) if x)
        return {
            "client": client,
            "system": self.sys.get("name") or "[AI system]",
            "assessor": self.meta.get("assessor") or "[Assessor]",
            "level": self.level,
            "threshold": str(hl.THRESHOLD[self.level]),
            "base": self.meta.get("base_assessment") or ("r2" if self.level == "ai2" else "e1/i1"),
            "assessment_type": (self.meta.get("assessment_type") or "assessment").split(" (")[0].lower(),
            "today": date.today().isoformat(),
            "doc_line": f"*Template for {client} · HITRUST {self.level} · generated {date.today().isoformat()}*",
            "system_owner": self.person("system_owner"),
            "gov_lead": self.person("ai_governance_lead"),
            "iso": self.person("security_officer"),
            "system_description": self.sys.get("description") or "[What the system does and for whom]",
            "users": u or "[End users; staff; privileged users]",
            "diagram": self.sys.get("diagram_reference") or "[File name and location; include trust boundaries and data flows]",
            "platforms": self.sys.get("ai_platforms") or self.sys.get("deployment") or "[Cloud subscription, regions, services, quotas]",
        }


def _tokens(expr):
    return re.findall(r"\(|\)|[A-Za-z_]+:[A-Z]{2}-\d{2}|[A-Za-z_][A-Za-z_0-9]*", expr)


def _eval(toks, flag):
    pos = [0]

    def peek():
        return toks[pos[0]] if pos[0] < len(toks) else None

    def take():
        pos[0] += 1
        return toks[pos[0] - 1]

    def atom():
        t = take()
        if t == "not":
            v = atom()
            return None if v is None else not v
        if t == "(":
            v = disj()
            take()
            return v
        return flag(t)

    def conj():
        vals = [atom()]
        while peek() == "and":
            take()
            vals.append(atom())
        return False if False in vals else (None if None in vals else True)

    def disj():
        vals = [conj()]
        while peek() == "or":
            take()
            vals.append(conj())
        return True if True in vals else (None if None in vals else False)

    return disj()


def preprocess(markup, ctx, inserts):
    out, stack = [], []
    for line in markup.split("\n"):
        s = line.strip()
        if s.startswith("@if "):
            stack.append(ctx.cond(s[4:].strip()))
            continue
        if s == "@endif":
            stack.pop()
            continue
        if not all(stack):
            continue
        if s.startswith("@insert "):
            out.append(inserts[s[8:].strip()](ctx))
            continue
        out.append(line)
    if stack:
        raise ValueError("unbalanced @if")
    text = "\n".join(out)
    toks = ctx.tokens()
    return re.sub(r"\{\{(\w+)\}\}", lambda m: toks.get(m.group(1), m.group(0)), text)


# ---------------------------------------------------------------- inserts
def _cell(v):
    return str(v if v not in (None, "") else "").replace("|", "/").replace("\n", " ")


def _table(header, rows):
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
    lines += ["| " + " | ".join(_cell(c) for c in r) + " |" for r in rows]
    return "\n".join(lines)


def ins_scope_table(ctx):
    types = ", ".join(t.capitalize() for t in ctx.types) or "[Generative / Predictive / Rule-based]"
    return _table(["In-scope AI system", "Business purpose", "Model type(s)", "Hosting / AI platform", "System owner"],
                  [[ctx.tokens()["system"], ctx.sys.get("description") or "[Purpose]", types,
                    ctx.sys.get("ai_platforms") or "[e.g. Azure OpenAI, AWS Bedrock, vendor SaaS]", ctx.person("system_owner")]])


def ins_models_table(ctx):
    models = [m for m in ctx.sys.get("models", []) if isinstance(m, dict)]
    rows = [[m.get("name"), m.get("version"), (m.get("type") or "").capitalize(), m.get("source"), m.get("provider"),
             m.get("owner"), ""] for m in models]
    if not rows:
        rows = [["[Model name]", "[Exact version / deployment ID]", "[Generative / Predictive / Rule-based]",
                 "[Internal / External]", "[Provider]", "[Owner]", "[Purpose in the flow]"]]
    return _table(["Model", "Version / deployment", "Type", "Internal / External", "Provider or builder", "Owner",
                   "Purpose in the flow"], rows)


def ins_threat_model_table(ctx):
    rows = [[tid, name, ref, reqs, "", "", "", "", "", ""] for tid, name, ref, reqs, c in tc.THREATS
            if ctx.cond(c)]
    return _table(["ID", "Threat", "Reference", "Related requirements", "Affected components", "Exposure (H/M/L)",
                   "Countermeasures in place", "Additional needed", "Residual risk", "Owner / due"], rows)


def _out_of_scope(ctx):
    return [r for r in ctx.score["rows"] if not r["in_scope"] or r["status"] == "N/A"]


def ins_scope_note(ctx):
    s = ctx.score
    if not ctx.types:
        return "> Tailoring is not answered yet, so all 44 AI requirements are shown. Regenerate after the first sync."
    out = _out_of_scope(ctx)
    ids = ", ".join(r["id"] for r in out) or "none"
    return (f"> Tailoring puts {s['in_scope'] - s['na']} of 44 AI requirements in scope. Out of scope or not "
            f"applicable: {ids}. Skip their questions.")


def ins_summary_table(ctx):
    s = ctx.score
    lvl = ctx.level
    caps, gaps = s["cap_candidates"], s["gaps"]
    rows = [
        ["Target", f"HITRUST {lvl} (on {ctx.tokens()['base']})"],
        ["Assessment type", ctx.meta.get("assessment_type") or ""],
        ["Assessor", ctx.meta.get("assessor") or ""],
        ["Fieldwork dates", f"{ctx.meta.get('started') or '[start]'} to {ctx.meta.get('assessment_date') or '[end]'}"],
        ["AI requirements in scope", f"{s['counted']} of 44" + ("" if ctx.types else " (tailoring not answered)")],
        ["Requirements fully rated", f"{s['scored']} of {s['counted']}"],
        ["Estimated average AI requirement score", "not yet scored" if s["average"] is None else str(s["average"])],
        [f"{lvl} certification threshold", f"{s['threshold']} (and the underlying {ctx.tokens()['base']} must certify)"],
        ["Status", s["verdict"]],
        ["Measured and Managed scored", "Yes" if s["measured_managed"] else
         ("No (score ceiling 75 per requirement)" if lvl == "ai2" else "Not applicable (ai1 scores Implemented only)")],
        ["CAP candidates", str(len(caps))],
        ["Gaps (no CAP expected)", str(len(gaps))],
    ]
    return _table(["Measure", "Result"], rows)


def _yn(v):
    return {True: "Yes", False: "No", None: "Not answered"}[v]


def ins_tailoring_table(ctx):
    t = ctx.tail
    types = ", ".join(ctx.types) or "Not answered"
    rows = [
        ["Q1 Model types in scope", types, "Sets the base requirement set"],
        ["Q2 Sensitive data used to train, tune or ground (RAG)", _yn(t.get("q2")), "Adds MR-01, MR-02, EN-02 when yes"],
        ["Q3 Confidential model architecture", _yn(t.get("q3")), "Adds AX-01, MR-02, EN-02 when yes"],
        ["RAG used", _yn(t.get("rag")), "RAG elements applicable or N/A"],
        ["Fine-tuning used", _yn(t.get("finetune")), "Fine-tuning elements"],
        ["Agents / plugins used", _yn(t.get("tools")), "DV-05 and agent elements"],
        ["External models used", _yn(t.get("external_models")), "SC-02, DV-04 element 4"],
        ["Client builds models", _yn(t.get("model_builder")), "IN-04"],
        ["Requirements in scope (this tool)", str(ctx.score["counted"]),
         "Compare with the MyCSF object; MyCSF is authoritative and scope overrides follow it"],
    ]
    return _table(["Tailoring question / characteristic", "Answer", "Effect"], rows)


def ins_inheritance_table(ctx):
    rows = []
    for rid in sorted(ctx.data.get("requirements", {}), key=hl.sort_key):
        prov = (ctx.data["requirements"][rid] or {}).get("provider") or "Customer"
        if prov != "Customer":
            rows.append([rid, ctx.reqs[rid]["title"], prov, ctx.reqs[rid]["inheritance"], ""])
    if not rows:
        rows = [["[Req]", "", "[Inherited / Shared (provider)]", "", "[HITRUST certification incl. AI, SRM]"]]
    return _table(["Req", "Requirement", "Responsibility", "HITRUST inheritability", "Basis"], rows)


def ins_method_text(ctx):
    if ctx.level == "ai1":
        return ("Each applicable evaluative element was rated Implemented (MET / NOT MET / N/A) using examine, interview "
                "and test. ai1 scores the Implemented level only, rated NC 0, SC 25, PC 50, MC 75 or FC 100; the AI score "
                "is the average across in-scope requirements, compared with the ai1 threshold of 83.")
    mm = ctx.score["measured_managed"]
    lv = "Policy 15%, Procedure 20%, Implemented 40%" + (", Measured 10%, Managed 15%" if mm else
                                                         "; Measured and Managed were not scored")
    return ("Each applicable evaluative element was rated Implemented (MET / NOT MET / N/A) with Policy and Procedure "
            f"coverage, using examine, interview and test. PRISMA maturity was rated per requirement: {lv}. Each level "
            "was rated NC 0, SC 25, PC 50, MC 75 or FC 100. A requirement scores the weighted sum; the AI score is the "
            "average across in-scope requirements, compared with the ai2 threshold of 62. CAP candidates are requirements "
            "below 71 with Implemented below Fully compliant; the control-reference average condition can only be "
            "confirmed in MyCSF.")


def ins_topic_table(ctx):
    topics = hl.load_data()["topics"]
    rows = []
    for t in topics:
        rs = [r for r in ctx.score["rows"] if r["topic_code"] == t["code"]]
        counted = [r for r in rs if r["in_scope"] and r["status"] != "N/A"]
        scored = [r["score"] for r in counted if r.get("score") is not None]
        avg = round(sum(scored) / len(scored), 1) if scored else "—"
        below = sum(1 for x in scored if x < ctx.score["threshold"])
        caps = sum(1 for r in counted if r.get("cap_candidate"))
        rows.append([f"{t['code']} {t['name']}", f"{len(counted)} of {len(rs)}", f"{len(scored)}", avg, below, caps])
    return _table(["Topic", "In scope", "Scored", "Average score", f"Below {ctx.score['threshold']}", "CAP candidates"], rows)


def _lvl(final, k):
    v = (final or {}).get(k)
    return "—" if v is None else hl.RATING_ABBR[v]


def ins_requirement_table(ctx):
    rows = []
    for r in ctx.score["rows"]:
        entry = ctx.data["requirements"].get(r["id"], {})
        if not r["in_scope"]:
            rows.append([r["id"], r["title"], "Out", "", "", "", "", "", ""])
            continue
        if r["status"] == "N/A":
            rows.append([r["id"], r["title"], "N/A", "", "", "", "", "", ""])
            continue
        # ratings are shown only once every element has a result; until then coverage suggestions mislead
        f = r.get("final", {}) if r.get("score") is not None else {}
        sc = "open" if r.get("score") is None else r["score"]
        cap = "Yes" if r.get("cap_candidate") else ("Gap" if r.get("gap") else "")
        row = [r["id"], r["title"], "In", entry.get("provider") or "Customer"]
        if ctx.level == "ai2":
            row += [_lvl(f, "policy"), _lvl(f, "procedure"), _lvl(f, "implemented")]
        else:
            row += ["", "", _lvl(f, "implemented")]
        rows.append(row + [sc, cap])
    return _table(["Req", "Requirement", "Scope", "Responsibility", "Policy", "Procedure", "Implemented", "Score",
                   "CAP / gap"], rows)


def ins_cap_text(ctx):
    line = hl.CAP_LINE[ctx.level]
    return (f"Requirements estimated below {line} with Implemented below Fully compliant. Each needs a corrective "
            f"action plan if HITRUST confirms the control-reference average is also below {line}. Full entries live "
            "in the CAP Tracker.")


def ins_cap_table(ctx):
    rows = []
    ids = hl.cap_ids(ctx.data)
    for r in ctx.score["cap_candidates"]:
        cap = (ctx.data["requirements"].get(r["id"], {}) or {}).get("cap", {}) or {}
        rows.append([ids.get(r["id"], ""), r["id"], r["score"], cap.get("weakness") or ", ".join(r.get("not_met", [])),
                     cap.get("remediation") or "", cap.get("poc") or "", cap.get("scheduled_completion") or ""])
    if not rows:
        rows = [["—", "None yet", "", "No requirement is fully rated below the CAP line yet", "", "", ""]]
    return _table(["CAP", "Req", "Est. score", "Weakness (condition)", "Corrective action", "Owner", "Target date"], rows)


def ins_gap_table(ctx):
    rows = [[r["id"], r["title"], r["score"], ", ".join(r.get("not_met", [])) or "Maturity below full marks", ""]
            for r in ctx.score["gaps"]]
    if not rows:
        rows = [["—", "None yet", "", "", ""]]
    return _table(["Req", "Requirement", "Est. score", "Gap", "Recommendation"], rows)


def ins_interviewee_table(ctx):
    seen = {}
    for rid, e in ctx.data.get("requirements", {}).items():
        for who in re.split(r"[;,]\s*", (e or {}).get("interviewees") or ""):
            if who.strip():
                seen.setdefault(who.strip(), []).append(rid)
    rows = [[who, "", ", ".join(sorted(v, key=hl.sort_key))] for who, v in sorted(seen.items())]
    if not rows:
        rows = [["[Role]", "[Date]", "[Requirements discussed]"]]
    return _table(["Interviewee (role)", "Date", "Requirements discussed"], rows)


def ins_mm_limit(ctx):
    if ctx.level == "ai2" and not ctx.score["measured_managed"]:
        return "- Measured and Managed were not scored, so no requirement can exceed 75."
    return ""


INSERTS = {
    "scope_table": ins_scope_table, "models_table": ins_models_table, "threat_model_table": ins_threat_model_table,
    "scope_note": ins_scope_note, "summary_table": ins_summary_table, "tailoring_table": ins_tailoring_table,
    "inheritance_table": ins_inheritance_table, "method_text": ins_method_text, "topic_table": ins_topic_table,
    "requirement_table": ins_requirement_table, "cap_text": ins_cap_text, "cap_table": ins_cap_table,
    "gap_table": ins_gap_table, "interviewee_table": ins_interviewee_table, "mm_limit": ins_mm_limit,
}


# ---------------------------------------------------------------- main
def slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")


def build(path, out_dir, only=None):
    data = hl.load_assessment(path)
    ctx = Context(data)
    tok = ctx.tokens()
    os.makedirs(out_dir, exist_ok=True)
    written = []
    for stem, title, markup, landscape in tc.DOCUMENTS:
        is_assessor = stem.startswith("assessor/")
        if (only == "client" and is_assessor) or (only == "assessor" and not is_assessor):
            continue
        dest = os.path.join(out_dir, stem + ".docx")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        b = DocBuilder(landscape=landscape, header_text=f"{tok['client']} · {title}",
                       footer_text="Confidential" if not is_assessor else "Confidential · Assessor working paper")
        b.render(preprocess(markup, ctx, INSERTS))
        b.save(dest)
        written.append(dest)
    if only != "assessor":
        dest = os.path.join(out_dir, "07-AI-Security-Registers.xlsx")
        xlsx_writer.registers(ctx, dest)
        written.append(dest)
    if only != "client":
        dest = os.path.join(out_dir, "assessor", "A3-Evidence-Request-List-and-CAP-Tracker.xlsx")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        xlsx_writer.evidence(ctx, dest)
        written.append(dest)
    return ctx, written


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("workbook")
    ap.add_argument("--out", help="output folder (default: <client>-<level>-templates next to the workbook)")
    ap.add_argument("--only", choices=("client", "assessor"))
    ap.add_argument("--zip", action="store_true", help="also write a .zip of the kit")
    a = ap.parse_args()
    data = hl.load_assessment(a.workbook)
    client = (data.get("client") or {}).get("name") or "client"
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.workbook)),
                                f"{slug(client)}-{data.get('meta', {}).get('level', 'ai2')}-templates")
    ctx, written = build(a.workbook, out, a.only)
    s = ctx.score
    print(f"Wrote {len(written)} files to {out}")
    for w in written:
        print("  " + os.path.relpath(w, out))
    print(("Tailoring not answered: every requirement included. " if not ctx.types else "") +
          f"{s['counted']} requirements in scope; {s['scored']} scored; average {s['average']}.")
    if a.zip:
        zpath = out.rstrip("/\\") + ".zip"
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for w in written:
                z.write(w, os.path.join(os.path.basename(out), os.path.relpath(w, out)))
        print(f"Zip: {zpath}")


if __name__ == "__main__":
    main()
