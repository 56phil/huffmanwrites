# Skill: Stoic Saturday Digest

The weekly newsletter: a Stoic epigraph, a reflection at its center, the week's
news read through it, a practice for the reader, and a roundup of this site's
report series. Drafted into `pending/`, sent through SendFox, then mirrored to
`content/posts/digests/`. **The draft is untracked** (`.gitignore` ignores
`pending/*.md` and keeps only `TEMPLATE.md`), so writing and sending one owes no
commit; only the page and its hero are source.

Unlike the weekly reports, **this file is not published by a runner.** Philip reads and
edits it before it sends, so nothing here commits or pushes on your behalf.

## Cadence, section, and file naming

- Written each **Saturday** to reach readers at **06:00 CT**. The page is dated
  `<Saturday>T06:00:00-05:00`, and because Hugo builds with `buildFuture: false` it
  appears only in a deploy that runs *after* that hour — dating the file does not by
  itself publish it.
- **The page is released by its own job, at 06:05 CT, and not by another article's
  push.** `com.huffmanwrites.digest-release` (Saturdays 06:05) dispatches
  `.github/workflows/hugo.yml` and then requires the page to answer with its own
  title, which is what puts it live at ~06:07. Until 2026-10-31 the release came from
  whatever push happened next, and the only push that lands between midnight and a
  06:00 send is the daily SITREP — so the letter's URL depended on a different
  article's job, and a SITREP abort left the letter 404 while its campaign was
  already scheduled. The two publications are independent now: the SITREP's push
  still releases the page as a side effect when it runs, and the job covers the case
  where it does not.
- **The `0 11 * * *` cron is not the trigger.** It exists for this hour, but GitHub
  delays scheduled workflows — measured on this repo, they run **~4 hours late** (the
  four crons fire around 09:2x, 15:0x, 16:0x and 17:1x UTC, not at the top of their
  hour), and on 2026-10-17 the 11:00Z fire did not run at all. A cron cannot serve a
  06:15 send, which is why the release is a dispatch from a launchd job where the
  clock is knowable.
- **The page is live by ~06:07 CT, so a hand send still confirms the URL first.** An
  email that arrives at 06:00 and links a page that is still deploying is the failure
  this note prevents (measured 2026-10-17 — the newsletter reached an inbox while the
  page was absent). A scheduled campaign has no human at send time, which is why it is
  set to 06:15 rather than 06:00.
- Draft in `pending/` (`pending/TEMPLATE.md` is the shape); published page in
  `content/posts/digests/`. Slug `stoic-saturday-<phrase>.md`, lowercase and hyphenated,
  from the title's phrase; title `Stoic Saturday: <Phrase>`.

## The release job

`com.huffmanwrites.digest-release` — plist in `scripts/`, installed to
`~/Library/LaunchAgents/`, invoked through `scripts/digest-release-runner.sh`,
which calls `scripts/digest-release.py`. Fires **Saturdays 06:05 CT**; wiring pinned
by `TestDigestRelease` in `scripts/test_gates.py`, and the log is
`~/Library/Logs/digest-release.out.log`.

It reads `content/posts/digests/` for a letter whose date falls on today in Central
time, and:

- **no letter today** → exit 0, one log line. Weekly and conditional, so an absent
  letter is not a failure; a non-zero exit there would alert every Saturday about
  something no reader can act on.
- **a letter whose hour has not arrived** → exit 0. Firing early would dispatch a
  build that cannot contain the page and then fail its own check.
- **the URL already answers 200** → exit 0, no dispatch. launchd fires a missed job
  on wake, so a second run around the same morning is normal and must not deploy
  twice.
- **otherwise** → dispatch `hugo.yml`, then run `scripts/verify-published.py`, which
  requires the page's own `<title>` to carry the letter's title. The run fails if the
  page never answers; fire-and-forget would read a broken deploy as a released page.

Exercise it without touching anything:
`python3 scripts/digest-release.py --date 2026-10-31 --now 2026-10-31T06:05:00 --dry-run`.
`--section` points it at a fixture directory, which is how the tests run it.

**`scripts/digest-prep.sh` was retired on 2026-10-31.** It was written for one letter
(the 2026-10-24 issue), carried that letter's title and dates in its prose, and
installed a one-shot launchd job that was supposed to remove itself; the installed
copy survived its run and failed every Friday afterwards, alerting on a draft that had
since been archived. Preparing a letter is now the steps in this file, run by hand or
by an agent: the Friday SITREP item, the gates, two builds, the page and hero in one
commit, and the release left to the job above.

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
`*PRH | [huffmanwrites.org](https://www.huffmanwrites.org) | © Philip Huffman*`.

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
- **The email body is rendered by `scripts/digest-email.py`, not by hand.** It converts the
  draft with Pandoc and prepends the masthead: the PRH logo, the words **Stoic Saturday**
  letterspaced, and the send date read off the draft's own `date` field. Then the body, then
  the site/unsubscribe footer.
  `python3 scripts/digest-email.py pending/<draft>.md --out /tmp/letter.html`.
  **The logo is the books' logo**, `static/img/prh-logo.png` — the horse-in-ring with the
  Chancery PRH wordmark, the same artwork every title page in `~/Developer/LaTeX/AllMyBooks`
  carries via `~/texmf/tex/latex/miscImages/prh-logo.png`, copied here at 288 px so the
  masthead displays it at 120 px. Do not redraw it. It is served from `www.` because an email
  client will not follow the apex 301, so the image has to be deployed before a campaign is
  created from it.
  Nothing else is styled: the letter is edited in the draft, not in a template. The masthead
  was added 2026-10-24 at Philip's request, as an increment of one — a later typographic pass
  is a separate change, not something to fold into this one.
- **Before you send, confirm the page resolves.** Fetch
  `https://www.huffmanwrites.org/posts/digests/<slug>/` and require a 200 whose `<title>` carries
  the digest's title. The page is live by ~06:06 CT, not 06:00 (see *Cadence* above); sending
  first means the email's link 404s for the first readers. If the page is not up, the send is
  early, not the page. **This check only applies to a letter sent by hand.** A campaign
  *scheduled* through the API a day ahead has no human at send time, so the check belongs at
  scheduling time — where the page is not live yet — and cannot substitute for giving the
  campaign an hour past ~06:06. If the send is scheduled, set it to 06:15 rather than 06:00.
- **After the send:** move the draft to `pending/archive/` (never delete). It is untracked, so
  this is a local move and owes no commit; then create the Hugo page at
  `content/posts/digests/<slug>.md` with the frontmatter above — or, when the page is prepared
  ahead of the send (the PR flow), it already exists and only the local archive move remains.

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
