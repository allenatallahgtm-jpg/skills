## What it does

`yc-application` turns a founder's real company facts into a complete, ready-to-submit Y Combinator application: every section of the form (company, founders, progress, idea, why now, competitors, business model, risks, equity, curious), a 1-minute founder video script, and a self-review before it hands anything over.

It never invents a fact. Traction, revenue, customers, investors and founder achievements come only from the founder; anything missing becomes a visible **placeholder** like `[FOUNDER: real MRR]`, and the hand-over lists every one as a question for you to answer. The only invented numbers anywhere in the [skill](https://www.aihero.dev/ai-coding-dictionary/skill) live in two clearly labelled fictional example applications it reads for shape.

## When to reach for it

Type `/yc-application`, or the [agent](https://www.aihero.dev/ai-coding-dictionary/agent) reaches for it automatically when you say you're applying to YC or want help with your application.

| Your situation | Reach for |
| --- | --- |
| Writing a YC application, from scratch or from notes, a deck or an old application | `yc-application` |
| Sharpening existing YC answers or the founder video | `yc-application`: paste what you have and it asks only for what's missing |
| The idea itself is still fuzzy, and you need to think it through before writing anything | [grill-me](https://aihero.dev/skills-grill-me), then come back |

## The fact sheet and the placeholder

The run has four beats: one batched round of intake questions (plus a short follow-up on the gaps that matter), a draft of every section, the video script, and a checklist pass.

The **fact sheet** at the top of the output file is the leading idea. Every number in the application must trace to a row in it, and every row came from you, from arithmetic on your inputs (shown), or from a cited public source. That is what makes the draft safe to submit and easy to update: send a real number back, and it changes the fact sheet first, then every answer and the video line that use it.

The drafting itself pushes each answer toward what partners read for: a one-liner of 50 characters or fewer that says what the product does, concrete numbers with time frames, explicit founder-market fit, a specific why now, a non-obvious insight against named competitors, and plain language. In regulated markets it also drafts the risks partners expect answered; for healthcare, that means HIPAA and BAAs, clinical liability, sales cycle, and who pays.

## Common questions

**Can it fill in numbers so the draft reads better, and I'll fix them later?**
No, by design. A plausible invented figure is the one most likely to survive into the submitted form, and a partner who checks it ends the application. The draft shows `[FOUNDER: ...]` instead, which reads worse on purpose: it is the to-do list.

**Does it match this batch's exact form?**
The form's wording and fields shift between batches. Paste your live form and it follows that wording, order and character limits; otherwise it drafts against the standing shape of the form, with why now and risks drafted as their own answers so you can place them wherever your form asks.

**Does it submit the application?**
No. It writes a Markdown file in the current directory, laid out question by question, for you to paste into the form.

## It's working if

- Its first message is one batched set of questions, not a single question or a finished draft.
- Every number in the draft is one you gave it, or a calculation it shows from yours.
- The one-liner arrives with its character count, at 50 or fewer.
- The hand-over ends with a list of open placeholders, each phrased as a question you can answer in a line.
- Sending a real number back changes every answer that uses it, including the video script.

## Where it fits

A reach-for-it-anytime standalone, off the engineering flows. Its neighbour is [grill-me](https://aihero.dev/skills-grill-me), because an idea that can't survive a grilling session won't survive a YC partner either: sharpen it there first, then draft here. For anything else, [ask-matt](https://aihero.dev/skills-ask-matt) routes you.
