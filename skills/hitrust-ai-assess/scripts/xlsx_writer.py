"""Excel workbooks of the HITRUST AI template kit (openpyxl): the client's AI Security Registers and the
assessor's Evidence Request List with CAP Tracker. Called by generate_templates.py."""
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

import hitrust_lib as hl
import templates_content as tc

HEAD_FILL = PatternFill("solid", fgColor="1F3A5F")
HEAD_FONT = Font(bold=True, color="FFFFFF", name="Calibri", size=10)
BODY_FONT = Font(name="Calibri", size=10)
NOTE_FONT = Font(name="Calibri", size=9, italic=True, color="595959")
WRAP = Alignment(wrap_text=True, vertical="top")
DATE_FMT = "yyyy-mm-dd"
ROWS_FOR_ENTRY = 200  # rows that get dropdowns and date formats for the client to fill in


def _sheet(wb, title, header, widths, rows=(), dropdowns=None, dates=(), note=None, first=False):
    ws = wb.active if first else wb.create_sheet()
    ws.title = title
    r0 = 1
    if note:
        ws.cell(row=1, column=1, value=note).font = NOTE_FONT
        r0 = 3
    for c, h in enumerate(header, 1):
        cell = ws.cell(row=r0, column=c, value=h)
        cell.fill, cell.font = HEAD_FILL, HEAD_FONT
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    for i, row in enumerate(rows, r0 + 1):
        for c, v in enumerate(row, 1):
            cell = ws.cell(row=i, column=c, value=v if v != "" else None)
            cell.font, cell.alignment = BODY_FONT, WRAP
    for c, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(c)].width = w
    ws.row_dimensions[r0].height = 32
    ws.freeze_panes = ws.cell(row=r0 + 1, column=2)
    last = max(r0 + len(rows), r0 + 1)
    ws.auto_filter.ref = f"A{r0}:{get_column_letter(len(header))}{last}"
    end = r0 + max(len(rows), ROWS_FOR_ENTRY)
    for col, options in (dropdowns or {}).items():
        dv = DataValidation(type="list", formula1='"' + ",".join(options) + '"', allow_blank=True)
        dv.error, dv.errorTitle = "Pick a value from the list", "Invalid entry"
        ws.add_data_validation(dv)
        dv.add(f"{col}{r0 + 1}:{col}{end}")
    for col in dates:
        for r in range(r0 + 1, end + 1):
            ws[f"{col}{r}"].number_format = DATE_FMT
    for r in range(r0 + 1, end + 1):
        for c in range(1, len(header) + 1):
            ws.cell(row=r, column=c).alignment = WRAP
    return ws


YN = ["Yes", "No", "N/A"]
HML = ["High", "Medium", "Low"]


def registers(ctx, dest):
    client, system = ctx.tokens()["client"], ctx.tokens()["system"]
    wb = Workbook()

    tabs = [
        ("RACI", "Who governs, secures and manages risk for the AI system; the accountable human for its outputs and actions", "GV-01", "P8", "Annual; on role change"),
        ("AI Inventory", "Every deployed AI system: platform, model name and version, owner, risk category, providers", "IN-01", "P8", "Semiannual; on model change"),
        ("Threat Register", "AI-specific threats, affected components, countermeasures and treatment", "TM-01, TM-02", "P1", "Before new model; semiannual; after AI incident"),
        ("Data Inventory", "Data used for training, testing, validation, tuning and RAG: provenance, sensitivity, protections", "IN-03, MR-01, FS-01, EN-02, AX-04, LC-02", "P5", "Semiannual; before data use"),
        ("Trusted Sources", "Approved sources of AI data", "IN-02", "P5", "Semiannual"),
        ("Providers", "AI providers: due diligence, assurance, SRM, BAA, contract security terms, model card reviews", "SC-01, SC-02, SC-03", "P4", "Onboarding; annual"),
        ("Change Log", "Every change to models, prompts, RAG, pipelines, agents/plugins and downloaded AI assets", "DV-02, DV-03, DV-04, DV-05, DV-07, DV-08", "P3, P4", "Every change"),
        ("Access Review", "Quarterly review of access to AI data, models, APIs, engineering environments and service identities", "AX-03 to AX-07", "P6", "Quarterly"),
        ("Monitoring Log", "Monthly review of AI inputs/outputs, filter tests and integrity checks of data, models, code and configs", "LM-02, LM-03", "P7", "Monthly"),
        ("Backup & Restore", "Backup coverage of each AI asset and restore test results", "RS-02", "P9", "Per backup schedule; restore test semiannual"),
        ("Training", "Annual AI security training for development, data science and cybersecurity staff", "DV-01", "P10", "Annual"),
        ("Review Log", "Sign-off of every recurring review the HITRUST AI requirements call for", "Several", "All", "As listed"),
    ]
    ml = ctx.cond("ml")
    keep = {"Data Inventory": ml, "Trusted Sources": ctx.cond("req:IN-02")}
    tabs = [t for t in tabs if keep.get(t[0], True)]
    _sheet(wb, "Read Me", ["Tab", "What it records", "HITRUST AI requirements", "Procedure", "Review frequency"],
           [18, 60, 30, 10, 30], tabs, first=True,
           note=f"{client} – {system}: AI Security Registers. Evidence for the HITRUST {ctx.level} assessment. "
                "Keep every row dated; the assessor samples from these tabs.")

    raci_rows = [[a] + codes.split() + [req] for a, codes, req in tc.RACI]
    _sheet(wb, "RACI", ["Activity"] + tc.RACI_ROLES + ["Requirement"], [44] + [14] * 7 + [20], raci_rows,
           note="Suggested defaults: R responsible, A accountable, C consulted, I informed. Confirm with the client "
                "and put names in row 3 headers if useful.")

    models = [m for m in ctx.sys.get("models", []) if isinstance(m, dict)]
    owner = ctx.person("system_owner")
    inv_rows = [[system, ctx.sys.get("ai_platforms") or "", m.get("name"), m.get("version"),
                 (m.get("type") or "").capitalize(), m.get("source"), m.get("provider"), m.get("owner") or owner,
                 "", "", "", "", "Active"] for m in models] or \
               [[system, "[AI platform]", "[Model name]", "[Exact version]", "", "", "[Provider]", owner,
                 "", "", "", "", "Active"]]
    _sheet(wb, "AI Inventory", ["AI system", "AI platform", "Model name", "Model version", "Model type",
                                "Internal / External", "AI service provider(s)", "System owner", "Risk category",
                                "Data sensitivity", "Last reviewed", "Next review due", "Status"],
           [24, 20, 20, 18, 14, 14, 22, 22, 14, 16, 14, 14, 12], inv_rows,
           dropdowns={"E": ["Generative", "Predictive", "Rule-based"], "F": ["Internal", "External"],
                      "I": HML, "M": ["Active", "Pilot", "Retired"]}, dates=("K", "L"))

    thr = [[tid, name, ref, reqs] + [""] * 11 for tid, name, ref, reqs, c in tc.THREATS if ctx.cond(c)]
    _sheet(wb, "Threat Register", ["ID", "Threat", "Reference", "Related requirements", "Description (system-specific)",
                                   "Affected components", "Likelihood", "Impact", "Countermeasures in place",
                                   "Additional countermeasures needed", "Treatment", "Owner", "Date identified",
                                   "Identification trigger", "Status"],
           [7, 34, 26, 22, 34, 24, 11, 11, 32, 32, 12, 16, 14, 20, 12], thr,
           dropdowns={"G": HML, "H": HML, "K": ["Mitigate", "Accept", "Transfer", "Avoid"],
                      "N": ["Before new model", "Semiannual review", "After AI incident", "New threat published"],
                      "O": ["Open", "Treated", "Not applicable"]}, dates=("M",))

    if keep["Data Inventory"]:
        _sheet(wb, "Data Inventory", ["Dataset ID", "Dataset / source", "Use", "Provenance (origin, how collected)",
                                      "Trusted source ID", "Sensitivity level", "Contains PHI / sensitive data",
                                      "Version", "Storage location", "Encrypted at rest", "Access group",
                                      "Data-use assessment date", "Minimized / de-identified",
                                      "Sanitized (poisoning check)", "Owner", "Last reviewed"],
               [11, 28, 14, 32, 12, 14, 14, 10, 24, 12, 18, 14, 14, 14, 16, 14], [],
               dropdowns={"C": ["Training", "Testing", "Validation", "Fine-tuning", "RAG"], "G": YN, "J": YN,
                          "M": YN, "N": YN}, dates=("L", "P"))
    if keep["Trusted Sources"]:
        _sheet(wb, "Trusted Sources", ["Source ID", "Source name", "Source type", "Approved uses",
                                       "Integrity check method", "Approved by", "Approved date", "Last reviewed",
                                       "Status"], [11, 28, 18, 28, 26, 18, 14, 14, 12], [],
               dropdowns={"I": ["Approved", "Under review", "Retired"]}, dates=("G", "H"))

    prov = [[p.get("name"), "", p.get("service") or p.get("role"), p.get("hitrust"), "", "", p.get("srm"), "", "",
             "", "", "", "", ""] for p in ctx.sys.get("providers", []) if isinstance(p, dict)]
    _sheet(wb, "Providers", ["Provider", "Provider type", "Service / component supplied",
                             "HITRUST cert incl. AI requirements", "Cert expiry", "Other assurance (SOC 2 etc.)",
                             "Shared responsibility matrix on file", "BAA signed",
                             "AI security requirements in contract (clause)", "Due diligence date", "Risk rating",
                             "Next review due", "Model card reviewed (model, date)", "Notes"],
           [22, 18, 26, 18, 12, 20, 16, 10, 30, 14, 11, 14, 26, 24], prov,
           dropdowns={"B": ["Model", "Dataset", "Software package", "Platform / infrastructure", "Language model tool",
                            "Contracted AI service"], "H": YN, "K": HML}, dates=("E", "J", "L"))

    _sheet(wb, "Change Log", ["Change ID", "Date deployed", "Asset type", "Asset / component", "From version",
                              "To version", "Description", "Release notes reviewed", "Hash / signature verified",
                              "Vulnerability scan result", "Testing evidence", "Threat review / red team done",
                              "Approved by", "Approval date", "Inventory updated"],
           [12, 13, 16, 24, 14, 14, 34, 12, 12, 20, 24, 14, 18, 13, 12], [],
           dropdowns={"C": ["Model", "Model alias", "Metaprompt", "RAG source / index", "Pipeline config",
                            "Agent / plugin", "Dataset", "Software package"], "H": YN, "I": YN, "L": YN, "O": YN},
           dates=("B", "N"))

    _sheet(wb, "Access Review", ["Review date", "Access type", "Resource", "Account / identity", "Role / permissions",
                                 "Least privilege confirmed", "MFA enforced", "Action", "Reviewer", "Ticket"],
           [13, 26, 24, 24, 26, 12, 10, 12, 18, 12], [],
           dropdowns={"B": ["AI data (AX-04)", "Deployed models (AX-05)", "Model API / app (AX-06)",
                            "Engineering env / code (AX-07)", "Model or agent identity (AX-03)"],
                      "F": YN, "G": YN, "H": ["Keep", "Modify", "Remove"]}, dates=("A",))

    _sheet(wb, "Monitoring Log", ["Review month", "Review date", "Inputs reviewed for attack",
                                  "Outputs reviewed for attack", "Input filter test", "Output filter test",
                                  "Dataset integrity check", "Model integrity check", "AI code integrity check",
                                  "Config / metaprompt integrity check", "Anomalies found", "Tickets / incidents",
                                  "Reviewer"],
           [12, 13, 12, 12, 11, 11, 12, 12, 12, 14, 28, 18, 18], [],
           dropdowns={c: ["Done", "Not done", "N/A"] for c in "CDGHIJ"} | {"E": ["Pass", "Fail"], "F": ["Pass", "Fail"]},
           dates=("B",))

    bk = [[a, t, el] + [""] * 10 for a, t, el, c in tc.BACKUP_ASSETS if ctx.cond(c)]
    _sheet(wb, "Backup & Restore", ["AI asset", "Asset type", "Requirement element", "Backed up", "Backup method / tool",
                                    "Frequency", "Retention", "Location", "Encrypted", "Last successful backup",
                                    "Last restore test", "Restore result", "Owner"],
           [36, 14, 14, 10, 20, 12, 12, 20, 10, 14, 14, 14, 16], bk,
           dropdowns={"D": YN, "I": YN, "L": ["Pass", "Fail", "Not tested"]}, dates=("J", "K"))

    _sheet(wb, "Training", ["Person", "Role group", "Course", "Completion date", "Next due", "Evidence"],
           [24, 20, 34, 14, 14, 30], [],
           dropdowns={"B": ["Development", "Data science", "Cybersecurity", "Other"]}, dates=("D", "E"))

    rv = [[n, r, f, "", "", "", "", ""] for n, r, f, c in tc.REVIEWS if ctx.cond(c)]
    _sheet(wb, "Review Log", ["Recurring review", "Requirement", "Frequency", "Date performed", "Performed by",
                              "Result / changes", "Approved by", "Next due"],
           [42, 14, 26, 14, 18, 36, 18, 14], rv, dates=("D", "H"))
    wb.save(dest)


EVIDENCE_STATUS = ["Not requested", "Requested", "Received", "Reviewed - sufficient", "Reviewed - gap",
                   "N/A (tailored out)"]


def evidence(ctx, dest):
    wb = Workbook()
    rows = []
    for r in ctx.score["rows"]:
        req = ctx.reqs[r["id"]]
        ev, tmpl, who, test = tc.EVIDENCE[r["id"]]
        if not r["in_scope"]:
            scope, status = "Out – " + r["scope_reason"], "N/A (tailored out)"
        elif r["status"] == "N/A":
            scope, status = "N/A – " + r.get("na_reason", ""), "N/A (tailored out)"
        else:
            scope, status = "In", "Not requested"
        entry = ctx.data["requirements"].get(r["id"], {}) or {}
        rows.append([r["id"], req["hitrust_id"], req["title"], scope, req["inheritance"],
                     entry.get("provider") or "Customer", ev, tmpl, who, test, status, "", "",
                     r["status"].title() if r["status"] else "", ""])
    client = ctx.tokens()["client"]
    _sheet(wb, "Evidence Requests", ["Req", "HITRUST ID", "Requirement", "Scope", "Inheritable", "Responsibility",
                                     "Evidence to request", "Client template", "Interview", "Test / show-me",
                                     "Request status", "Requested", "Received", "Workbook status", "Assessor notes"],
           [8, 26, 34, 26, 11, 16, 44, 36, 22, 40, 18, 12, 12, 16, 36], rows, first=True,
           dropdowns={"K": EVIDENCE_STATUS}, dates=("L", "M"),
           note=f"{client} – HITRUST {ctx.level} evidence request list. Scope and Workbook status come from the "
                f"assessment workbook as of generation; regenerate after each sync.")

    ids = hl.cap_ids(ctx.data)
    cap_rows = []
    for r in ctx.score["cap_candidates"]:
        e = ctx.data["requirements"].get(r["id"], {}) or {}
        cap = e.get("cap", {}) or {}
        f = r.get("final", {}) or {}
        impl = f.get("implemented")
        cap_rows.append([ids.get(r["id"]), r["id"], r["title"], cap.get("weakness") or ", ".join(r.get("not_met", [])),
                         r["score"], hl.RATING_ABBR.get(impl, "") if impl is not None else "", "",
                         cap.get("remediation"), cap.get("poc"), cap.get("scheduled_completion"),
                         cap.get("status") or "Open", "", ""])
    _sheet(wb, "CAP Tracker", ["CAP ID", "Req", "Requirement", "Finding / weakness", "Est. score",
                               "Implemented rating", "Root cause", "Corrective action", "Owner", "Target date",
                               "Status", "Closure evidence", "Validated by"],
           [10, 8, 30, 40, 10, 12, 30, 40, 18, 13, 16, 30, 16], cap_rows,
           dropdowns={"F": ["NC", "SC", "PC", "MC", "FC"], "K": ["Open", "In progress", "Ready for validation", "Closed"]},
           dates=("J",),
           note=f"CAP candidates: score below {hl.CAP_LINE[ctx.level]} with Implemented below Fully compliant. "
                "HITRUST confirms the control-reference condition in MyCSF.")
    wb.save(dest)
