---
name: bankruptcy-credit-dispute
description: Turns a client's credit report(s) and bankruptcy papers into a ready-to-review dispute packet (one-issue-per-letter FCRA disputes to Equifax, Experian, TransUnion, and Innovis covering obsolete, inaccurate, duplicate, or mixed-file bankruptcy records and discharged accounts still reporting balances, plus furnisher direct disputes, file disclosure requests, a LexisNexis vendor dispute, an opt-in identity theft block, an analysis memo, and a deadline checklist), signed by an attorney or by the consumer, then drafts follow-up letters when a bureau says an item was "verified", never responds, or reinserts a deleted item. Use when the user provides credit reports and bankruptcy documents and wants the bankruptcy removed or corrected on the credit report, or shares a bureau's dispute results.
---

# Bankruptcy Credit Dispute Packet

Input: one or more credit reports (Equifax, Experian, TransUnion, Innovis, or a tri-merge) plus the bankruptcy papers (PDF, DOCX, HTML, TXT, or images). Later: the bureaus' dispute results.
Output: a case folder with one letter per issue per recipient (.md + .docx), an analysis memo, a client authorization form (attorney signer), a checklist, and follow-up letters when needed.

Paths used below:
- `SKILL_DIR`: the directory containing this `SKILL.md`
- `PY`: `<workspace>/.venv/bin/python`
- `CASE_DIR`: `<workspace>/bankruptcy-disputes/<client-slug>-<YYYY-MM-DD>`

Every legal citation the scripts emit is listed, with its primary source, in `$SKILL_DIR/references/citations.md`. Do not add a citation to a letter that is not in that table.

## Ground rules (non-negotiable)

1. **Assert only supported grounds.** An accurately reported bankruptcy may stay on the report for 10 years from the order for relief (15 U.S.C. § 1681c(a)(1)); Equifax, Experian, and TransUnion remove Chapter 13 cases 7 years after filing by policy, not by statute. If nothing is inaccurate, obsolete, or unverifiable, say so and give the expected removal date. Never invent a dispute.
2. **Never guess facts.** If a value is not in the documents, leave it out of `case.json` and ask. Identity mismatches, reaffirmed debts, and non-dischargeable debts go to attorney review, never automatically into a letter.
3. **Opt-in grounds only on explicit confirmation.** "Unverifiable" (`assert_unverifiable`), mixed file (`not_client_record_confirmed`), identity theft (`identity_theft_confirmed` plus `ftc_report_number`), and post-petition late payments (`assert_post_petition_lates`, a contested argument) are never asserted automatically.
4. **Minimize PII.** Record only the last 4 digits of SSNs and account numbers. Never commit or push case files to git unless the user explicitly asks.
5. Everything is a draft for review. Never claim that letters were sent.

## Steps

### 1. Intake
- Find the uploaded files (ask where they are if unclear) and copy them into `CASE_DIR/input/`.
- Ask who signs: the attorney (default) or the consumer (`signer: "consumer"`).
- Attorney signer: read `<workspace>/bankruptcy-disputes/attorney.json` if it exists. Otherwise ask once for name, firm, address, city/state/ZIP, phone, email, and bar number, then save that file for future cases. Consumer signer: no attorney details; ask for the client's phone and email if they want them on the letterhead.
- Ask for the planned mail date (default: today) and the client's state if not obvious.

### 2. Environment (first run only)
```bash
test -x <workspace>/.venv/bin/python || (python3 -m venv <workspace>/.venv && <workspace>/.venv/bin/pip install -q pypdf python-docx)
```

### 3. Extract text
```bash
$PY $SKILL_DIR/scripts/extract_text.py CASE_DIR/input --out CASE_DIR/text
```
Read every resulting `.txt`. For pages reported as "no text layer" and for image files, open them with your file-reading tool and read them visually. If a PDF is encrypted, ask for an unlocked copy.

### 4. Build `CASE_DIR/case.json`
Follow `$SKILL_DIR/references/case.example.json` exactly. Dates are `YYYY-MM-DD`.

| Field | Source document |
|---|---|
| `chapter`, `case_number`, `district`, `filing_date`, `debtor_name` | Voluntary Petition (Official Form 101), docket header, or Notice of Chapter X Case (Form 309). For voluntary cases the order-for-relief date is the petition date. |
| `disposition` (`discharged`/`dismissed`/`withdrawn`/`open`) + `disposition_date` | Order of Discharge (Form 318 for Ch 7, 3180W for Ch 13), Order of Dismissal, or docket |
| `scheduled_creditors[]` (name, last 4) | Schedules D and E/F, plus amended schedules |
| `excluded_from_discharge[]` | Reaffirmation agreements, adversary judgments, and typically non-dischargeable debts (student loans, recent taxes, domestic support, restitution). When unsure, list it here so it goes to review. |
| `credit_reports.<bureau>` | Keys `equifax`, `experian`, `transunion`, `innovis`. `report_source`: `annual_free` if the report was the free annual disclosure (45-day deadline), else `paid` or `other`. |
| `credit_reports.<bureau>.public_record` | "Public Records" section: name, SSN last 4, chapter, case #, filed date, status, status date, and `source` if a vendor such as LexisNexis is named. One object, a list (one entry per listing, so duplicates are caught), or `null` if no bankruptcy appears. |
| `credit_reports.<bureau>.tradelines[]` | Accounts matching scheduled creditors: creditor, account last 4, status, balance, past_due, date_opened, `furnisher_address` if printed; `original_creditor` for debt buyers; `date_of_first_delinquency` and `late_payments_after_petition` (`YYYY-MM` list) only if the report shows them |

For a tri-merge report, split the data by bureau. Include only bureaus whose data you actually have.

Before generating, show the user a short summary of the extracted facts and confirm anything ambiguous. Set these options only from the user's answer:
- `not_client_record_confirmed`: true only if the client confirms they never filed this case.
- `identity_theft_confirmed` + `ftc_report_number` (+ `identity_theft_accounts`): only if the client confirms identity theft and has filed an FTC Identity Theft Report.
- `assert_unverifiable`, `assert_post_petition_lates`: true only if the attorney wants that ground.
- `request_disclosure`: `true` (all five agencies) or a list such as `["innovis", "lexisnexis"]`. Missing Equifax/Experian/TransUnion reports get a disclosure letter automatically.
- `dispute_vendor`: true to dispute with LexisNexis even when no report names it as the source.
- `other_grounds`: specific extra inaccuracies, keyed by bureau.

### 5. Generate the packet
```bash
$PY $SKILL_DIR/scripts/generate_packet.py CASE_DIR/case.json --out CASE_DIR/packet
```
The script checks obsolescence (10 years from filing, 7 for Chapter 13; accounts 7 years from 180 days after first delinquency), compares each listing field by field against the court record, catches dismissed or withdrawn cases reported as something else and duplicate listings, and flags discharged tradelines still showing balances, the wrong status, or double counting by an original creditor and a debt buyer (skipping excluded and post-petition debts). One letter per issue, in `letters/`: `<bureau>-obsolete`, `<bureau>-public-record`, `<bureau>-discharged-accounts`, `<bureau>-identity-theft-block`, `<recipient>-file-disclosure`, `lexisnexis-vendor-dispute`, `furnisher-*`. It also writes `analysis.md`, `checklist.md`, and (attorney signer) `client-authorization`.

### 6. Verify, then report
- Read `analysis.md` and each letter. Confirm every ground matches the documents. Fix mismatches in `case.json` and rerun step 5; don't hand-edit letters.
- Tell the user, per bureau, what is disputed and why, or that the bankruptcy is accurately reported and when it should age off.
- List every "Needs attorney review" item, every reserve ground, and every generated file path.
- Remind the user of the manual steps in `checklist.md`: signatures, ID and proof of address, PACER exhibits, verifying every mailing address, certified mail, and deadlines.

### 7. Follow-up (when results arrive or the deadline passes)
Use this when the user shares a bureau's response letter or updated report, or asks what to do after no response.
- Read the response (step 3 extracts it). Add a `bureau_responses` section to the same `case.json` (format in the example file; keys may include `innovis` and `lexisnexis`): the original mail date and tracking number, the received date if known, `extended` (true if the client sent new info during the investigation), `response_date` (`null` if none), `procedure_described`, and a result per item (`verified`, `deleted`, `updated`, `no_response`, `reinserted` with `deleted_date`, `reinserted_date`, `reinsertion_notice_date`). Add `source` to an item when the response names the vendor that supplied it.
- Run:
```bash
$PY $SKILL_DIR/scripts/generate_followup.py CASE_DIR/case.json --out CASE_DIR/followup-<YYYY-MM-DD>
```
- It writes `letters/<bureau>-mov` (re-dispute plus a § 1681i(a)(7) procedure demand, a request for the record's source, and whether the enclosures were considered), `letters/<bureau>-no-response` (deletion demand once the 30- or 45-day period plus mailing time has passed), `letters/<bureau>-reinsertion` (reinsertion without written notice within 5 business days), and `letters/lexisnexis-vendor-dispute` when a response names LexisNexis. It also writes `followup-analysis.md` with next steps and new deadlines.
- Tell the user to attach **new evidence** to any re-dispute: a bureau may end a reinvestigation it reasonably determines is frivolous or irrelevant (§ 1681i(a)(3)), and a repeat dispute with nothing new invites that. Have the user fill in the `[Any NEW supporting evidence]` enclosure line.
- For updated items, pull a fresh report and confirm the data matches the court record. If the bureau already described its procedure and still won't correct the item, recommend evaluating an FCRA claim (due by the earlier of 2 years after discovery or 5 years after the violation, § 1681p) rather than another letter.
