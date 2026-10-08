# Skill: Daily Global SITREP

A situation report on the state of the country and the world, written every
morning from a briefing pack that a script produced, and **published
automatically** — this job goes to production in the same run that writes the
file, with no human reading it first.

## When this runs

- Scheduled by launchd: `com.huffmanwrites.daily-sitrep` (plist source:
  `scripts/com.huffmanwrites.daily-sitrep.plist`; runner:
  `scripts/daily-sitrep-runner.sh`), **every day at 0600 CT**.
- The runner invokes Claude Code headless in this repo with this skill, and hands
  it the briefing pack at `/tmp/sitrep-pack-$TODAY.md`.
- If a file for today's date already exists, it was deleted before you started: the
  runner removes a stale copy at that path so it can never be committed with
  today's title. Write the file fresh. Do not go looking for yesterday's text to
  revise.
- The beats, in Philip's words (2026-10-07): the courts, the administration and
  the rule of law, markets and the economy, and elections and civics. "Global"
  adds the world-news beat. **Technology and AI is not a beat** — it was one of
  the five he chose, and he removed it on 2026-10-07: "That risk concerns me.
  Let's eliminate the AI beat." See "Do not write about technology or AI" below.

## Provider policy (Philip, 2026-09-06)

- **No Anthropic or OpenAI resources.** The only AI API keys available are FAL
  and Ollama. Do not call api.anthropic.com, api.openai.com, or any
  Anthropic/OpenAI endpoint.
- The model runs on **Ollama, local or cloud**. The runner points at the local
  Ollama daemon (`http://localhost:11434`), which serves both local models and
  `:cloud` models; model `deepseek-v4.1-flash:cloud` (must match `ollama list`
  exactly). Auth uses `OLLAMA_API_KEY` from the login keychain
  (`huffmanwrites-ollama`), with `~/.secrets` as fallback; the runner extracts it
  because launchd does not source the shell.
- FAL is available for images. This report does not generate one: it carries the
  **series plate** (see Output), a fixed pair reused every day.

## The one thing that makes this job different

**This job publishes.** The runner commits and pushes the page it wrote, and the
site deploys on that push. There is no drafting standard here, only the
publishing standard: everything below is a requirement, not a preference, and no
human sees the piece before it is live.

Three consequences you should feel while writing.

**A fabricated fact ships unread.** The repo's most dangerous failure class
(CLAUDE.md §Citations) is a URL or a name that looks checkable and is wrong, and
here it would go straight to production the moment it is written. The runner
fetches every URL you cite and compares the page's own title against your link
text, which catches a link that resolves to the wrong page — but it cannot catch
a fact you got wrong on a page you did fetch.

**A daily cadence has no review window.** By the time a human could read
yesterday's edition, today's is already due. The gates are the entire review, and
the runner aborts the push on any failure. That is why the standard is the
publishing standard on every run, including the quiet ones.

**A thin report is worse than no report.** A slow day is a real day: write it
short and say it was quiet. Do not pad it with recalled history, generic
analysis, or a "what this means" paragraph that says nothing. Manufactured length
is the failure this job is most exposed to, because a situation report invites
the habit of filling every heading.

## Step 1 — Read the briefing pack. It is the spine of the piece.

**The runner has already written the pack and given you its path in the prompt**
(`/tmp/sitrep-pack-$TODAY.md`). Read that file first, in full. Do not re-fetch
the Federal Register, the Treasury, the BLS, or the markets to reconstruct it.

If you need a field in structured form, re-run the collector, which is on your
allow-list:

```
python3 scripts/sitrep-pack.py --json              # the same data, structured
python3 scripts/sitrep-pack.py                     # the pack again, as markdown
python3 scripts/sitrep-pack.py --date 2026-10-07   # evaluate a past date
python3 scripts/sitrep-pack.py --window-days 2     # widen the Federal Register / CourtListener lookback
```

The pack opens with a `## Sources in this pack` table that says, per source,
whether it answered. Read that table first: it tells you which sections are whole
and which carry a gap. The sections below it are the day's hard record — the
Federal Register documents, the court opinions and filings, the Treasury yield
curve, the debt to the penny, the BLS series, and the prediction markets with
enough volume to read.

**Every number in your piece comes from this pack or from a page you fetched
yourself.** You do not recall a score, a rate, a price, a date, a case name, a
dollar figure, or a quotation. If a number you want is not in the pack, run the
pack again, fetch the page that carries it, or leave it out. Do not fill the gap
from memory. This is the rule that makes the job safe to run unattended: the pack
is the only thing in the pipeline that has seen today's numbers, so a writer that
reconstructs them from memory converts every figure in the piece into a recalled
one — and a recalled figure is the fabrication path CLAUDE.md was written about.

**A number that did not come from this run is a number you cannot vouch for.**
Every block in the pack is stamped with its own date and an "as of" line. Keep
that stamp with the number when you write it: a market print from 09:40 CT, a
debt figure for the prior business day, a BLS series for a named month. A reader
must be able to tell whether a figure is today's or a week old.

**If a source failed, the pack says so and so do you.** A failed source appears
as a `**SOURCE UNAVAILABLE** — <name>: <reason>` line and as a row marked
unavailable in the status table. The pack still exits 0, because a report with a
gap in it is still a report. Your piece does the same: say in one sentence that
the source was unreachable, work around the gap, and move on. Never fill the
silence from memory, and never present a partial section as a whole one.

## Step 2 — Get what the pack cannot give you.

The pack carries the day's hard record. It is not reporting, and it does not
cover every beat. **One** section of the report has **no collector at all** and is
entirely yours to fetch:

- **The world** — one story from outside the United States that actually moved.

For that, and for any context the pack cannot supply, search and read what
carries the story. Fetch the page before you cite it. A fact in that section is
held to exactly the same standard as a number in the pack: fetched, and linked.

Do not let the fetched beat swallow the piece. One story, chosen for what
changed, is the shape. A general-news digest is not this report.

### Do not write about technology or AI

There is no technology or AI section, and adding one is a failure rather than
initiative. It was a beat of the first version and Philip removed it on
2026-10-07, the day after the first edition shipped, because the fetched half of
that beat was the one place in the report where the writer chose what to assert
with no collector behind the choice.

So: no AI-model releases, no data-centre or chip news, no technology-company
items, no "and in technology" paragraph — not as a section, not inside another
section, not in the lede, and not in `## Sources`. The pack does not raise the
subject (see its `## 7. Not in this pack`) and neither do you. If the day's news
is dominated by it, the report is shorter and says nothing about it, which is
correct.

**What the ban does not cover.** A government action that merely mentions
technology belongs to the beat it is actually part of, and reporting it is not
the removed beat. A Federal Register notice continuing the Section 301 actions
against China over technology transfer is trade policy; it goes in the
administration section, named as the trade action it is. An agency rule on
medical devices goes in the administration section. The test is which beat the
item is, not which words appear in its title. A private company's product
launch, a model release, or an industry trend is the removed beat and does not
appear at all.

## Step 3 — Write it.

### House style

- Tone: personal stakes + historical context + contemporary urgency. Not
  yelling, not lecturing. Think *with* the reader.
- **Third person.** The report is a situation report, not a letter. Write "the
  Senate voted", not "I watched the Senate vote". Address the reader only where
  a turn of address genuinely earns its place.
- Prose is the spine. The pack is evidence. A reader should finish knowing what
  changed, why it matters, and what to watch tomorrow.
- Em-dash limit: no more than 3 in the prose you write. Not counted: a dash
  inside quotation marks, and a dash standing as a date or number range (the
  en-dash is the right mark for a range; an em-dash there is a typo). Count with
  `python3 scripts/check-emdashes.py --file <path>`.
- **Never end a sentence with a preposition** (house rule, 2026-09-25). Applies
  to body prose and to the frontmatter display fields (`title`, `description`,
  `hero_caption`). Check with
  `python3 scripts/check-prepositions.py --file <path>`.
- Closing attribution: `*PRH | [huffmanwrites.org] | © Philip Huffman*`.

### Sourcing rules that are not negotiable

These are CLAUDE.md's citation rules restated as instructions; read that file for
the reasoning and the failure each one prevents.

- **Fetch before you cite.** A URL may be written only after the page has been
  retrieved and confirmed to be the thing cited.
- **Never construct a URL from a pattern.** Do not infer a slug from a headline,
  do not build a URL from the shape of a real one, and do not guess a
  date-and-slug from a publication date. A constructed URL returns 200 and lands
  the reader on an unrelated page, and no ordinary check can see it.
- **The link's visible text must be the thing cited** — the headline, the case
  name, the document. Never `text`, `here`, or `link`. The runner fetches each
  page and compares your link text against its own `<title>`, so a placeholder
  anchor blinds the only check that catches a link pointing at the wrong page.
  `check-report-frontmatter.py` fails the report on a placeholder anchor.
- **Every direct quotation carries a resolvable source link** in the piece's own
  apparatus — the `## Sources` list. The link must contain the quoted wording
  (point at the passage, not a landing page) and must be live when the report
  publishes. If you cannot link the wording, do not put it in quotation marks:
  attribute the idea in prose instead.
- **Quote verbatim, never paraphrase inside quotation marks.** What is between
  the quotation marks is a claim that those exact words appear at that address.
  Copy a name, an initial, a suffix, or a figure off the fetched page; never
  reconstruct it from memory.
- A quotation from a translated work names the translator, the translation, and
  the year. (Rare here, but the rule binds wherever a translation appears.)

### Structure

1. **The lede** — the day in one paragraph. This is not a summary of the table
   below it: it is what actually changed. If three things moved, name the one the
   reader cannot afford to miss and say why, in prose. No
   **Question:**/**Answer:** pair here; this is a report, not a weekly essay.
2. **The administration and the rule of law** — the Federal Register documents
   of the window: presidential documents, rules, proposed rules, notices. Name
   the few that matter and what they do; do not print the whole list.
3. **The courts** — opinions filed in the window (Supreme Court, D.C. Circuit)
   and new district-court complaints, then a line on each of the watched dockets
   saying whether the watcher recorded a filing in the window.
4. **Markets** — the board (indexes, VIX, yields, gold, oil, the dollar), the
   Treasury yield curve with the 2s10s spread, and the federal debt to the penny.
   Keep each figure with its "as of" stamp.
5. **The economy** — the BLS series in the pack (cpi, unemployment, payrolls),
   each with its month, and what the three readings taken together say.
6. **Elections and the midterms** — the Polymarket markets with real volume:
   question text, implied probability, 24-hour volume. These are the venues'
   prices, not this site's view; attribute each figure to the venue that carries
   it, and never average a thin book into a number that reads as a forecast.
7. **The world** — one story from outside the country, fetched and cited.
8. **Sources** — every link you used, in the piece's citation apparatus.

There is no technology or AI section. See "Do not write about technology or AI"
in Step 2 for why, and for what that rules out.

A section with nothing in it is a sentence, not a heading padded to look full. If
the courts were quiet, say the courts were quiet. If a source for a beat was
unavailable, say so there. **Do not create a section that exists only to be
filled**, and do not drop a beat silently: a reader should be able to tell the
difference between "nothing happened" and "we could not look".

Target 1,200-2,000 words of prose. A quiet day lands at the low end, and that is
correct.

## Output

- File: `content/posts/sitrep/sitrep-YYYY-MM-DD.md` (date = run date).
- Frontmatter:
  ```yaml
  ---
  title: "SITREP: <Month D, YYYY>"
  description: "One sentence naming what the day's report found."
  date: <run time, CT, ISO 8601>
  author: Philip Huffman
  lastmod: <same as date>
  draft: false
  featuredOnHome: true
  tags: [sitrep, civics, markets]
  hero_desktop: "img/articles/115-sitrep_16x9.webp"
  hero_mobile: "img/articles/115-sitrep_4x5.webp"
  hero_alt: "An armillary instrument of Parian marble: nested open rings crossed by a slender gold needle above a dark granite dome, lit by a single shaft of gold against midnight navy."
  hero_caption: "The watch is kept in the same light every morning. What it reads is never the same twice."
  ---
  ```
  - `draft: false` — this job publishes; the runner will push it.
  - `featuredOnHome: true` is set as the house default for a published post, but
    the SITREP section cascades `hiddenInHomeList: true` (see
    `content/posts/sitrep/_index.md`), so the daily series does not flood the
    home feed. The current edition is surfaced on the home page by the section
    template. Keep the flag.
  - **The four hero fields are copied verbatim from the block above — do not
    invent, edit, or regenerate them.** They point at a **series plate**: one
    pair of images commissioned for the report (number 115) and reused for every
    daily installment, the way a masthead is reused. The gate pins the two paths
    (`--plate 115-sitrep`), so a path that names a different file, or a missing
    one, fails the publish.
  - `description` is the day's finding, not a generic blurb. It renders as the
    social card and the search result, so it must say what today's report found.

### The series plate (fixed, copied verbatim — do not generate one)

Every SITREP carries the **same** hero pair, commissioned once for the series and
reused for every daily installment. It is plate **115** and it is not a daily
choice. Copy these four fields exactly, byte for byte:

```yaml
hero_desktop: "img/articles/115-sitrep_16x9.webp"
hero_mobile: "img/articles/115-sitrep_4x5.webp"
hero_alt: "An armillary instrument of Parian marble: nested open rings crossed by a slender gold needle above a dark granite dome, lit by a single shaft of gold against midnight navy."
hero_caption: "The watch is kept in the same light every morning. What it reads is never the same twice."
```

Do not invent, edit, or regenerate them, and do not give an individual edition
its own hero. The plate belongs to the series, not to the day, so two editions
carrying the same image is the intended result.

### Date guard

The `date` must never be ahead of the wall clock when the file is written, and it
must be an ISO 8601 timestamp the gate can parse. Hugo's default
`buildFuture: false` silently skips future-dated content: the build succeeds and
the page is simply absent, which is the failure that hides. At a 0600 CT run,
stamp the run time; do not round it forward.

- No newsletter/sendfox fields.

## Step 4 — Report back, in this shape

End your run with a short summary the runner's log will carry:

- the file you wrote and its word count;
- the day in one line (the lede's finding);
- the per-section item counts you wrote from the pack;
- every URL you cited that did NOT come from the briefing pack;
- any source that failed and what you wrote around it;
- anything you could not verify and therefore left out.

Keep it under 200 words. The runner reads your file, not your prose.

## Fallbacks

- **A pack source failed.** Say so in one sentence in that section and write
  around the gap. Do not invent the missing numbers.
- **A beat is quiet.** Say the beat is quiet. A short honest report is correct.
- **No story worth the lede.** Then the lede is the day's most consequential
  pack item — a court ruling, a rule, a market move — written as prose.
- **You cannot find a source for a claim.** Leave the claim out. There is no
  version of this job where an unverifiable sentence ships.

## A note for a future session

**What is deliberately not in the pack, and why.** The collector covers the beats
that have an API: the Federal Register, the CourtListener search API, the Treasury
yield curve, FiscalData, CNBC's quote service, the BLS public API, and Polymarket's
Gamma API. **World affairs has no collector.** There is no feed for "the one story
that moved", and a daily-cadence collector cannot be given a stable query for it,
so that beat is fetched and cited by the writer, and it is the one section where a
fabrication is most likely to originate. The gates catch a dead link, a
placeholder anchor, and a quoted name detail that appears on no cited page; they
cannot catch a story the writer half-remembered and cited to a page it did fetch
for a different reason.

**The AI and technology beat is gone, and the reason generalizes.** It had the
same shape as the world beat: half of it came from a collector (prediction-market
prices) and half was fetched. On 2026-10-07 Philip read that risk stated plainly —
"It concerns me" — and removed the beat outright. That is the cheapest available
answer to an uncollected beat, and it is worth remembering as the first option
rather than the last: a beat nobody collects is a beat the writer invents, and a
beat the series does not carry cannot be invented. Removing it cost one entry in
this file and one tuple in the collector.

**The lever for hardening what remains is a wider collector, not a longer set of
instructions.** If a future session wants to remove the residual risk in the world
beat, the move is to build a collector that pre-fetches a candidate pool of stories
for the writer to *select from*, the way `scripts/sitrep-pack.py` pre-fetches the
day's documents — not to add another paragraph of fetch-before-cite prose to this
file. Instructions bind only the writer that reads them; a collector binds every
run. Do not mistake the length of this skill for its strength.
