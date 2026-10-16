#!/usr/bin/env python3
"""Analyze a bankruptcy case file against credit reports and build the dispute packet.

Usage:
    python generate_packet.py <case.json> --out <dir> [--today YYYY-MM-DD]

Input format: see ../references/case.example.json
Outputs (in --out):
    analysis.md                  findings, grounds, items needing attorney review
    letters/<bureau>.md|.docx    one dispute letter per bureau that has grounds
    letters/furnisher-*.md|.docx direct disputes to creditors (15 U.S.C. 1681s-2(b))
    client-authorization.md|.docx
    checklist.md                 mailing checklist + response deadlines
Only grounds supported by the data are asserted. Anything uncertain is listed
under "Needs attorney review" and is NOT put in a letter.
"""
import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

BUREAUS = {
    "equifax": ("Equifax Information Services LLC", "P.O. Box 740256", "Atlanta, GA 30374"),
    "experian": ("Experian", "P.O. Box 4500", "Allen, TX 75013"),
    "transunion": ("TransUnion LLC, Consumer Dispute Center", "P.O. Box 2000", "Chester, PA 19016"),
}
BK_STATUS_WORDS = ("bankrupt", "discharg", "chapter", "ch 7", "ch 13", "included")


# ---------------------------------------------------------------- helpers
def d(s):
    return date.fromisoformat(s) if s else None


def add_years(dt, n):
    try:
        return dt.replace(year=dt.year + n)
    except ValueError:  # Feb 29
        return dt.replace(year=dt.year + n, day=28)


def norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s or "").lower())


def norm_case(s):
    # "2:15-bk-12345-ABC" vs "15-12345" -> compare year+number core
    digits = re.findall(r"\d+", str(s or ""))
    digits = [x for x in digits if len(x) >= 2]
    if len(digits) >= 2:
        return digits[-2][-2:] + digits[-1].lstrip("0")
    return norm(s)


def norm_status(s):
    s = norm(s)
    for key in ("dismiss", "withdraw", "discharg", "open", "filed", "closed"):
        if key in s:
            return {"withdraw": "withdrawn", "dismiss": "dismissed", "discharg": "discharged"}.get(key, key)
    return s


def money(v):
    try:
        return float(str(v).replace("$", "").replace(",", "") or 0)
    except ValueError:
        return 0.0


def fmt(dt):
    return dt.strftime("%B %-d, %Y") if dt else "[date]"


# ---------------------------------------------------------------- analysis
def analyze(case, today):
    court = case["bankruptcy_court_record"]
    client = case["client"]
    opts = case.get("options", {})
    chapter = str(court.get("chapter", "")).strip()
    filed = d(court.get("filing_date"))
    disposition = norm_status(court.get("disposition"))
    disp_date = d(court.get("disposition_date"))

    excluded = {(norm(x.get("account_last4")), norm(x.get("creditor"))): x for x in court.get("excluded_from_discharge", [])}
    scheduled = court.get("scheduled_creditors", [])

    results, review = {}, []
    if not filed:
        review.append("Court filing date missing - cannot evaluate obsolescence. Get the petition / docket from PACER.")

    for bureau, rep in case.get("credit_reports", {}).items():
        bureau = bureau.lower()
        if bureau not in BUREAUS:
            review.append(f"Unknown bureau '{bureau}' skipped.")
            continue
        r = {"public_record": [], "tradelines": [], "notes": []}
        pr = rep.get("public_record")

        if pr:
            # Obsolete (statutory)
            if filed and today >= add_years(filed, 10):
                r["public_record"].append(
                    ("obsolete", f"**Obsolete information.** The order for relief was entered on {fmt(filed)}, more than ten years ago. "
                     "Under 15 U.S.C. § 1681c(a)(1), this item may no longer be reported."))
            # Chapter 13 seven-year policy
            elif chapter == "13" and filed and today >= add_years(filed, 7) and opts.get("include_chapter13_policy", True):
                r["public_record"].append(
                    ("ch13_policy", f"**Chapter 13 reporting period expired.** This Chapter 13 case was filed on {fmt(filed)}, more than seven years ago. "
                     "Consistent with your published practice of removing Chapter 13 bankruptcies seven years from the filing date, please delete it."))

            # Field-by-field accuracy
            mism = []
            if pr.get("chapter") and chapter and norm(pr["chapter"]) != norm(chapter):
                mism.append(f"chapter (reported: {pr['chapter']}; court record: {chapter})")
            if pr.get("case_number") and court.get("case_number") and norm_case(pr["case_number"]) != norm_case(court["case_number"]):
                mism.append(f"case number (reported: {pr['case_number']}; court record: {court['case_number']})")
            if pr.get("filing_date") and filed and d(pr["filing_date"]) != filed:
                mism.append(f"filing date (reported: {fmt(d(pr['filing_date']))}; court record: {fmt(filed)})")
            if pr.get("status_date") and disp_date and d(pr["status_date"]) != disp_date:
                mism.append(f"{disposition or 'status'} date (reported: {fmt(d(pr['status_date']))}; court record: {fmt(disp_date)})")
            rep_status = norm_status(pr.get("status"))
            if rep_status and disposition and rep_status != disposition and not (rep_status == "closed" and disposition == "discharged"):
                if disposition in ("dismissed", "withdrawn"):
                    r["public_record"].append(
                        ("disposition", f"**{disposition.title()} case reported incorrectly.** The court record shows the case was {disposition} on {fmt(disp_date)}, "
                         f"but it is reported as \"{pr.get('status')}\"."))
                else:
                    mism.append(f"status (reported: {pr.get('status')}; court record: {disposition} on {fmt(disp_date)})")
            if mism:
                r["public_record"].append(
                    ("inaccurate", "**Inaccurate case details.** The record misstates the " + "; ".join(mism) +
                     ". The certified court records are enclosed as Exhibit B."))

            # Identity mismatch -> review unless attorney confirmed
            id_issue = []
            if pr.get("ssn_last4") and norm(pr["ssn_last4"]) != norm(client.get("ssn_last4")):
                id_issue.append(f"SSN last 4 on record ({pr['ssn_last4']}) does not match client")
            names = [norm(client.get("name"))] + [norm(a) for a in client.get("aliases", [])]
            if pr.get("name") and norm(pr["name"]) not in names:
                id_issue.append(f"name on record ('{pr['name']}') does not match client or aliases")
            if court.get("debtor_name") and norm(court["debtor_name"]) not in names:
                id_issue.append(f"court debtor name ('{court['debtor_name']}') does not match client - confirm this is the client's case")
            if id_issue:
                if opts.get("not_client_record_confirmed"):
                    r["public_record"].append(
                        ("not_client", "**Not my client's record.** My client did not file the bankruptcy reported. "
                         "This appears to be a mixed-file or identity error: " + "; ".join(id_issue) + "."))
                else:
                    review.append(f"{bureau.title()}: possible mixed file - " + "; ".join(id_issue) +
                                  ". Set options.not_client_record_confirmed=true only if the client confirms they never filed.")

            if opts.get("assert_unverifiable"):
                r["public_record"].append(
                    ("unverifiable", "**Unverifiable source.** U.S. Bankruptcy Courts generally do not furnish data to, or verify data for, "
                     "consumer reporting agencies. If you cannot verify this item through a reliable source, "
                     "15 U.S.C. § 1681i(a)(5)(A) requires its prompt deletion."))

            for other in opts.get("other_grounds", {}).get(bureau, []):
                r["public_record"].append(("other", f"**Other.** {other}"))

        # Tradelines included in the bankruptcy
        if disposition == "discharged":
            for t in rep.get("tradelines", []):
                key_acct, key_name = norm(t.get("account_last4")), norm(t.get("creditor"))
                match = next((s for s in scheduled if
                              (key_acct and norm(s.get("account_last4")) == key_acct) or
                              (key_name and (norm(s.get("name")) in key_name or key_name in norm(s.get("name"))))), None)
                if not match:
                    continue
                excl = next((v for (a, n), v in excluded.items() if (a and a == key_acct) or (n and n in key_name)), None)
                if excl:
                    review.append(f"{bureau.title()}: {t.get('creditor')} …{t.get('account_last4')} is excluded/reaffirmed "
                                  f"({excl.get('reason', 'see schedule')}) - not disputed automatically.")
                    continue
                opened = d(t.get("date_opened"))
                if opened and filed and opened > filed:
                    review.append(f"{bureau.title()}: {t.get('creditor')} …{t.get('account_last4')} opened after the petition date - likely post-petition debt, not disputed.")
                    continue
                problems = []
                if money(t.get("balance")) > 0:
                    problems.append(f"balance of ${money(t['balance']):,.2f}")
                if money(t.get("past_due")) > 0:
                    problems.append(f"past-due amount of ${money(t['past_due']):,.2f}")
                if not any(w in str(t.get("status", "")).lower() for w in BK_STATUS_WORDS):
                    problems.append(f"status \"{t.get('status')}\" instead of \"Discharged in Bankruptcy\"")
                if problems:
                    r["tradelines"].append({**t, "problems": problems})
        elif rep.get("tradelines") and disposition in ("open", "filed"):
            r["notes"].append("Case not yet discharged - tradelines not evaluated.")

        if pr and not r["public_record"]:
            keep_until = add_years(filed, 7 if chapter == "13" else 10) if filed else None
            r["notes"].append("Bankruptcy appears ACCURATELY reported - no good-faith ground to dispute it" +
                              (f"; expected to age off around {fmt(keep_until)}." if keep_until else "."))
        results[bureau] = r
    return results, review


# ---------------------------------------------------------------- rendering
def header(case):
    a = case["attorney"]
    return [f"**{a['firm']}**", f"{a['address']} · {a['city_state_zip']}",
            f"{a['phone']} · {a['email']} · Bar No. {a.get('bar', '[____]')}", ""]


def bureau_letter(case, bureau, r, letter_date):
    c, court, a = case["client"], case["bankruptcy_court_record"], case["attorney"]
    rep = case["credit_reports"][bureau]
    name, l1, l2 = BUREAUS[bureau]
    L = header(case) + [fmt(letter_date), "", "**VIA CERTIFIED MAIL, RETURN RECEIPT REQUESTED. No. [tracking #]**", "",
                        name, l1, l2, "",
                        "**Re: Formal Dispute: Bankruptcy Public Record and Related Accounts**",
                        f"**Consumer:** {c['name']}  ",
                        f"**Date of Birth:** {c.get('dob', '[DOB]')}  **SSN (last 4):** XXX-XX-{c.get('ssn_last4', '####')}  ",
                        f"**Current Address:** {c['address']}  ",
                        f"**Report/File No.:** {rep.get('report_number', '[n/a]')}  ",
                        f"**Item Disputed:** Chapter {court.get('chapter')} Bankruptcy, Case No. {court.get('case_number')}, "
                        f"U.S. Bankruptcy Court, {court.get('district', '[District]')}", "",
                        "To Whom It May Concern:", "",
                        f"This firm represents {c['name']} (\"my client\"). My client's signed authorization, a copy of government-issued "
                        "identification, and proof of address are enclosed as **Exhibit A**. Please send all correspondence about this dispute "
                        "to my client and to this office.", "",
                        "Pursuant to the Fair Credit Reporting Act (\"FCRA\"), 15 U.S.C. § 1681i, my client disputes the following information "
                        "in their consumer file:", ""]
    if r["public_record"]:
        L.append("**A. Bankruptcy Public Record**")
        L.append("")
        L += [f"- {text}" for _, text in r["public_record"]]
        L.append("")
    if r["tradelines"]:
        L.append("**B. Accounts Discharged in Bankruptcy but Reported Inaccurately**")
        L.append("")
        L.append(f"The following accounts were scheduled in the bankruptcy and discharged by order entered "
                 f"{fmt(d(court.get('disposition_date')))} (Exhibit C). Each must report a $0 balance, no past-due amount, and a status of "
                 "\"Discharged in Bankruptcy\":")
        L.append("")
        L += [f"- {t.get('creditor')}, account ending {t.get('account_last4')}: currently shows " + "; ".join(t["problems"]) + "."
              for t in r["tradelines"]]
        L.append("")
    must_delete = any(k in ("obsolete", "ch13_policy", "not_client", "unverifiable") for k, _ in r["public_record"])
    actions = []
    if r["public_record"]:
        actions.append("**Delete** the bankruptcy public record from my client's file." if must_delete else
                       "**Correct** the bankruptcy public record to match the enclosed court records, or delete it if it cannot be verified.")
    if r["tradelines"]:
        actions.append("**Update** each listed account to a $0 balance, $0 past due, status \"Discharged in Bankruptcy.\"")
    L += ["**Requested Action**", "",
          "1. Conduct a reasonable reinvestigation within **30 days** of receipt, as required by 15 U.S.C. § 1681i(a)(1)."]
    L += [f"{i}. {x}" for i, x in enumerate(actions, 2)]
    n = len(actions) + 2
    L += [f"{n}. Send my client written results and an updated copy of the consumer report, as required by § 1681i(a)(6).",
          f"{n+1}. If any item is verified, provide a description of the procedure used, including the name, address, and telephone "
          "number of every furnisher or source contacted, as required by §§ 1681i(a)(6)(B)(iii) and 1681i(a)(7).",
          f"{n+2}. Do not reinsert any deleted item without complying with § 1681i(a)(5)(B).", "",
          "You are required to maintain reasonable procedures to assure maximum possible accuracy (15 U.S.C. § 1681e(b)). "
          "Willful or negligent noncompliance gives rise to civil liability under 15 U.S.C. §§ 1681n and 1681o. My client reserves "
          f"all rights and remedies, including complaints to the Consumer Financial Protection Bureau and the {case.get('state', '[State]')} "
          "Attorney General.", "",
          "Thank you for your prompt attention to this matter.", "", "Sincerely,", "", "", "______________________________",
          f"{a['name']}, Esq.  ", f"{a['firm']}  ", f"Counsel for {c['name']}", "",
          "**Enclosures:** Exhibit A: Client Authorization, ID, proof of address; Exhibit B: Court docket/records; "
          + ("Exhibit C: Discharge Order; " if court.get("disposition", "").lower().startswith("discharg") else "")
          + "Exhibit D: Credit report with disputed items highlighted", "",
          f"cc: {c['name']}"]
    return "\n".join(L)


def furnisher_letter(case, creditor, items, letter_date):
    c, court, a = case["client"], case["bankruptcy_court_record"], case["attorney"]
    addr = items[0].get("furnisher_address") or "[Furnisher dispute address from credit report]"
    bureaus = ", ".join(sorted({i["_bureau"].title() for i in items}))
    probs = sorted({p for i in items for p in i["problems"]})
    L = header(case) + [fmt(letter_date), "", "**VIA CERTIFIED MAIL, RETURN RECEIPT REQUESTED. No. [tracking #]**", "",
                        creditor, *addr.split("\n"), "",
                        f"**Re: Direct Dispute: Account ending {items[0].get('account_last4')}, Discharged in Bankruptcy**  ",
                        f"**Consumer:** {c['name']}, SSN last 4: {c.get('ssn_last4')}  ",
                        f"**Bankruptcy:** Chapter {court.get('chapter')}, Case No. {court.get('case_number')}, {court.get('district')}; "
                        f"discharged {fmt(d(court.get('disposition_date')))}", "",
                        "To Whom It May Concern:", "",
                        f"This firm represents {c['name']}. This account was scheduled in the above bankruptcy and the debt was discharged "
                        "(Discharge Order enclosed). You continue to report it to " + bureaus + " with: " + "; ".join(probs) + ".", "",
                        "Please investigate and correct your reporting to a $0 balance, $0 past due, and \"Discharged in Bankruptcy\" status, and "
                        "notify every consumer reporting agency to which you furnished this account, as required by 15 U.S.C. § 1681s-2. "
                        "Any attempt to collect this discharged debt violates the discharge injunction, 11 U.S.C. § 524(a)(2).", "",
                        "Sincerely,", "", "", "______________________________", f"{a['name']}, Esq.  ", a["firm"], "",
                        "**Enclosures:** Client authorization; Discharge Order; Schedule listing this account; Credit report excerpt"]
    return "\n".join(L)


def authorization(case):
    c, a = case["client"], case["attorney"]
    return "\n".join(["# Client Authorization to Dispute Credit Information", "",
                      f"I, **{c['name']}**, DOB {c.get('dob', '[DOB]')}, SSN last 4 {c.get('ssn_last4', '[####]')}, residing at {c['address']}, "
                      f"authorize **{a['name']}, Esq.** and **{a['firm']}** to act on my behalf in disputing information in my consumer files "
                      "with Equifax, Experian, TransUnion, and any furnisher of information, and to receive information about those disputes. "
                      "I confirm that, to the best of my knowledge, the statements in the enclosed disputes are true and correct.", "", "",
                      "______________________________  Date: ____________  ", c["name"]])


def to_docx(md_text, path):
    try:
        import docx
        from docx.shared import Pt
    except ImportError:
        return False
    doc = docx.Document()
    doc.styles["Normal"].font.name = "Times New Roman"
    doc.styles["Normal"].font.size = Pt(12)
    for line in md_text.split("\n"):
        line = line.rstrip()
        if line.startswith("# "):
            doc.add_heading(line[2:], level=1)
            continue
        style = None
        if line.startswith("- "):
            line, style = line[2:], "List Bullet"
        p = doc.add_paragraph(style=style)
        p.paragraph_format.space_after = Pt(0 if not line else 4)
        for i, chunk in enumerate(re.split(r"\*\*", line)):
            if chunk:
                p.add_run(chunk).bold = i % 2 == 1
    doc.save(str(path))
    return True


def write(md, path):
    path.write_text(md)
    return to_docx(md, path.with_suffix(".docx"))


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("case")
    ap.add_argument("--out", required=True)
    ap.add_argument("--today")
    args = ap.parse_args()
    case = json.loads(Path(args.case).read_text())
    for k in ("attorney", "client", "bankruptcy_court_record", "credit_reports"):
        if k not in case:
            sys.exit(f"case.json missing required section: {k}")
    today = d(args.today) or date.today()
    mail = d(case.get("mail_date")) or today
    out = Path(args.out)
    (out / "letters").mkdir(parents=True, exist_ok=True)

    results, review = analyze(case, today)
    docx_ok = True
    letters = []
    furnishers = {}
    for bureau, r in results.items():
        if r["public_record"] or r["tradelines"]:
            docx_ok &= write(bureau_letter(case, bureau, r, mail), out / "letters" / f"{bureau}.md")
            letters.append(bureau)
        for t in r["tradelines"]:
            furnishers.setdefault((t.get("creditor"), t.get("account_last4")), []).append({**t, "_bureau": bureau})
    for (cred, acct), items in furnishers.items():
        slug = re.sub(r"[^a-z0-9]+", "-", str(cred).lower()).strip("-")
        docx_ok &= write(furnisher_letter(case, cred, items, mail), out / "letters" / f"furnisher-{slug}-{acct}.md")
    if letters or furnishers:
        docx_ok &= write(authorization(case), out / "client-authorization.md")

    # analysis report
    court = case["bankruptcy_court_record"]
    A = [f"# Dispute Analysis: {case['client']['name']}", "", f"_Generated {fmt(today)}. Attorney review required before mailing._", "",
         f"**Court record:** Chapter {court.get('chapter')}, Case {court.get('case_number')}, {court.get('district')}; "
         f"filed {fmt(d(court.get('filing_date')))}; {court.get('disposition')} {fmt(d(court.get('disposition_date')))}", ""]
    for bureau, r in results.items():
        A.append(f"## {bureau.title()}")
        A += [f"- Public record ground ({k}): {t}" for k, t in r["public_record"]] or []
        A += [f"- Tradeline: {t.get('creditor')} …{t.get('account_last4')}: " + "; ".join(t["problems"]) for t in r["tradelines"]]
        A += [f"- Note: {n}" for n in r["notes"]]
        if not (r["public_record"] or r["tradelines"] or r["notes"]):
            A.append("- No bankruptcy items found on this report.")
        A.append("")
    A += ["## Needs attorney review (not included in any letter)", ""] + ([f"- {x}" for x in review] or ["- None"])
    A += ["", "## Generated files", ""] + [f"- letters/{b}.md" for b in letters] + \
         [f"- letters/furnisher-{re.sub(r'[^a-z0-9]+', '-', str(c).lower()).strip('-')}-{a}.md" for c, a in furnishers] + \
         (["- client-authorization.md"] if letters or furnishers else ["- (no letters: nothing to dispute in good faith)"])
    (out / "analysis.md").write_text("\n".join(A))

    # checklist
    C = ["# Mailing Checklist & Deadlines", "", f"Planned mail date: **{fmt(mail)}**", "",
         "- [ ] Attorney reviewed analysis.md and every letter",
         "- [ ] Client signed client-authorization; attach ID + proof of address (Exhibit A)",
         "- [ ] Attach PACER docket / court records (Exhibit B) and discharge or dismissal order (Exhibit C)",
         "- [ ] Highlight disputed items on each credit report (Exhibit D)",
         "- [ ] Verify current bureau dispute addresses; fill in furnisher addresses",
         "- [ ] Send certified mail, return receipt; record tracking numbers", "",
         "| Deadline | Date |", "|---|---|",
         f"| Bureau reinvestigation due (≈30 days after receipt, assume 5 days mail) | {fmt(mail + timedelta(days=35))} |",
         f"| Extended deadline if client sends new info (45 days) | {fmt(mail + timedelta(days=50))} |",
         f"| Results notice due (5 business days after completion) | ≈{fmt(mail + timedelta(days=42))} |",
         f"| Pull fresh reports to confirm corrections | {fmt(mail + timedelta(days=60))} |",
         "", "If an item is verified without a description of the procedure, or no response arrives: send the follow-up/method-of-verification "
         "demand, file a CFPB complaint, and evaluate FCRA claims (§§ 1681n/1681o; 2-year limitations period from discovery, § 1681p)."]
    (out / "checklist.md").write_text("\n".join(C))

    print((out / "analysis.md").read_text())
    if not docx_ok:
        print("\n(note: python-docx not installed - only .md files written)")


if __name__ == "__main__":
    main()
