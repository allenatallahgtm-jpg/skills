# Fictional example: Tallyport (B2B SaaS)

> **FICTIONAL.** Tallyport, its founders, customers, investors and every number below are invented to show the shape of a strong YC application. Read it for structure and tone only. Never copy a figure, name or claim from this file into a real application: a real one uses only the founder's real facts, with `[FOUNDER: ...]` placeholders for anything missing.

---

## Company

**Company name:** Tallyport

**Describe what your company does in 50 characters or less.**
Software that catches freight overcharges. *(42 characters)*

**Company URL:** tallyport.com

**What is your company going to make? Please describe your product and what it does or will do.**
Mid-size shippers (companies spending $5M–$200M a year on freight) get thousands of carrier invoices every month. Roughly 4–8% of freight spend is billed wrong: duplicate charges, accessorial fees nobody agreed to, wrong fuel surcharges, rates that don't match the contract. Today these companies either eat the loss or hire a freight audit firm that checks samples by hand and takes 30–50% of whatever it recovers.

Tallyport connects to a shipper's TMS, ERP and email inbox, pulls in every invoice (PDF, EDI 210 or portal export) and checks each line against the signed contract, the rate confirmation and the actual shipment data. When it finds an error, it files the dispute with the carrier automatically and tracks it until the money comes back. Customers pay a flat platform fee plus 10% of recovered dollars.

**Where do you live now, and where would the company be based after YC?**
San Francisco, CA / San Francisco, CA

---

## Founders

**Who writes code, or does other technical work on your product?**
Both founders. [Founder A] built the document extraction and contract-matching engine. [Founder B] built the integrations (NetSuite, SAP, MercuryGate, Oracle TMS) and the carrier dispute workflow. No non-founder has written product code.

**Are you looking for a cofounder?** No.

**Please tell us about an impressive thing each founder has built or achieved.**
- **[Founder A]:** As the 4th engineer at a logistics startup, built the pricing engine that quoted $1.2B in loads a year. Before that, placed top 50 in the ICPC World Finals.
- **[Founder B]:** Ran freight procurement for a $3B consumer goods company and personally recovered $2.1M in billing errors in one year using spreadsheets and email. That is the manual version of Tallyport.

**How long have the founders known one another and how did you meet?**
Six years. We met when [Founder B]'s company was [Founder A]'s startup's largest customer, and we worked together weekly for three years on rate integrations.

---

## Progress

**How far along are you?**
Live with paying customers. 9 shippers on annual contracts, 3 more in pilot.

**How long have each of you been working on this? How much of that has been full-time?**
Seven months, all of it full-time for both of us.

**What tech stack are you using?**
TypeScript/Node, Python for the extraction models, Postgres, Temporal for long-running dispute workflows, and fine-tuned open-weight models for invoice parsing (cheaper and more accurate than general LLM APIs on our documents). Hosted on AWS.

**Are people using your product?** Yes.

**How many active users or customers do you have? How many are paying?**
12 customers, 9 of them paying. Together they run about $410M a year of freight spend through Tallyport.

**Do you have revenue?** Yes.

**What is your monthly revenue?**
$38K MRR. Revenue has grown 31% month over month for the last four months. In that time we have recovered $1.9M for customers, and 62% of it came from error types their previous audit firm never flagged.

**If you are applying with the same idea as a previous batch, did anything change?** N/A

**If you have already participated or committed to participate in an incubator, accelerator or pre-accelerator program, please tell us about it.** None.

---

## Idea

**Why did you pick this idea to work on? Do you have domain expertise? How do you know people need what you're making?**
[Founder B] did this job by hand. At a $3B company, one person working part-time with spreadsheets found $2.1M of errors in a year. That was only the easy cases, and only about 15% of invoices got checked. Every procurement lead we called had the same problem and no good tool for it.

Our evidence: 9 of our first 11 pilots turned into paid contracts, the median pilot paid for a year of the platform fee within 30 days, and 3 of our customers came from referrals by other customers.

**Why now?**
1. Models can now reliably read messy, unstructured carrier invoices and 40-page rate contracts. Two years ago this needed a person.
2. Carriers have moved to portals and APIs, so disputes can be filed automatically instead of over the phone.

**Who are your competitors? What do you understand about your business that they don't?**
- **Legacy freight audit firms** (Cass, nVision and others): services businesses that charge high contingency fees, sample invoices and catch mostly duplicates. Their margins depend on cheap manual labor, so automation works against their own business model.
- **TMS add-on modules**: they check whether the invoice matches the quote, not whether it matches the contract, and they stop at flagging. They don't file the dispute or get the money back.
- **Spreadsheets and doing nothing**: the most common option today.

What we understand: finding the error is only half the job. The value is in **actually getting the money back**. Carriers ignore disputes that are badly documented. Ours include the contract clause, the rate confirmation and the shipment data, and 87% of them get paid. Every dispute that's won or lost also teaches us more about how each carrier behaves, and that dataset gets better with every customer.

**How do or will you make money? How much could you make?**
A platform fee of $1.5K–$8K a month, depending on invoice volume, plus 10% of recovered dollars. Average contract value today is about $50K a year.

About 25,000 US companies spend more than $5M a year on freight. At $50K average contract value, that's a $1.25B opportunity in US mid-market shippers alone, before enterprise accounts, international freight, or adding payment automation (paying carriers through us), which would roughly triple revenue per customer.

**What are the biggest risks, and how are you handling them?**
- *A TMS vendor adds contract auditing:* their products are built to plan shipments, not to win disputes, and we integrate with them, so customers keep both.
- *Carriers push back on automated disputes:* every dispute carries its evidence, and 87% get paid; badly documented disputes are the ones carriers ignore.
- *Recovery shrinks as billing improves:* the platform fee carries the business on its own, and payment automation is the next product.

**Which category best applies to your company?** B2B SaaS / Supply Chain & Logistics

**If you had any other ideas you considered applying with, please list them.**
Automated customs classification for small importers. We may come back to it, since it uses the same document-intelligence core.

---

## Equity

**Have you formed ANY legal entity yet?** Yes, a Delaware C-Corp.

**Please list all legal entities you have and in what state or country each was formed.** Tallyport, Inc. (Delaware)

**Please describe the breakdown of the equity ownership in percentages among the founders, employees and any other stockholders.**
[Founder A] 50%, [Founder B] 50%. Four-year vesting with a one-year cliff for both founders.

**Have you taken any investment yet?**
$250K on a post-money SAFE at a $10M cap from two angels (former logistics executives).

**Are you currently fundraising?** No.

---

## Curious

**What convinced you to apply to Y Combinator?**
Three YC founders we respect said the batch forced them to focus on growth week by week. We also sell to companies that buy from other YC companies, and we want that network.

**How did you hear about Y Combinator?** Hacker News, and a referral from a founder in the W24 batch.

---

## Founder video script (1 minute, both founders on camera)

> **[A]:** Hi, I'm [Founder A], I write the code.
> **[B]:** And I'm [Founder B]. I used to run freight procurement at a $3B company.
> **[A]:** We're building Tallyport. Mid-size shippers get overbilled 4 to 8 percent on freight, and nobody catches it.
> **[B]:** I found $2.1M in errors by hand in one year, and that was only 15% of the invoices.
> **[A]:** Tallyport reads every invoice, checks it against the contract and files the dispute automatically.
> **[B]:** We have 9 paying customers, $38K in monthly revenue growing 31% a month, and we've recovered $1.9M so far.
> **[A]:** We've known each other six years. We're both full-time and both technical.
> **[B]:** Thanks for watching.

One take, no editing or music, and look at the camera.

---

## Why this example is strong

- **The one-liner says what the product does, not the vision.** A reader understands it in 5 seconds.
- **Concrete numbers everywhere:** MRR, growth rate, dollars recovered, pilot-to-paid conversion.
- **Founders who fit the problem:** one has done the job by hand, the other has built similar systems.
- **A clear why now** and a specific insight competitors can't easily copy.
- **Plain language with no buzzwords**, and every answer is as short as it can be.
