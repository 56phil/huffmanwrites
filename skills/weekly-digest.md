# Skill: Stoic Saturday Digest

The weekly newsletter: a Stoic epigraph, a reflection at its center, the week's
news read through it, a practice for the reader, and a roundup of this site's
report series. Drafted Saturday morning into `pending/`, sent through SendFox,
then mirrored to `content/posts/digests/`.

Unlike the weekly reports, **this file is not published by a runner.** Philip reads and
edits it before it sends, so nothing here commits or pushes on your behalf.

## Cadence, section, and file naming

- Written each **Saturday** to reach readers at **06:00 CT**. `.github/workflows/hugo.yml`
  builds on a schedule at 11:00 UTC for exactly this, so a page dated at the run and
  flagged `draft: false` goes live on that cron.
- Draft in `pending/` (`pending/TEMPLATE.md` is the shape); published page in
  `content/posts/digests/`. Slug `stoic-saturday-<phrase>.md`, lowercase and hyphenated,
  from the title's phrase; title `Stoic Saturday: <Phrase>`.

## Frontmatter

```yaml
---
title: "Stoic Saturday: <Phrase>"
description: "One or two sentences naming the week's developments and the Stoic line that sorts them."
date: <Saturday 06:00 CT, ISO 8601>
lastmod: <when the draft was finished; may precede date>
author: Philip Huffman
sendfox_subject: "Stoic Saturday: <Phrase>"
tags:
  - weekly-digest
  - stoicism
hero_desktop: "img/articles/NN-slug_16x9.webp"
hero_mobile: "img/articles/NN-slug_4x5.webp"
hero_alt: "<a sentence describing the plate>"
hero_caption: "<the line the plate earns>"
draft: false
featuredOnHome: true
---
```

- **`sendfox_subject`** is the inbox line, `title` the page line; a missing field sends a
  blank subject.
- **`featuredOnHome: true`** is required: the home feed fills its Recent Posts from flagged
  posts and more than five carry the flag, so an unflagged post reaches no reader from the
  home page. `scripts/check-series-posts.py` covers the recurring series.
- **`lastmod`** on every post; `scripts/check-content-frontmatter.py` fails a post without it, and
  also requires `sort_key` on every summary. `scripts/check-report-frontmatter.py --corpus` reads
  series installments the way a publisher would.
- **Hero fields.** Each digest gets its own plate, since the image carries the week's theme;
  the report series instead reuse one fixed plate. New heroes must be **WebP** named
  `[NN]-[slug]_16x9.webp` and `[NN]-[slug]_4x5.webp` (see `skills/hero-image-workflow.md`).
  `scripts/check-hero-paths.py` fails a path that names no file.

## The reflection

**The letter's central component**, established 2026-10-10. Every Stoic Saturday carries a
reflection of **no fewer than three well-written paragraphs**. The letter is built around it;
the week's items support it rather than the other way around.

- **Where it sits.** Immediately after the epigraph, near the top of the letter, under the
  bold heading **The reflection**. The week's items follow it.
- **What it is.** A sustained piece of thinking, not a summary of the items. It names the
  meaning the week carries and turns it over: what the pattern is, what the Stoic line above
  it actually says and refuses to say, and what it asks of the reader. The items below supply
  the facts; the reflection supplies the reading of them.
- **The epigraph serves the reflection.** Choose the line above it for the reflection, not the
  reflection for the line: the epigraph is the one that sorts what the reflection argues.
- **Three paragraphs is the floor, not the target.** A reflection that restates the items in
  shorter words is not a reflection. It has to take a position and hold it.

Where a letter shipped without one, the fix is to write it and amend the published page —
the email cannot be recalled, but the site's copy is the record a reader returns to. The
2026-10-10 letter ("The Thing Not Done") went out without a reflection and was amended the
same morning.

**Not mechanically gated.** Length has a floor, but whether the reflection is *well written*
and truly central is a judgment, and it is the one the reader is owed. The gates named below
cover the rest.

## The weekly-reports roundup

A **standing structural element**, added 2026-10-03, under the heading **The weekly
reports**. For **each publishing series**, write a sentence or two on the **most recent
published installment** and link that installment's full report. Each source file is the
same slug under the matching section (`content/posts/essays/senate-race-report-<DATE>.md`,
and so on).

The six series and the URL each installment resolves to (`<DATE>` is `YYYY-MM-DD`):

- Senate Race Report: `/posts/essays/senate-race-report-<DATE>/`
- Docket Report: `/posts/essays/docket-report-<DATE>/`
- Bond Ninety-Days: `/posts/investing/bond-market-ninety-days-<DATE>/`
- S&P Ninety-Days: `/posts/investing/sp500-next-ninety-days-<DATE>/`
- Chiefs Report: `/posts/sports/chiefs-report-<DATE>/`
- Global SITREP: `/posts/sitrep/sitrep-<DATE>/`

Three rules:

- **A summary states what the installment found**, not the cadence. The roundup reports the
  reports rather than advertising them.
- **Every summary names a report that exists.** Fetch the URL and confirm it resolves before
  you write it in. Where a series has not yet published its first installment, say so rather
  than linking a page that does not exist.
- **The link is written only after the page has been retrieved.** Those shapes are the
  pattern the files take; they are not a licence to construct a URL from the calendar.

**The Repair Plan is excluded.** It is a quarterly working document for a future
administration, not a reader-facing report, and it does not appear in the roundup.

## Writing rules

Tone: personal stakes + historical context + contemporary urgency. Not yelling, not
lecturing. Think *with* the reader. Structure: the epigraph; **the reflection** (the central
component, no fewer than three paragraphs, immediately after the epigraph); the week's items
with bold lead-ins; **The weekly reports**; **The Practice**; the sign-off ("See you next
Saturday. — Phil"); the sources line; the `## Sources` list; and the closing attribution
`*PRH | [huffmanwrites.org](https://huffmanwrites.org) | © Philip Huffman*`.

These rules are enforced, and each names its gate.

- **Never end a sentence with a preposition.** House rule, 2026-09-25, covering the body
  prose and the frontmatter display fields (`title`, `description`, `hero_caption`). Check
  with `python3 scripts/check-prepositions.py --file <path>`; the ratchet is `--check`.
- **Em-dash limit: no more than 3** in the prose you write. Two categories are exempt,
  because they are not your prose: a dash **inside quotation marks**, and a dash standing as
  a **date or numeric range**. Count with `python3 scripts/check-emdashes.py --file <path>`;
  `--check` fails a file whose count grows.
- **A quotation from a translated work names the translator, the translation, and the
  year.** The Stoic epigraph is the case this catches: write `Author, *Work*, §N (trans.
  Name, Year)`, never a bare reference that hides the translation.
  `scripts/check-quotes.py` fails an epigraph that names no translator or carries no
  URL-bearing line.
- **Every direct quotation carries a resolvable source link** in the piece's apparatus (the
  `## Sources` list), pointing at the translation, edition, or passage containing the quoted
  wording rather than a landing page or an article *about* the work. With no linkable
  rendering, drop the quotation marks and attribute the idea in prose.
- **Never construct a URL. Fetch it, or do not cite it.** A constructed URL can return 200
  and serve an unrelated page. `scripts/check-links.py --check` rejects placeholder and
  blocklisted URLs in CI; `scripts/check-links.py --online --titles` fetches each citation
  and compares the page's own title against your link text, the only check here that can
  catch a link pointing at the wrong page.
- **The link text must be the thing cited**, never a placeholder such as `text`, `here`, or
  `link`. `python3 scripts/check-report-frontmatter.py --anchors-corpus` fails any published
  post that uses one, and it runs in CI.

## The send flow

- **Token:** the SendFox key is the login keychain item `huffmanwrites-sendfox`, with
  `~/.secrets` (`SENDFOX_CLIENT_SECRET`) as the fallback. **Never a repo-local
  `.sendfox_token`;** both it and `.fal_token` were that mistake, and
  `scripts/check-secrets.py` fails if either returns.
- **Send:** the `pending/` file is the newsletter body and the page source at once; send it
  through the SendFox API, whose `form-action` the site CSP whitelists.
- **After the send:** move the pending file to `pending/archive/` (never delete), then
  create the Hugo page at `content/posts/digests/<slug>.md` with the frontmatter above.

## What is not gated

- **The reflection is a writing judgment.** Its floor is three paragraphs, but no gate counts
  them or reads them, and none can check that the reflection is the letter's center rather
  than a restatement of the items. Whether it is worth reading is the part a reader is owed,
  and it is yours.
- **The roundup judgment is a writing decision.** No gate checks which installment is the
  most recent, which one you surface, or whether your sentence states what it found. That is
  the part a reader is owed, and it is yours.
- **The mechanical half is enforced**, in CI or in the weekly integrity sweep: dead links
  (`scripts/check-links.py`), placeholder anchors and report frontmatter
  (`scripts/check-report-frontmatter.py --anchors-corpus`), content frontmatter
  (`scripts/check-content-frontmatter.py`), quotation citations
  (`scripts/check-quotes.py`), dashes (`scripts/check-emdashes.py`), and prepositions
  (`scripts/check-prepositions.py`). All of those fail the deploy.
- A human edits the digest before it sends, so the gates are a floor rather than the whole
  review. Write to the publishing standard anyway: an edit catches a bad sentence, not a
  fabricated one.
