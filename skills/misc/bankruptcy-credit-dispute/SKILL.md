---
name: bankruptcy-credit-dispute
description: Turns a client's credit report(s) and bankruptcy papers into a ready-to-review attorney dispute packet (per-bureau FCRA dispute letters, furnisher letters for discharged debts still reporting balances, client authorization, analysis memo, deadline checklist), then drafts follow-up letters when a bureau says an item was "verified" or never responds. Use when the user provides credit reports and bankruptcy documents and wants the bankruptcy removed or corrected on the credit report, or shares a bureau's dispute results.
---

# Bankruptcy Credit Dispute Packet

Input: one or more credit reports (Equifax, Experian, TransUnion, or a tri-merge) plus the bankruptcy papers (PDF, DOCX, HTML, TXT, or images). Later: the bureaus' dispute results.
Output: a case folder with dispute letters (.md + .docx), an analysis memo, a client authorization form, a checklist, and follow-up letters when needed.

Paths used below:
- `SKILL_DIR`: the directory containing this `SKILL.md`
- `PY`: `<workspace>/.venv/bin/python`
- `CASE_DIR`: `<workspace>/bankruptcy-disputes/<client-slug>-<YYYY-MM-DD>`

## Ground rules (non-negotiable)

1. **Assert only supported grounds.** An accurately reported bankruptcy may stay on the report for 10 years (15 U.S.C. § 1681c(a)(1)), and bureaus remove Chapter 13 cases after 7 years by policy. If nothing is inaccurate, obsolete, or unverifiable, say so and give the expected removal date. Never invent a dispute.
2. **Never guess facts.** If a value is not in the documents, leave it out of `case.json` and ask. Identity mismatches, reaffirmed debts, and non-dischargeable debts go to attorney review, never automatically into a letter.
3. **Assert "unverifiable" only when the attorney asks for it** (`options.assert_unverifiable`).
4. **Minimize PII.** Record only the last 4 digits of SSNs and account numbers. Never commit or push case files to git unless the user explicitly asks.
5. Everything is a draft for attorney review. Never claim that letters were sent.

## Steps

### 1. Intake
- Find the uploaded files (ask where they are if unclear) and copy them into `CASE_DIR/input/`.
- Attorney details: read `<workspace>/bankruptcy-disputes/attorney.json` if it exists. Otherwise ask once for name, firm, address, city/state/ZIP, phone, email, and bar number, then save that file for future cases.
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
| `credit_reports.<bureau>.public_record` | "Public Records" section: name, SSN last 4, chapter, case #, filed date, status, status date. `null` if no bankruptcy appears. |
| `credit_reports.<bureau>.tradelines[]` | Accounts matching scheduled creditors: creditor, account last 4, status, balance, past_due, date_opened, and `furnisher_address` if printed |

For a tri-merge report, split the data by bureau. Include only bureaus whose data you actually have.

Before generating, show the user a short summary of the extracted facts and confirm anything ambiguous. Set these options only from the user's answer:
- `not_client_record_confirmed`: true only if the client confirms they never filed this case.
- `assert_unverifiable`: true only if the attorney wants that ground.
- `other_grounds`: specific extra inaccuracies, keyed by bureau.

### 5. Generate the packet
```bash
$PY $SKILL_DIR/scripts/generate_packet.py CASE_DIR/case.json --out CASE_DIR/packet
```
The script checks obsolescence (10 years from filing, 7 for Chapter 13), compares each report field by field against the court record, catches dismissed or withdrawn cases reported as something else, and flags discharged tradelines still showing balances or the wrong status (skipping excluded and post-petition debts). It writes `analysis.md`, `letters/<bureau>`, `letters/furnisher-*`, `client-authorization`, and `checklist.md` (letters and authorization as both .md and .docx).

### 6. Verify, then report
- Read `analysis.md` and each letter. Confirm every ground matches the documents. Fix mismatches in `case.json` and rerun step 5; don't hand-edit letters.
- Tell the user, per bureau, what is disputed and why, or that the bankruptcy is accurately reported and when it should age off.
- List every "Needs attorney review" item and every generated file path.
- Remind the user of the manual steps in `checklist.md`: client signature, ID and proof of address, PACER exhibits, certified mail, and deadlines.

### 7. Follow-up (when results arrive or the deadline passes)
Use this when the user shares a bureau's response letter or updated report, or asks what to do after no response.
- Read the response (step 3 extracts it). Add a `bureau_responses` section to the same `case.json` (format in the example file): the original mail date and tracking number, the received date if known, `extended` (true if the client sent new info during the investigation), `response_date` (`null` if none), `procedure_described`, and a result per item (`verified`, `deleted`, `updated`, `no_response`).
- Run:
```bash
$PY $SKILL_DIR/scripts/generate_followup.py CASE_DIR/case.json --out CASE_DIR/followup-<YYYY-MM-DD>
```
- It writes `letters/<bureau>-mov.md|.docx` (re-dispute plus a § 1681i(a)(7) demand for the verification procedure) for verified or unaddressed items. It writes `letters/<bureau>-no-response.md|.docx` (demand for deletion under § 1681i(a)(5)(A)) when the 30/45-day period plus mailing time has passed with no results. It also writes `followup-analysis.md` with next steps and new deadlines.
- Tell the user to attach **new evidence** to any re-dispute, because a bureau may reject a repeat dispute with nothing new as frivolous (§ 1681i(a)(3)). Have the user fill in the `[Any NEW supporting evidence]` enclosure line.
- For deleted items, remind the user to watch for reinsertion (§ 1681i(a)(5)(B)). For updated items, pull a fresh report and confirm the data matches the court record. If the bureau already described its procedure and still won't correct the item, recommend evaluating an FCRA claim (2-year limitations period, § 1681p) rather than another letter.
