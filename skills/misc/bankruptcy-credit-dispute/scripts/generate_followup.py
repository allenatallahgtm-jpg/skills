#!/usr/bin/env python3
"""Second-round letters after a bureau answers (or ignores) the first dispute.

Usage:
    python generate_followup.py <case.json> --out <dir> [--today YYYY-MM-DD]

Reads case.json (same file used by generate_packet.py) plus a
"bureau_responses" section (see ../references/case.example.json):

    "bureau_responses": {
      "equifax": {
        "original_mail_date": "2026-10-20",
        "received_date": "2026-10-24",          optional, else mail date + 5 days
        "extended": false,                      true if client sent new info (45-day period)
        "response_date": "2026-11-15",          null if no response yet
        "procedure_described": false,           did the response describe HOW it verified?
        "items": [
          {"item": "public_record", "result": "verified", "source": "LexisNexis Risk Solutions"},
          {"item": "Capital Card Bank 9876", "result": "reinserted", "deleted_date": "2026-11-15",
           "reinserted_date": "2026-12-01", "reinsertion_notice_date": null}
        ]
      }
    }

Keys may be equifax, experian, transunion, innovis, or lexisnexis.
item: "public_record" or "<creditor> <last4>" matching a disputed tradeline.
result: verified | deleted | updated | no_response | reinserted
The reinvestigation period is 45 days when the bureau's report_source is
"annual_free" or "extended" is true, else 30 (see generate_packet.reinvestigation_days).

Writes per recipient:
    letters/<bureau>-mov.md|.docx          re-dispute + method-of-verification demand (verified items)
    letters/<bureau>-no-response.md|.docx  demand for deletion (deadline passed, no results)
    letters/<bureau>-reinsertion.md|.docx  reinsertion without timely notice
    letters/lexisnexis-vendor-dispute      when a response names LexisNexis as the source
    followup-analysis.md                   what happened, what to do next, new deadlines
"""
import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_packet import (MAIL_DAYS, RECIPIENTS, add_business_days, analyze, address_block, d,  # noqa: E402
                             deadline_basis, fmt, is_lexis, letterhead, mail_line, name_of, norm, reinvestigation_days,
                             signature_block, signer, v, vendor_grounds, vendor_letter, write)


def match_tradeline(label, tradelines):
    key = norm(label)
    return next((t for t in tradelines if norm(f"{t.get('creditor')}{t.get('account_last4')}") == key
                 or (norm(t.get("account_last4")) and key.endswith(norm(t.get("account_last4")))
                     and norm(t.get("creditor"))[:6] in key)), None)


def ref_block(case, bureau, resp, title):
    c, court = case["client"], case["bankruptcy_court_record"]
    rep = case.get("credit_reports", {}).get(bureau) or {}
    return address_block(bureau) + [
        f"**Re: {title}**  ",
        f"**Consumer:** {c['name']}  ",
        f"**Date of Birth:** {c.get('dob', '[DOB]')}  **SSN (last 4):** XXX-XX-{c.get('ssn_last4', '####')}  ",
        f"**Current Address:** {c['address']}  ",
        f"**Report/File No.:** {rep.get('report_number', '[n/a]')}  ",
        f"**Original Dispute:** mailed {fmt(d(resp.get('original_mail_date')))}, certified no. {resp.get('original_tracking', '[tracking #]')}  ",
        f"**Bankruptcy:** Chapter {court.get('chapter')}, Case No. {court.get('case_number')}, {court.get('district')}", "",
        "To Whom It May Concern:", ""]


def start(case, letter_date):
    return letterhead(case) + [fmt(letter_date), ""] + mail_line()


def remedies(case):
    return ["Willful or negligent noncompliance gives rise to civil liability under 15 U.S.C. §§ 1681n and 1681o. "
            + v(case, "My client intends", "I intend") + " to file a complaint with the Consumer Financial Protection Bureau and "
            + v(case, "reserves", "reserve") + " all rights and remedies.", "", "Thank you for your prompt attention to this matter.", ""]


def mov_letter(case, bureau, resp, verified, letter_date):
    opts = case.get("options", {})
    L = start(case, letter_date) + ref_block(case, bureau, resp, "Second Dispute and Demand for Description of Reinvestigation Procedure")
    L += [f"On {fmt(d(resp.get('original_mail_date')))}, " + v(case, "this office disputed inaccurate information in my client's file",
                                                                 "I disputed inaccurate information in my file") +
          f" (copy enclosed). Your response dated {fmt(d(resp.get('response_date')))} states that the following items were verified "
          "as accurate or does not address them. " + v(case, "My client continues", "I continue") +
          " to dispute them, for the reasons below:", ""]
    for label, reasons in verified:
        L.append(f"**{label}**")
        L.append("")
        L += [f"- {r}" for r in reasons] or ["- See the enclosed original dispute."]
        L.append("")
    L += ["**Your reinvestigation was not reasonable.** 15 U.S.C. § 1681i(a)(4) requires you to review and consider all relevant "
          "information " + v(case, "my client", "I") + " submitted. The enclosed court records directly contradict what you report. "
          "Merely confirming the data with the furnisher or a public-record vendor, without weighing those records, is not a "
          "reasonable reinvestigation under 15 U.S.C. § 1681i(a)(1)(A) and does not meet your duty of maximum possible accuracy under "
          "15 U.S.C. § 1681e(b).", ""]
    has_pr = any(lbl == "Bankruptcy public record" for lbl, _ in verified)
    if has_pr and opts.get("assert_unverifiable"):
        L += ["**Unverifiable source.** U.S. Bankruptcy Courts generally do not furnish data to, or verify data for, consumer "
              "reporting agencies. If no reliable source verified this item, 15 U.S.C. § 1681i(a)(5)(A) requires its deletion.", ""]
    who = v(case, "my client", "me")
    L += ["**Requested Action**", "",
          "1. Under 15 U.S.C. § 1681i(a)(7), provide within **15 days** of receiving this request a description of the procedure "
          "used to determine the accuracy and completeness of each item above, including the business name and address of any "
          "furnisher of information contacted and its telephone number, if reasonably available (15 U.S.C. § 1681i(a)(6)(B)(iii))."]
    n = 2
    if has_pr:
        L.append(f"{n}. Identify the source of the bankruptcy public record (the court, PACER, or a public-records vendor, and if a "
                 "vendor, its name and address), as 15 U.S.C. § 1681g(a)(2) requires you to disclose the sources of information in "
                 + v(case, "my client's", "my") + " file.")
        n += 1
    L += [f"{n}. State whether the court documents enclosed with the original dispute were reviewed and considered, as required by "
          "15 U.S.C. § 1681i(a)(4), and the date the reinvestigation was completed.",
          f"{n+1}. Conduct a new reinvestigation that considers the enclosed records, and delete or correct each item listed above "
          "(15 U.S.C. § 1681i(a)(5)(A)).",
          f"{n+2}. Send {who} written results and an updated copy of the consumer report.", ""]
    L += remedies(case)
    L += signature_block(case, ["Copy of original dispute and certified mail receipt", "Your response letter",
                                v(case, "Client authorization, ", "") + "ID, proof of address", "Court docket and orders",
                                "[Any NEW supporting evidence: list it here]"])
    return "\n".join(L)


def no_response_letter(case, bureau, resp, received, deadline, items, letter_date):
    n = (deadline - received).days
    L = start(case, letter_date) + ref_block(case, bureau, resp, "Failure to Complete Reinvestigation: Demand for Deletion")
    L += [f"On {fmt(d(resp.get('original_mail_date')))}, " + v(case, "this office", "I") + " disputed the items listed below (copy and "
          f"certified mail receipt enclosed). You received the dispute on or about {fmt(received)}. Under "
          f"{deadline_basis(case, bureau, resp.get('extended'))}, you were required to complete your reinvestigation within {n} days, "
          f"by {fmt(deadline)}, and under 15 U.S.C. § 1681i(a)(6)(A) to send written results within five business days afterward. "
          "As of the date of this letter, " + v(case, "neither my client nor this office has", "I have not") + " received any results.", "",
          "Disputed items:", ""]
    L += [f"- {i}" for i in items] + [""]
    L += ["Information you have not verified within the statutory period cannot be treated as verified. Under 15 U.S.C. "
          "§ 1681i(a)(5)(A), information that is inaccurate or incomplete or cannot be verified must be promptly deleted or modified.", "",
          "**Requested Action**", "",
          "1. Immediately delete or correct each item listed above.",
          f"2. Send {v(case, 'my client', 'me')} written confirmation and an updated copy of the consumer report.",
          "3. Do not reinsert any deleted item without the certification and notice required by 15 U.S.C. § 1681i(a)(5)(B).", ""]
    L += remedies(case)
    L += signature_block(case, ["Copy of original dispute", "Certified mail receipt and return receipt (green card)",
                                v(case, "Client authorization, ", "") + "ID, proof of address"])
    return "\n".join(L)


def reinsertion_letter(case, bureau, resp, items, letter_date):
    L = start(case, letter_date) + ref_block(case, bureau, resp, "Reinsertion of Deleted Information Without Required Notice")
    L += [f"On {fmt(d(resp.get('original_mail_date')))}, " + v(case, "this office disputed", "I disputed") +
          " the items below, and you deleted them. You later reinserted them:", ""]
    for label, it in items:
        notice = d(it.get("reinsertion_notice_date"))
        L.append(f"- {label}: deleted {fmt(d(it.get('deleted_date')))}; reinserted {fmt(d(it.get('reinserted_date')))}; "
                 + (f"written notice dated {fmt(notice)}, more than five business days after reinsertion." if notice else
                    "no written notice of reinsertion received."))
    L += ["", "Under 15 U.S.C. § 1681i(a)(5)(B)(i), deleted information may not be reinserted unless the furnisher certifies that it is "
          "complete and accurate. Under 15 U.S.C. § 1681i(a)(5)(B)(ii) and (iii), you must notify the consumer in writing of a "
          "reinsertion not later than five business days after it, including the business name and address of any furnisher "
          "contacted and a notice of the right to add a statement to the file. That notice was not given on time.", "",
          "**Requested Action**", "",
          "1. Delete each reinserted item.",
          "2. Identify the furnisher that certified each item as complete and accurate, and the date of that certification.",
          f"3. Send {v(case, 'my client', 'me')} written confirmation and an updated copy of the consumer report.", ""]
    L += remedies(case)
    L += signature_block(case, ["Copy of original dispute and certified mail receipt", "Your deletion notice",
                                "Credit report showing the reinserted items", v(case, "Client authorization, ", "") + "ID, proof of address"])
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("case")
    ap.add_argument("--out", required=True)
    ap.add_argument("--today")
    args = ap.parse_args()
    case = json.loads(Path(args.case).read_text())
    responses = case.get("bureau_responses")
    if not responses:
        sys.exit("case.json has no bureau_responses section. See references/case.example.json.")
    if signer(case) not in ("attorney", "consumer"):
        sys.exit("case.json signer must be \"attorney\" or \"consumer\".")
    if signer(case) == "attorney" and "attorney" not in case:
        sys.exit("case.json missing required section: attorney")
    today = d(args.today) or date.today()
    out = Path(args.out)
    (out / "letters").mkdir(parents=True, exist_ok=True)

    results, _ = analyze(case, today)
    empty = {"obsolete": [], "obsolete_tradelines": [], "public_record": [], "reserve": [], "tradelines": [], "records": []}
    A = [f"# Follow-up Analysis: {case['client']['name']}", "", f"_Generated {fmt(today)}. " + v(case, "Attorney review required before mailing._", "Review every statement before mailing._"), ""]
    deadlines, written, vendor_hits = [], [], []

    for bureau, resp in responses.items():
        bureau = bureau.lower()
        if bureau not in RECIPIENTS:
            A += [f"## {bureau}", "- Unknown bureau, skipped.", ""]
            continue
        r = results.get(bureau, empty)
        A.append(f"## {name_of(bureau)}")
        mailed = d(resp.get("original_mail_date"))
        if not mailed:
            A += ["- original_mail_date missing: cannot compute deadlines. Ask the user.", ""]
            continue
        received = d(resp.get("received_date")) or mailed + timedelta(days=MAIL_DAYS)
        days = reinvestigation_days(case, bureau, resp.get("extended"))
        deadline = received + timedelta(days=days)
        A.append(f"- Dispute received {fmt(received)}" + ("" if resp.get("received_date") else " (estimated)") +
                 f"; reinvestigation deadline {fmt(deadline)} ({days} days under {deadline_basis(case, bureau, resp.get('extended'))}).")

        pr_reasons = [txt for _, txt in r["obsolete"] + r["public_record"] + r["reserve"]]
        if bureau == "lexisnexis":
            pr_reasons = [txt for _, txt in vendor_grounds(results)]
        tls = r["tradelines"] + r["obsolete_tradelines"]
        disputed = (["Bankruptcy public record"] if pr_reasons else []) + \
                   [f"{t.get('creditor')}, account ending {t.get('account_last4')}" for t in tls]

        if not resp.get("response_date"):
            if today <= deadline + timedelta(days=7):
                A += [f"- No response yet, but the deadline plus results-mailing time has not clearly passed. "
                      f"Re-check after {fmt(deadline + timedelta(days=8))}.", ""]
                continue
            path = out / "letters" / f"{bureau}-no-response.md"
            write(no_response_letter(case, bureau, resp, received, deadline, disputed or ["[items from original dispute]"], today), path)
            written.append(path.relative_to(out))
            A += [f"- **No response** {(today - deadline).days} days after the deadline. Wrote demand for deletion.",
                  "- Strong FCRA claim candidate: keep the certified mail receipt and green card.", ""]
            deadlines.append((f"{name_of(bureau)}: confirm deletion after no-response demand", today + timedelta(days=30)))
            continue

        A.append(f"- Response dated {fmt(d(resp['response_date']))}"
                 + (", procedure described." if resp.get("procedure_described") else ", no description of procedure."))
        verified, reinserted = [], []
        for it in resp.get("items", []):
            label, res = it.get("item", ""), str(it.get("result", "")).lower()
            if label == "public_record":
                name, reasons = "Bankruptcy public record", pr_reasons
            else:
                t = match_tradeline(label, tls)
                name = f"{t.get('creditor')}, account ending {t.get('account_last4')}" if t else label
                if t and t.get("problems"):
                    reasons = [f"Discharged in bankruptcy but still reports: {'; '.join(t['problems'])}."]
                elif t:
                    reasons = [f"Obsolete: the seven-year period under 15 U.S.C. § 1681c(a)(4)-(5) and (c)(1) ended {fmt(t['expires'])}."]
                else:
                    reasons = []
            if is_lexis(it.get("source")) and bureau != "lexisnexis":
                vendor_hits.append((bureau, it.get("source")))
                A.append(f"- {name}: response names {it.get('source')} as the source. See the vendor dispute below.")
            if res == "verified":
                verified.append((name, reasons))
                A.append(f"- {name}: **verified**. Re-disputed below." + ("" if reasons else
                         " (No ground found in the original analysis: confirm this item really is inaccurate before re-disputing.)"))
            elif res == "deleted":
                A.append(f"- {name}: deleted. Watch for reinsertion: the bureau needs the furnisher's certification and must notify "
                         "the consumer in writing within 5 business days of any reinsertion (15 U.S.C. § 1681i(a)(5)(B)).")
            elif res == "updated":
                A.append(f"- {name}: updated. Pull a fresh report and confirm the new data matches the court record exactly.")
            elif res == "no_response":
                verified.append((name, reasons))
                A.append(f"- {name}: not addressed in the response. Included in the re-dispute.")
            elif res == "reinserted":
                ins, notice = d(it.get("reinserted_date")), d(it.get("reinsertion_notice_date"))
                if not ins:
                    A.append(f"- {name}: reinserted, but reinserted_date is missing: ask the user before writing a letter.")
                elif notice and notice <= add_business_days(ins, 5):
                    A.append(f"- {name}: reinserted {fmt(ins)} with written notice dated {fmt(notice)}, within 5 business days. "
                             "No reinsertion letter. If the item is still inaccurate, re-dispute it with new evidence.")
                elif not notice and today <= add_business_days(ins, 5) + timedelta(days=MAIL_DAYS):
                    # The 5-business-day notice period (plus mail time) has not run, so late notice cannot be asserted yet.
                    recheck = add_business_days(ins, 5) + timedelta(days=MAIL_DAYS + 1)
                    A.append(f"- {name}: reinserted {fmt(ins)}; the 5-business-day written notice period (plus mail time) has "
                             f"not run. No reinsertion letter yet. Re-check on {fmt(recheck)}: if no notice has arrived, "
                             "rerun the follow-up.")
                    deadlines.append((f"{name_of(bureau)}: re-check for reinsertion notice ({name})", recheck))
                else:
                    reinserted.append((name, it))
                    A.append(f"- {name}: reinserted {fmt(ins)} " + (f"with late notice dated {fmt(notice)}." if notice else
                             "with no written notice.") + " Wrote reinsertion demand.")
            else:
                A.append(f"- {name}: unknown result '{res}'. Check the response letter.")
        if verified:
            path = out / "letters" / f"{bureau}-mov.md"
            write(mov_letter(case, bureau, resp, verified, today), path)
            written.append(path.relative_to(out))
            A.append("- Wrote re-dispute + method-of-verification demand. **Attach new evidence** (certified docket, "
                     "discharge order, schedules): a bureau may end a reinvestigation it reasonably determines is frivolous or "
                     "irrelevant (§ 1681i(a)(3)), and a repeat dispute with nothing new invites that response.")
            if resp.get("procedure_described"):
                A.append("- The bureau already described its procedure. If the re-dispute fails, evaluate an FCRA claim rather "
                         "than another letter.")
            deadlines.append((f"{name_of(bureau)}: method-of-verification response due (15 days after receipt, § 1681i(a)(7))",
                              today + timedelta(days=MAIL_DAYS + 15)))
            deadlines.append((f"{name_of(bureau)}: second reinvestigation due ({reinvestigation_days(case, bureau)} days after receipt)",
                              today + timedelta(days=MAIL_DAYS + reinvestigation_days(case, bureau))))
        if reinserted:
            path = out / "letters" / f"{bureau}-reinsertion.md"
            write(reinsertion_letter(case, bureau, resp, reinserted, today), path)
            written.append(path.relative_to(out))
            A.append("- File a CFPB complaint with the reinsertion letter; reinsertion without notice is an FCRA claim candidate.")
        A.append("")

    if vendor_hits and "lexisnexis" not in {b.lower() for b in responses}:
        vg = vendor_grounds(results, {b for b, _ in vendor_hits} | {b for b, r in results.items() if r.get("vendor_source")})
        if vg:
            b0, src = vendor_hits[0]
            note = v(case, f"{name_of(b0)} identified your company ({src}) as the source of the bankruptcy record in my client's file.",
                     f"{name_of(b0)} identified your company ({src}) as the source of the bankruptcy record in my file.")
            path = out / "letters" / "lexisnexis-vendor-dispute.md"
            write(vendor_letter(case, vg, today, note), path)
            written.append(path.relative_to(out))
            A += ["## LexisNexis Risk Solutions", "- A bureau named LexisNexis as its source. Wrote vendor dispute.", ""]
            deadlines.append(("LexisNexis: reinvestigation due (30 days after receipt)", today + timedelta(days=MAIL_DAYS + 30)))
        else:
            A += ["## LexisNexis Risk Solutions", "- A bureau named LexisNexis as its source, but no public-record ground applies: "
                  "no vendor letter.", ""]

    A += ["## New deadlines", "", "| Event | Date |", "|---|---|"] + [f"| {e} | {fmt(dt)} |" for e, dt in deadlines]
    A += ["", "FCRA limitations period (§ 1681p): the earlier of 2 years after discovery of the violation or 5 years after it occurred.",
          "", "## Generated files", ""] + ([f"- {p}" for p in written] or ["- None"])
    (out / "followup-analysis.md").write_text("\n".join(A))
    print((out / "followup-analysis.md").read_text())


if __name__ == "__main__":
    main()
