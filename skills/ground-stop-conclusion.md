# Skill: the ground-stop conclusion, written and published in one run

The third and last installment of the series on the nationwide ground stop of
13NOV26. It is written **and published in the same run** by
`com.huffmanwrites.ground-stop-conclusion-release` at 10:00 CT on 1 December
2026 (1600Z). There is no review step: the gates are the review.

Philip, 17NOV26: "It is my wish that the article be written as part of the act
of publishing."

The second installment, `content/posts/essays/the-sixty-routers.md`, ends by
promising "a fuller accounting follows in early December". This is that
accounting, and the promise is the brief.

## Where every fact comes from

**`future-pieces/faa-ground-stop-source-notes.md` is the whole source.** Read
§18 (the government's stated cause and its contradictions), §19 (the daily
collection log), §20 (settled daily totals) and §21 (verified citations) before
writing a word.

- **A date, name, figure or quotation is copied from that pack or from a page
  you fetched in this run. Never from memory, never inferred.**
- **Archive URLs come from §21 only.** A capture that is not in that table has
  not been checked and may not serve the document. §16's list is stale and says
  so itself.
- **Daily numbers come from §20.** It is a merged, dated table; the tracker
  shows three days and the pack keeps them all.
- **An advisory cited live must also carry its archived copy in the piece.** The
  FAA's index drops the document fifteen days after the fact, which is before
  this piece publishes, so a live `adv_otherdis` URL alone will be a dead link
  in a footnote. `scripts/faa-ground-stop-pack.py --audit --file <this piece>`
  is the check, and the runner runs it.

## What the piece must establish

In this order, because this is the order the record supports:

1. **What the two orders actually said.** Advisory 111, 20:54Z, "NATIONAL GROUND
   STOP", no REASON and no REMARKS field. Advisory 120, 22:46Z, "NATIONWIDE
   GROUND STOP", `REASON: COMMUNICATIONS FAILURE`. Two documents, one blank
   field, and the difference between them is the difference between the order
   and its explanation.
2. **What the government now says caused it**, and what it does not say. The Q&A
   of 15NOV26 names two sites: a radio communications site at El Dorado,
   Arkansas, where L3Harris had deployed a new router, and a radar site at
   Amarillo, Texas, replaced three weeks earlier. The flood was "1,000 connection
   attempts every 4 to 5 seconds" destabilising 17 of 22 en route centres. The
   agency's own words on cause are "we don't actually have the root cause". That
   sentence is the spine: a stop of four hours and twenty-five minutes whose
   explanation is still open three weeks later.
3. **The remedy and its cost.** The broadcasting function was disabled on
   "approximately 60 similar routers". No document says what the function did or
   what the airspace gave up. Print that absence as an absence.
4. **The Thanksgiving period**, 20–30NOV26, which is the test the second
   installment said the schedule would face: Airlines for America projected
   nearly 29 million passengers with the busiest days on 29 and 30 November, and
   §20's ledger is the day-by-day record of what actually happened. Report the
   ledger, including the days it shows nothing unusual; a quiet day is a finding.
5. **The money, as four different numbers**: $12.52B appropriated in P.L. 119-21
   §40003 (with $4.75B expressly for telecommunications infrastructure), $4.3B
   obligated, $1B spent, and a request for $50B to build a network the agency
   would not own. Say which is which; do not net them into a figure of your own.
6. **What nobody has published.** No OIG report on 13NOV26. No root cause. No
   document on whether the copper-to-fiber cutover resumed. GAO's finding of
   11,389 project schedules that are not integrated, from GAO-26-107992, which
   predates the outage and explains it better than any press account.

## What the piece must not do

- **Do not name a root cause.** There is none in the record. "The router flooded
  the network" is the agency's account of the mechanism; the reason the router
  did it is unanswered, and a sentence that closes that gap is a fabrication.
- **Do not use `nasstatus.faa.gov` for anything.** It never carried the national
  stop, and it contradicted itself within half an hour (§17).
- **Do not attribute a quotation to a translation or a person** unless the pack
  or a page you fetched carries it verbatim, with the name inside it.
- **Do not cite a live advisory URL without its archived copy** in the same
  footnote, as above.
- **Do not resolve the count discrepancy** between the FAA (12,462 on the day,
  9,082 by major airlines) and FlightAware (9,938 worldwide). Print both with
  their definitions, or print one and say whose it is.

## Shape and length

2,800–3,500 words, the length of the two installments before it. House voice:
personal stakes, historical context, contemporary urgency; think *with* the
reader. No stranded prepositions; no more than three em-dashes in your own prose
(quoted material does not count). End the body with the credo line the essays
carry, then the closing attribution exactly as below.

Structure that has worked for this series: a scene or a single document in the
first paragraph, then the record, then the contradiction, then what remains
unanswered, then the close that returns to the opening object.

## Frontmatter, exactly

```yaml
---
title: "<your title>"
description: "<one sentence, no stranded preposition>"
date: 2026-12-01T10:00:00-06:00
author: Philip Huffman
lastmod: 2026-12-01T10:00:00-06:00
draft: false
featuredOnHome: true
hero_desktop: "img/articles/163-ground-stop-conclusion_16x9.webp"
hero_mobile: "img/articles/163-ground-stop-conclusion_4x5.webp"
hero_alt: "<one sentence describing a marble slab in a dark hall with a seam of amber light>"
hero_caption: "<short line; it must not repeat the alt text>"
tags:
  - civics
  - essays
  - aviation
---
```

The hero pair is fixed. Do not generate, rename or re-prompt an image.

## Citations

Every quotation and every load-bearing fact carries a link in the piece's own
apparatus: `## Sources` for prose citations, footnotes for the report-style
citations the two installments used. A source line carries the date of
publication in the house form (`November 15, 2026`) and a link that contains the
wording quoted. If a wording cannot be linked, drop the quotation marks and
attribute the idea in prose.

End the file with exactly:

```
*PRH | [huffmanwrites.org](https://www.huffmanwrites.org) | © Philip Huffman*
```

## The gates that will run after you finish

`scripts/publish-report.sh` runs frontmatter, hero paths, anchors, links
(`--online --titles`), quotation names, em-dashes, prepositions, render
integrity, and two builds. Then `faa-ground-stop-pack.py --audit --file` checks
every archive URL in the piece and every advisory's archived copy. A failure
aborts the publish: the file stays on disk and nothing is pushed.

You may run `python3 scripts/check-emdashes.py --file`, `check-prepositions.py
--file` and `check-links.py --file` yourself before you finish. Everything else
is the runner's job and its log is the record.
