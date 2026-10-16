---
name: yc-application
description: Draft a ready-to-submit Y Combinator application from the founder's real facts, covering every form section, a 1-minute founder video script and a self-review. Use when the user is applying to YC, mentions a YC application or batch, or wants their YC answers or founder video sharpened.
---

Turn a founder's real company facts into a complete YC application: every form section drafted, a 1-minute founder video script, and a self-review that passes before you hand it over. The reader is a YC partner skimming hundreds of applications, so every answer must land in one read.

## The truth rule

Every fact in a real application comes from the founder. Traction, revenue, users, growth, customers, pilots, quotes, investors, valuations, dates and founder achievements are written only as the founder stated them. Where a fact is missing, write a **placeholder** naming exactly what is needed, `[FOUNDER: real MRR]`, and ask for it. Never invent, estimate, round up or "illustrate" a number, customer or investor in a real application: partners check, and one made-up figure sinks the whole application.

Two narrow exceptions, both shown in the draft:

- **Arithmetic** on founder-supplied inputs (growth rate from two MRR figures, market size from a customer count times a price). Show the inputs.
- **Public facts** you can cite (a count of US home health agencies). Put the source beside it; with no source, it is a placeholder.

Invented numbers exist only in the **fictional examples** under [examples/](examples/). Read them for the shape of a strong answer; no figure, name or claim from them ever enters a founder's draft.

## Principles for every answer

- **Lead with the answer.** The first sentence answers the question; the rest supports it.
- **Concrete numbers** over adjectives, each with its time frame ("$38K MRR, up 31% a month for four months", not "strong growth").
- **Founder-market fit**: say why these founders, specifically, will win this market.
- **Why now**: name the change (technology, regulation, behaviour, cost) that makes this possible or urgent today.
- **A non-obvious insight**: what the founders understand that competitors don't, stated as a claim someone could disagree with.
- **Plain language**: a smart outsider understands every sentence. No buzzwords, no vision statements in place of facts.
- **Short**: the shortest answer that carries the facts. Cut every sentence that doesn't add one.

## Process

The output is one Markdown file, `yc-application-<company-slug>.md` in the current directory (or the path the founder names), in this order: fact sheet, application sections in form order, founder video script, open placeholders.

### 1. Gather the facts

Read [INTAKE.md](INTAKE.md) and run it. If the founder has pasted or pointed at material (a deck, an old application, a website, notes), mine that first and ask only for what it doesn't cover. Ask in batched rounds, never one question per message. Accept partial answers: a gap becomes a placeholder, not a blocker.

Done when the fact sheet is written and every intake question has either an answer or a placeholder.

### 2. Draft every section

Read [SECTIONS.md](SECTIONS.md) and draft every section it lists, in order: company, founders, progress, idea, why now, competitors, business model, risks, equity, curious. Read the example in [examples/](examples/) closest to the founder's company for the shape of a strong answer:

| The company is | Read |
| --- | --- |
| B2B, SaaS, infrastructure, anything sold to businesses | [examples/tallyport-b2b-saas.md](examples/tallyport-b2b-saas.md) |
| Healthcare, or any regulated market | [examples/inflow-health-healthcare.md](examples/inflow-health-healthcare.md) |

When the company is in a regulated or risk-heavy domain (healthcare, fintech, hardware, marketplaces, consumer, AI on another company's model), read [DOMAINS.md](DOMAINS.md) for the risks partners will expect answered.

Done when every section has a draft built only from fact-sheet facts and placeholders.

### 3. Write the founder video script

Follow the video section of [SECTIONS.md](SECTIONS.md). Done when the script fits in 60 seconds spoken and every founder speaks.

### 4. Self-review, then hand over

Run [CHECKLIST.md](CHECKLIST.md) against the file, item by item, and fix every failure. Then hand over in chat:

- the file path,
- every open placeholder, each as a direct question to the founder,
- the three weakest answers, and the one real fact that would most strengthen each.

Done when every checklist item passes or its failure is a listed placeholder.

When the founder sends real facts back, update the fact sheet first, then every section and the video script that use those facts, then run the checklist again.
