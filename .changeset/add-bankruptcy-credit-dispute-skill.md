---
"mattpocock-skills": patch
---

Add the `bankruptcy-credit-dispute` skill (misc bucket, model-invoked). It reads a client's credit reports and bankruptcy papers, compares each bureau's reporting (Equifax, Experian, TransUnion, Innovis) against the court record, and drafts a dispute packet with one issue per letter: obsolete records and accounts, inaccurate, duplicate, or mixed-file public records, discharged accounts still showing balances, furnisher direct disputes, file disclosure requests, a LexisNexis vendor dispute, and an opt-in identity theft block. Letters can be signed by an attorney (with a client authorization) or by the consumer. Deadlines account for the 45-day period after a free annual disclosure. A follow-up script drafts method-of-verification, no-response, and reinsertion letters once results come back. Every citation is listed with its primary source in `references/citations.md`.
