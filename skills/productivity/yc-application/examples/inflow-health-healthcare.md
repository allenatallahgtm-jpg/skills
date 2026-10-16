# Fictional example: Inflow Health (healthcare)

> **FICTIONAL.** Inflow Health, its founders, customers, investors and every number below are invented to show the shape of a strong healthcare YC application. Read it for structure and tone only. Never copy a figure, name or claim from this file into a real application: a real one uses only the founder's real facts, with `[FOUNDER: ...]` placeholders for anything missing.

---

## Why this idea wins

Most healthcare applications lose for predictable reasons: slow sales to big hospital systems, FDA risk, no clear buyer, or only cutting costs for someone who doesn't care about cost. This example avoids all of those:

| What YC partners worry about in healthcare | How this idea answers it |
|---|---|
| "Hospitals take 18 months to buy" | It sells to owner-run home health agencies, which can sign in 2–3 weeks |
| "FDA / clinical liability" | It handles paperwork only and never makes clinical decisions. A nurse approves every admission |
| "Who pays and why?" | The agency pays, because the product **brings in new patients**. That's new revenue, not a cost saving |
| "Can you prove it works?" | The result shows up in weeks: more admissions per month |
| "Isn't this crowded?" | AI for billing and prior authorization is crowded. Intake for post-acute care (home health, hospice, nursing facilities) mostly isn't |
| "Why you?" | One founder ran intake at her family's agency; the other built document AI |

---

## Company

**Company name:** Inflow Health

**Describe what your company does in 50 characters or less.**
AI that helps home health agencies win referrals. *(49 characters)*

**Company URL:** inflowhealth.com

**What is your company going to make? Please describe your product and what it does or will do.**
When a hospital discharges a patient who needs care at home, a discharge planner faxes a 30–100 page referral packet to several home health agencies at once. Whichever agency says yes first usually gets the patient. Today an intake coordinator reads each packet by hand, checks the patient's insurance, checks that the agency has a nurse available in the patient's zip code and the right clinical skills, then calls back. That takes hours. By then the patient has often gone to another agency.

Inflow reads each referral as soon as it arrives by fax, email or a hospital referral portal. It pulls out the diagnoses, medications, orders and insurance, checks eligibility in real time, matches the patient against nurse schedules in the agency's medical-records system, and gives the intake nurse a one-screen summary: accept or decline, with the reasons. The nurse approves with one click, and Inflow sends the acceptance back and creates the patient chart.

Our customers' median time to respond to a referral went from 4.5 hours to 11 minutes, and they admit 22% more of the referrals they receive.

**Where do you live now, and where would the company be based after YC?**
San Francisco, CA / San Francisco, CA

---

## Founders

**Who writes code, or does other technical work on your product?**
Both founders. [Founder A] built the document-reading and summarization pipeline. [Founder B] built the integrations with the agencies' medical-records systems (HCHB, WellSky, Axxess) and the real-time eligibility checks. No non-founder has written product code.

**Are you looking for a cofounder?** No.

**Please tell us about an impressive thing each founder has built or achieved.**
- **[Founder A]:** Tech lead for document extraction at a lending startup. Built the system that processed 2M+ loan files a year and cut manual review by 70%. Previously did ML research on reading handwritten forms.
- **[Founder B]:** Ran intake for her family's home health agency for three years while studying CS. Rebuilt their intake process, which took the agency from 140 to 310 patients without hiring another intake coordinator. Inflow is the software version of what she did there.

**How long have the founders known one another and how did you meet?**
Eight years. We were roommates in college, built two hackathon projects together, and have talked about starting this company since [Founder B]'s time at the agency.

---

## Progress

**How far along are you?**
Live in production. 14 agencies are paying, across 31 branch offices in 6 states. 4 more agencies are in pilots.

**How long have each of you been working on this? How much of that has been full-time?**
Eight months, all of it full-time for both of us.

**What tech stack are you using?**
TypeScript and Python. A fine-tuned open-weight vision-language model reads the faxed pages; it beats general-purpose model APIs on cost and accuracy for these documents, and patient data never leaves our own setup. We use Postgres and Temporal (for long-running intake workflows), and connect to insurers' eligibility systems through a clearinghouse. Everything runs on AWS under HIPAA terms: we have a Business Associate Agreement (BAA) with AWS, every customer signs one with us, and our SOC 2 Type II audit window is in progress.

**Are people using your product?** Yes.

**How many active users or customers do you have? How many are paying?**
18 agencies, 14 of them paying. About 220 intake staff use Inflow every day, and it processed 9,400 referrals last month.

**Do you have revenue?** Yes.

**What is your monthly revenue?**
$46K MRR, up from $9K four months ago (about 50% month over month). Revenue retention is 100%+ because agencies add more branches after the first one. All 14 paying customers converted from pilots, and 5 came from referrals by other agency owners.

**If you have already participated or committed to participate in an incubator, accelerator or pre-accelerator program, please tell us about it.** None.

---

## Idea

**Why did you pick this idea to work on? Do you have domain expertise? How do you know people need what you're making?**
[Founder B] did this job. At her family's agency, referrals came in by fax at 4:55pm, and if nobody called back by morning the patient went somewhere else. She estimated they lost a third of good referrals just to speed. Every agency owner we've talked to (over 120 of them) says the same thing: intake is where they lose revenue, and intake coordinators are hard to hire and quick to burn out.

The proof is in the numbers. In a home health agency, one admitted patient brings in several thousand dollars in Medicare payments. An agency that admits even 10 more patients a month earns far more than Inflow costs. Our median customer earned back a year of fees within the first 6 weeks.

**Why now?**
1. Until recently, software couldn't reliably read low-quality faxes with handwritten orders. Current vision models can. Our field-level accuracy is 97.8%, measured against nurse-checked packets.
2. There is a severe shortage of home health staff, so agencies can't hire their way out of the problem.
3. As the population ages and hospitals discharge patients sooner, the volume of referrals keeps growing.

**Who are your competitors? What do you understand about your business that they don't?**
- **Medical-records vendors** (WellSky, HCHB, Axxess): they store the referral after a person has typed it in, so they start too late in the process. We integrate with them rather than compete.
- **Document workflow tools** (e.g. Forcura): they route and organize faxes but leave people to read and decide.
- **Hospital-side referral platforms** (e.g. CarePort): they help the hospital send referrals, not the agency win them.
- **Outsourced intake teams overseas**: cheaper staff, but they aren't faster.

What we understand: **in home health, intake is a race, not a paperwork task.** Competitors sell it as efficiency. We sell more patients and measure it in admissions. And every referral we process teaches us which hospitals, diagnoses and insurers lead to admissions and profitable episodes of care. That data becomes the basis for the bigger opportunity: becoming the routing layer between hospitals and post-acute providers.

**How do or will you make money? How much could you make?**
We charge a platform fee per branch office ($1.5K–$4K a month) based on referral volume. The average contract today is about $40K a year per agency.

The US has about 11,000 Medicare-certified home health agencies and nearly 6,000 hospices. Skilled nursing facilities, medical equipment suppliers and home infusion providers take referrals the same way. That's over 30,000 potential customers, or a $1B+ software market. The larger opportunity is the routing layer: hospitals want their patients placed fast, and post-acute providers want the right patients. We'd sit in the middle and process both sides.

**What are the biggest risks, and how are you handling them?**
- *Privacy and HIPAA:* every customer signs a BAA with us, we have one with AWS, patient data stays in our own environment, and our SOC 2 Type II audit window is in progress.
- *Clinical liability:* Inflow recommends, a licensed nurse decides, and every decision is logged.
- *Sales cycle:* we sell to owner-run agencies, not hospital systems. Our median time from first call to signed contract is 19 days.
- *Medical-records vendors building this themselves:* they've had 20 years and are built for documentation, not speed. We're also an integration partner, which makes their systems more valuable.
- *Medicare payment changes:* agencies need more patients whenever payment rates tighten, so our value grows when margins shrink.

**Which category best applies to your company?** Healthcare / B2B SaaS

**If you had any other ideas you considered applying with, please list them.**
Automated prior authorization for infusion centers. We decided against it as a first product because the space is crowded and it depends on insurers' timelines.

---

## Equity

**Have you formed ANY legal entity yet?** Yes, a Delaware C-Corp.

**Please list all legal entities you have and in what state or country each was formed.** Inflow Health, Inc. (Delaware)

**Please describe the breakdown of the equity ownership in percentages among the founders, employees and any other stockholders.**
[Founder A] 50%, [Founder B] 50%. Four-year vesting with a one-year cliff for both founders.

**Have you taken any investment yet?**
$300K on a post-money SAFE at a $12M cap from three angels: two former home health executives and one YC alum.

**Are you currently fundraising?** No.

---

## Curious

**What convinced you to apply to Y Combinator?**
Healthcare companies die from slow sales cycles. YC's weekly focus on growth is the opposite of how healthcare normally works, and that's the habit we want. Healthcare founders from YC have also told us the network opens doors with health system partners.

**How did you hear about Y Combinator?** Hacker News, and a referral from a founder in a recent healthcare batch.

---

## Founder video script (1 minute, both founders on camera)

> **[B]:** I'm [Founder B]. I ran intake at my family's home health agency.
> **[A]:** I'm [Founder A]. I built document AI that processed millions of loan files.
> **[B]:** When a hospital discharges a patient, it faxes a referral to five agencies. The first one to say yes gets the patient. Most agencies take hours.
> **[A]:** Inflow reads the fax, checks insurance and nurse availability, and has an answer ready in minutes. A nurse approves with one click.
> **[B]:** Our customers' response time went from 4.5 hours to 11 minutes, and they admit 22% more patients.
> **[A]:** We have 14 paying agencies and $46K in monthly revenue, growing about 50% a month.
> **[B]:** We've known each other eight years, we're both full-time, and we both write code.
> **[A]:** Thanks for watching.

One take, no editing or music, and look at the camera.

---

## Why this application works

- **A revenue story, not a cost-saving story.** "More patients" sells faster than "fewer hours."
- **A metric that's easy to remember:** response time cut from 4.5 hours to 11 minutes.
- **Healthcare risks answered upfront:** HIPAA, liability, sales cycle, and who pays.
- **A small first product with a large next step:** an intake tool that grows into a referral routing network.
- **A founder who has done the job,** plus one who has built this kind of technology before.
