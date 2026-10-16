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
          {"item": "public_record", "result": "verified"},
          {"item": "Capital Card Bank 9876", "result": "updated"}
        ]
      }
    }

item: "public_record" or "<creditor> <last4>" matching a disputed tradeline.
result: verified | deleted | updated | no_response

Writes per bureau:
    letters/<bureau>-mov.md|.docx         re-dispute + method-of-verification demand (verified items)
    letters/<bureau>-no-response.md|.docx demand for deletion (deadline passed, no results)
    followup-analysis.md                  what happened, what to do next, new deadlines
"""
import argparse
import json
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_packet import BUREAUS, analyze, d, fmt, header, norm, write  # noqa: E402

MAIL_DAYS = 5


def match_tradeline(label, tradelines):
    key = norm(label)
    return next((t for t in tradelines if norm(f"{t.get('creditor')}{t.get('account_last4')}") == key
                 or (norm(t.get("account_last4")) and key.endswith(norm(t.get("account_last4")))
                     and norm(t.get("creditor"))[:6] in key)), None)


def ref_block(case, bureau, resp, title):
    c, court = case["client"], case["bankruptcy_court_record"]
    rep = case["credit_reports"].get(bureau, {})
    name, l1, l2 = BUREAUS[bureau]
    return [name, l1, l2, "",
            f"**Re: {title}**  ",
            f"**Consumer:** {c['name']}  ",
            f"**Date of Birth:** {c.get('dob', '[DOB]')}  **SSN (last 4):** XXX-XX-{c.get('ssn_last4', '####')}  ",
            f"**Current Address:** {c['address']}  ",
            f"**Report/File No.:** {rep.get('report_number', '[n/a]')}  ",
            f"**Original Dispute:** mailed {fmt(d(resp.get('original_mail_date')))}, certified no. {resp.get('original_tracking', '[tracking #]')}  ",
            f"**Bankruptcy:** Chapter {court.get('chapter')}, Case No. {court.get('case_number')}, {court.get('district')}", "",
            "To Whom It May Concern:", ""]


def signature(case, enclosures):
    a, c = case["attorney"], case["client"]
    return ["Sincerely,", "", "", "______________________________", f"{a['name']}, Esq.  ", f"{a['firm']}  ",
            f"Counsel for {c['name']}", "", "**Enclosures:** " + "; ".join(enclosures), "", f"cc: {c['name']}"]


def mov_letter(case, bureau, resp, verified, letter_date):
    opts = case.get("options", {})
    L = header(case) + [fmt(letter_date), "", "**VIA CERTIFIED MAIL, RETURN RECEIPT REQUESTED. No. [tracking #]**", ""]
    L += ref_block(case, bureau, resp, "Second Dispute and Demand for Description of Reinvestigation Procedure")
    L += [f"On {fmt(d(resp.get('original_mail_date')))}, this office disputed inaccurate information in my client's file "
          f"(copy enclosed). Your response dated {fmt(d(resp.get('response_date')))} states that the following items were verified "
          "as accurate. My client continues to dispute them, for the reasons below, which your response does not address:", ""]
    for label, reasons in verified:
        L.append(f"**{label}**")
        L.append("")
        L += [f"- {r}" for r in reasons] or ["- See the enclosed original dispute."]
        L.append("")
    L += ["**Your reinvestigation was not reasonable.** Section 1681i(a)(4) requires you to review and consider all relevant "
          "information my client submitted. The enclosed court records directly contradict what you report. Merely confirming "
          "the data with the furnisher or a public-record vendor, without weighing those records, is not a reasonable "
          "reinvestigation under § 1681i(a)(1)(A) and does not meet your duty of maximum possible accuracy under § 1681e(b).", ""]
    if any(lbl == "Bankruptcy public record" for lbl, _ in verified):
        L += ["**Identify the source.** For the bankruptcy public record, identify by name, address, and telephone number the "
              "person or entity that verified it, and the date and method of that verification."
              + (" U.S. Bankruptcy Courts generally do not furnish data to, or verify data for, consumer reporting agencies. "
                 "If no reliable source verified this item, § 1681i(a)(5)(A) requires its deletion." if opts.get("assert_unverifiable") else ""), ""]
    L += ["**Requested Action**", "",
          "1. Under 15 U.S.C. § 1681i(a)(7), provide within **15 days** of receiving this request a description of the procedure "
          "used to determine the accuracy and completeness of each item above, including the business name, address, and "
          "telephone number of every furnisher contacted (§ 1681i(a)(6)(B)(iii)).",
          "2. Conduct a new reinvestigation that considers the enclosed records, and delete or correct each item listed above.",
          "3. Send my client written results and an updated copy of the consumer report.", "",
          "Willful or negligent noncompliance gives rise to civil liability under 15 U.S.C. §§ 1681n and 1681o. If these items are "
          "not corrected, my client intends to file a complaint with the Consumer Financial Protection Bureau and reserves all "
          "rights and remedies.", "",
          "Thank you for your prompt attention to this matter.", ""]
    L += signature(case, ["Copy of original dispute and certified mail receipt", "Your response letter",
                          "Client authorization, ID, proof of address", "Court docket and orders",
                          "[Any NEW supporting evidence: list it here]"])
    return "\n".join(L)


def no_response_letter(case, bureau, resp, received, deadline, items, letter_date):
    L = header(case) + [fmt(letter_date), "", "**VIA CERTIFIED MAIL, RETURN RECEIPT REQUESTED. No. [tracking #]**", ""]
    L += ref_block(case, bureau, resp, "Failure to Complete Reinvestigation: Demand for Deletion")
    L += [f"On {fmt(d(resp.get('original_mail_date')))}, this office disputed the items listed below (copy and certified mail "
          f"receipt enclosed). You received the dispute on or about {fmt(received)}. Under 15 U.S.C. § 1681i(a)(1)(A), you were "
          f"required to complete your reinvestigation by {fmt(deadline)}, and under § 1681i(a)(6)(A) to send my client written "
          "results within five business days afterward. As of the date of this letter, neither my client nor this office has "
          "received any results.", "",
          "Disputed items:", ""]
    L += [f"- {i}" for i in items] + [""]
    L += ["Information you have not verified within the statutory period cannot be treated as verified. Under § 1681i(a)(5)(A), "
          "you must promptly delete it or modify it to be accurate.", "",
          "**Requested Action**", "",
          "1. Immediately delete or correct each item listed above.",
          "2. Send my client written confirmation and an updated copy of the consumer report.",
          "3. Do not reinsert any deleted item without the certification and notice required by § 1681i(a)(5)(B).", "",
          "Your failure to comply with § 1681i gives rise to civil liability under 15 U.S.C. §§ 1681n and 1681o. My client intends "
          "to file a complaint with the Consumer Financial Protection Bureau and reserves all rights and remedies.", ""]
    L += signature(case, ["Copy of original dispute", "Certified mail receipt and return receipt (green card)",
                          "Client authorization, ID, proof of address"])
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
    from datetime import date
    today = d(args.today) or date.today()
    out = Path(args.out)
    (out / "letters").mkdir(parents=True, exist_ok=True)

    results, _ = analyze(case, today)
    A = [f"# Follow-up Analysis: {case['client']['name']}", "", f"_Generated {fmt(today)}. Attorney review required before mailing._", ""]
    deadlines, written = [], []

    for bureau, resp in responses.items():
        bureau = bureau.lower()
        if bureau not in BUREAUS:
            A += [f"## {bureau}", "- Unknown bureau, skipped.", ""]
            continue
        r = results.get(bureau, {"public_record": [], "tradelines": []})
        A.append(f"## {bureau.title()}")
        mailed = d(resp.get("original_mail_date"))
        if not mailed:
            A += ["- original_mail_date missing: cannot compute deadlines. Ask the user.", ""]
            continue
        received = d(resp.get("received_date")) or mailed + timedelta(days=MAIL_DAYS)
        deadline = received + timedelta(days=45 if resp.get("extended") else 30)
        A.append(f"- Dispute received {fmt(received)}" + ("" if resp.get("received_date") else " (estimated)") +
                 f"; reinvestigation deadline {fmt(deadline)}.")

        disputed = (["Bankruptcy public record"] if r["public_record"] else []) + \
                   [f"{t.get('creditor')}, account ending {t.get('account_last4')}" for t in r["tradelines"]]

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
            deadlines.append((f"{bureau.title()}: confirm deletion after no-response demand", today + timedelta(days=30)))
            continue

        A.append(f"- Response dated {fmt(d(resp['response_date']))}"
                 + (", procedure described." if resp.get("procedure_described") else ", no description of procedure."))
        verified = []
        for it in resp.get("items", []):
            label, res = it.get("item", ""), str(it.get("result", "")).lower()
            if label == "public_record":
                name, reasons = "Bankruptcy public record", [txt for _, txt in r["public_record"]]
            else:
                t = match_tradeline(label, r["tradelines"])
                name = f"{t.get('creditor')}, account ending {t.get('account_last4')}" if t else label
                reasons = ([f"Discharged in bankruptcy but still reports: {'; '.join(t['problems'])}."] if t else [])
            if res == "verified":
                verified.append((name, reasons))
                A.append(f"- {name}: **verified**. Re-disputed below." + ("" if reasons else
                         " (No ground found in the original analysis: confirm this item really is inaccurate before re-disputing.)"))
            elif res == "deleted":
                A.append(f"- {name}: deleted. Watch for reinsertion: the bureau must certify accuracy and notify the client within "
                         "5 business days of any reinsertion (§ 1681i(a)(5)(B)).")
            elif res == "updated":
                A.append(f"- {name}: updated. Pull a fresh report and confirm the new data matches the court record exactly.")
            elif res == "no_response":
                verified.append((name, reasons))
                A.append(f"- {name}: not addressed in the response. Included in the re-dispute.")
            else:
                A.append(f"- {name}: unknown result '{res}'. Check the response letter.")
        if verified:
            path = out / "letters" / f"{bureau}-mov.md"
            write(mov_letter(case, bureau, resp, verified, today), path)
            written.append(path.relative_to(out))
            A.append("- Wrote re-dispute + method-of-verification demand. **Attach new evidence** (certified docket, "
                     "discharge order, schedules): a repeat dispute with nothing new can be rejected as frivolous under § 1681i(a)(3).")
            if resp.get("procedure_described"):
                A.append("- The bureau already described its procedure. If the re-dispute fails, evaluate an FCRA claim rather "
                         "than another letter.")
            deadlines.append((f"{bureau.title()}: method-of-verification response due (15 days after receipt)",
                              today + timedelta(days=MAIL_DAYS + 15)))
            deadlines.append((f"{bureau.title()}: second reinvestigation due", today + timedelta(days=MAIL_DAYS + 30)))
        A.append("")

    A += ["## New deadlines", "", "| Event | Date |", "|---|---|"] + [f"| {e} | {fmt(dt)} |" for e, dt in deadlines] or []
    A += ["", "FCRA limitations period (§ 1681p): 2 years from discovery of the violation, no later than 5 years after it occurred.",
          "", "## Generated files", ""] + ([f"- {p}" for p in written] or ["- None"])
    (out / "followup-analysis.md").write_text("\n".join(A))
    print((out / "followup-analysis.md").read_text())


if __name__ == "__main__":
    main()
