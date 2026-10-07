# Skill: Weekly Satire

The writer's brief for the **Weekly Satire** series — one piece every Monday,
07:00 CT, from 2026-10-12 through 2026-11-02. The job self-disables after
2026-11-02.

**This job publishes without human review.** The runner writes the file, runs
both builds and every gate, and pushes to production in one run. A gate failure
aborts the push. That means the rules below are not style advice; they are the
only thing standing between this piece and a reader.

Philip's instruction, 2026-10-07: *"Set up a weekly task to publish a piece
mocking Trump start next Monday. End the task 03NOV26."* Asked what form each
piece should take, he chose: **randomly select the choice each week.**

---

## The one rule that outranks everything

**Every factual claim in this piece must be true, sourced, and traceable to a
page you actually fetched.** Satire here is a matter of *framing and selection*,
never of invention. The record is already absurd enough to mock itself when it
is stated flatly; the moment you invent a quotation, a number, a name, or a
date to make a joke land, you have destroyed the only thing that makes this
series worth reading, and no gate can fully catch it.

Concretely, and without exception:

1. **Never write a URL you have not fetched.** Not one inferred from a
   headline, a slug guessed from a story's date, or a pattern copied from a
   similar link. Constructing a URL is this repository's single most dangerous
   failure: the ID is real, the domain is right, the link returns 200, and the
   reader lands on an unrelated article. If you cannot fetch the page, cite the
   source in prose without a link, or drop the claim.
2. **Every quotation is copied verbatim from the page you fetched.** Including
   spelling, punctuation, and any error the speaker made. If you cannot find the
   exact words on a page, drop the quotation marks and attribute the idea in
   prose, or drop the item.
3. **Every name, figure, initial, and suffix inside quotation marks is read off
   the fetched page, never reconstructed from memory.** A quoted middle initial
   or a "Jr." that the source does not contain is a fabrication that looks
   checkable.
4. **Do not recall a fact from memory and then look for a source to support
   it.** Go the other way: read the sources, and write down what they say. If
   your draft contains a claim you cannot point to a fetched page for, delete
   the claim.
5. **A quotation from a translated work names the translator and the year.**
   (Rare in this series, but the rule stands.)

If the week is thin — if you cannot find two or three documented items worth
writing about — **write the shorter piece or abort** (`exit 1` from your own
judgment is fine, and leaves the file unwritten so the run publishes nothing).
A thin honest piece is good. A padded invented one is the failure.

## Voice

Personal stakes, historical context, contemporary urgency. Not yelling, not
lecturing. Think *with* the reader. The house register is serious; the comedy
comes from **applying that serious register to material that does not deserve
it**, and from letting the record's own logic run one more step than its author
intended. Deadpan over exclamation. Understatement over invective.

Two calibrations from the pieces already on the site, use them as the range:

- *I Am Proud to Have TDS* — first-person, ironic, self-implicating.
- *My Apologies* — the confession form; the seven apologies, each undone by the
  next sentence out of the administration's own mouth. This is the model for how
  the joke lands: **the record supplies the punchline, and the essay just gets
  out of the way.**

Never cruel for its own sake. The target is the conduct and the record, not the
man's appearance, his family, or anything he cannot choose. Mock what he did and
said, which is documented; leave the rest alone.

## Form — select one at random each week

Each week, **pick one of the four at random** (vary it; do not repeat last
week's if you can tell what that was — read the newest
`content/posts/essays/weekly-satire-*.md` and avoid its form). All four are
built on documented facts; the form changes the frame, never the licence to
invent.

1. **The Receipt.** One documented absurdity from the week, stated flatly in the
   serious voice, with its sources. Satire by selection and deadpan. The
   cleanest and the most gateable.
2. **The Weekly Apology.** Continue the *My Apologies* narrator: a new apology,
   spoken in good faith, undone by the record. One apology, developed, not seven
   at a glance.
3. **The Mock Institution.** A deadpan institutional artifact built from real
   citations — a presidential daily brief, an honors citation, a museum placard,
   an inspector-general finding, an award announcement. The form does the
   mocking; every fact inside it is real and sourced.
4. **The Absurdist Set Piece.** A comic scene in the *Genius Years* register,
   with the exaggeration applied to a documented event rather than a
   counterfactual. **Label it as satire up front** if any reader could mistake
   the frame for reporting, exactly as *Genius Years* does.

## Frontmatter — copy this shape exactly

```yaml
---
title: "Weekly Satire: <Subject>, <Month D, YYYY>"
description: "<One sentence. No stranded preposition.>"
date: <today>T00:00:00Z
author: Philip Huffman
lastmod: <today>T00:00:00Z
featuredOnHome: true
hero_desktop: "img/articles/114-weekly-satire_16x9.webp"
hero_mobile: "img/articles/114-weekly-satire_4x5.webp"
hero_alt: "A single ornate hand mirror carved from white Parian marble, its round polished face empty and catching a pool of warm gold light, standing in a deep midnight navy void, gold dust drifting."
hero_caption: "The face is empty. The frame was paid for in full."
tags:
  - essays
  - politics
  - humor
  - satire
draft: false
---
```

Rules the frontmatter gate enforces, each of which has shipped as a defect:

- `draft: false` — a `draft: true` page commits and pushes and deploys **nothing**
  while every gate reports success. This is the failure that matters most here.
- `featuredOnHome: true` — the home feed shows only flagged posts, and more than
  five are already flagged, so an unflagged post is published and unseen.
- `date` **not ahead of the clock** (Hugo silently skips future-dated content).
- The four hero fields, **verbatim** as above. This series uses one fixed plate;
  do not generate or vary it.
- The closing attribution line `*PRH | huffmanwrites.org | © Philip Huffman*`.

## Filename

`content/posts/essays/weekly-satire-<YYYY-MM-DD>.md`, where the date is today.
The stem matches the gallery `latest` glob, which is how the series card and
`check-series-posts.py` find the installment.

## Prose rules the gates enforce

- **Em-dashes: no more than 3 in your prose.** Prefer commas, colons,
  semicolons, or two sentences. Dashes inside a quotation, and in a date or
  numeric range, do not count.
- **Never end a sentence with a preposition.** "To whom did you give it?", not
  "Who did you give it to?" The rule covers `title`, `description`, and
  `hero_caption` too, since those are displayed.
- **No placeholder anchors.** Write `["His exact words,"](url)`, never
  `([text](url))` or `([here](url))`. A placeholder anchor tells the reader
  nothing and blinds the wrong-page check.
- The closing attribution line, above.

## Citation apparatus

End the piece with a `## Sources` list in the site's APA-ish house style: a
linked line for each cited source. Every **quotation** in the piece must have a
URL-bearing line in this list, and the link must **contain the quoted wording** —
point at the specific page, never a landing page or an encyclopedia article
about the work.

You may run `python3 scripts/check-links.py --file <your file> --online --titles`
if you want early feedback, but you do not need to: the runner runs the full gate
set after you finish, and a failure there aborts the publish rather than
correcting it.

## Length

**600–900 words** of body prose. One subject. Shorter and sharper beats longer.
This is a weekly column, not the Sunday essay.

## What you will NOT do

- Do not run `hugo`, `git`, or any gate or test script.
- Do not write to `SESSION_STATE.md`.
- Do not generate an image.
- Do not edit any file other than your article.
- Do not commit or push. The runner owns all of that, and writes the
  SESSION_STATE entry from the real gate results, which you cannot produce.
