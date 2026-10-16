# Intake

Gather the founder's real facts in two rounds, then write the fact sheet. Mine any material the founder already gave you before asking anything, and drop every question it answers.

## Round 1: everything at once

Send the questions below in a single message, numbered and grouped under their headings. Open with one line: "Answer what you can, skip what you can't. Anything you skip becomes a marked gap in the draft, never a guess." Leave out any question already answered.

**Company**

1. Company name and URL.
2. In one plain sentence: what does the product do, and for whom?
3. Who pays for it, and who uses it day to day (if different)?
4. Where do the founders live now, and where would the company be based after YC?

**Founders** (per founder)

5. Name, role, and whether they write code or do other technical work on the product.
6. Full-time since when? If not full-time yet, when, and what is the blocker?
7. The most impressive thing they have built or achieved, with a number if there is one.
8. Their direct experience with this problem or this industry.
9. How long the founders have known each other, and how they met.
10. Are you looking for a cofounder?

**Progress**

11. Stage: idea, building, launched, or revenue? Launch date if launched.
12. Users: how many active (and how you define active), how many paying.
13. Revenue: current MRR, and MRR for each of the last 3 to 6 months.
14. Retention or churn, pilots run and how many converted to paid.
15. The customer outcome you can prove, as a before and after ("response time went from X to Y").
16. Customers you may name in the application, and where customers came from (referrals, outbound, inbound).
17. Tech stack, including any AI models and how you use them.

**Idea and market**

18. Why this idea? How do you know people need it (interviews, waitlist, LOIs, usage)?
19. Why now: what changed recently that makes this possible or urgent?
20. Competitors and substitutes, including "doing nothing" and spreadsheets.
21. What do you understand about this market that competitors don't?
22. Pricing, average contract or order value, and how you would size the market.
23. The biggest risks to the company, and what you are doing about each.
24. Other ideas you considered applying with.

**Equity and history**

25. Legal entity: formed? Type and state or country.
26. Equity split among founders and anyone else, and vesting terms.
27. Investment taken: amount, instrument (SAFE, priced round), cap or valuation, and from whom.
28. Fundraising now? Any incubator or accelerator, past or committed? Applied to YC before, and what changed since?
29. Why YC, who encouraged you to apply, and how you heard about it.

## Round 2: only the gaps that matter

After Round 1, send one follow-up message covering, at most, ten items:

- **Vague answers turned into numbers.** "A lot of users" becomes "how many weekly active users today?"; "growing fast" becomes "MRR three months ago and today?"
- **Gaps in the answers partners read first**: the one-liner inputs, who writes code, traction, founder-market fit, why now.
- **Contradictions** between answers (two different MRR figures, a full-time date that doesn't match the time worked).

Then draft. Whatever is still missing stays a placeholder; never block the draft on it.

## The fact sheet

Open the output file with the fact sheet. It is the single source of truth: every number in the application must trace to a row.

```markdown
## Fact sheet

| Fact | Value | Source |
| --- | --- | --- |
| MRR | $12K (March); $7K (December) | Founder, Round 1 |
| MoM growth | 19% a month, compounded December to March | Arithmetic on the MRR row |
| Paying customers | [FOUNDER: number of paying customers today] | Missing |
| Target customers in the US | [FOUNDER: count of target companies, with its source] | Missing |
```

Placeholders always use the form `[FOUNDER: <exactly what is needed>]`, specific enough that the founder can answer it in one line.
