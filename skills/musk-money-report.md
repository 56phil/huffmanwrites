# Skill: The Musk Money (one-off, 6 December 2026)

Philip, 2026-11-02: *"Elon Musk spent a large amount of money on the midterm
election. After the dust settles, I want to publish a piece on that."*
Philip, 2026-11-05: *"Add the job. Schedule it for 1000 06DEC."*

This is the piece `future-pieces/musk-midterm-spending.md` was written to wait
for. That brief is the source of the angle, the material and the date; read it
first, and read the three civics pieces it links. Nothing here replaces it.

## When this runs

Once. `com.huffmanwrites.musk-money-report` fires Sunday **2026-12-06 at 10:00
CT**, and the runner's date guard makes that the only day it can ever run. The
date is not a preference: the **Post-General** FEC report (period 10/15 through
11/23) is due **2026-12-03**, so December 3 is the first day a cycle total
exists for any committee. Before it, "how much did he spend" rests on press
tallies that are superseded within the week.

The runner aborts with an alert if no `30G` Post-General filing is in the pack.
If that happens, the piece does not exist yet and nothing is published.

## The collector, and the one rule that governs this piece

`scripts/fec-spending-pack.py` runs **before** you, and its output is handed to
you by path in the prompt. Read it. Every figure in the article comes from it.

**You may not recall a number.** Not the cycle total, not a committee's receipts,
not a race's margin, not a cost per vote. If a number is not in the pack and not
on a page you fetched and linked, it does not go in the piece. This rule matters
more here than anywhere else in the corpus, because every figure is a claim
about a named person's money.

What the pack prints, per committee:

1. **Identity** — the registered name, type, designation, city. Name the
   committee as the filing names it, and heed a `NOTE` when the registered name
   does not contain the expected label.
2. **Summary filings** — every Form 3X, with `total_receipts` and
   `total_disbursements` and its report type. This is the layer the
   Post-General report lands in. **Read the `30G` rows**: that is the report
   which makes this piece possible.
3. **Musk itemized receipts** — Schedule A rows for Musk's own names only.
   A zero row count is a **finding, not an error**: it means the summary reports
   money the itemization has not reached.
4. **Independent expenditures** — Schedule E, by candidate, support or oppose.
5. **`coverage:`** — how many requests and rows. A pack that inspected nothing
   says so, and then you have nothing to write.

If a source prints `SOURCE UNAVAILABLE`, that beat of the piece states the gap
rather than filling it. A piece with a named gap is honest; a piece with an
invented number is not.

## What the corpus already published — link it, do not re-report it

These are on the site. The piece's job is the **total and the verdict**, not the
rediscovery of the contributions:

- **"A Loss Is Not a Refund"** (`/posts/civics/a-loss-is-not-a-refund/`) — the
  failure-is-not-an-alibi argument, with the filings read on 2026-11-05: Texas
  PAC's $158,000,000 Q3 receipts against a zero-row Schedule A, $181,850,225 in
  independent expenditures through 10/26, America PAC's $50,326,939 itemized,
  and the final-week $15.3M push. Reuse a figure from it only if the pack prints
  the same figure today; if the Post-General filing changes one, the new number
  wins and the piece says the earlier reporting was incomplete.
- **"A Fix the Court Cannot Undo"** (`/posts/civics/a-fix-the-court-cannot-undo/`)
  — the structural repair. Link it as the follow-on; do not re-argue it.
- **"Who Chooses the Choices"** (`/posts/civics/who-chooses-the-choices/`) — the
  diagnosis. Link it.
- **"Elon Musk and the Engineering of Chaos"** (`/posts/essays/elon-musk-and-the-engineering-of-chaos/`)
  — the administration piece. This is the election piece; do not re-run DOGE.

## The itemization question, which is this piece's actual finding

Two filings disagree with the coverage, and the disagreement is the story:

- `senate-race-report-2026-10-18.md` cites AP for "Musk gave $158 million to the
  Senate Leadership Fund." That committee's **itemized** Schedule A on
  2026-11-05 held two Musk receipts totalling **$10,000,000**. The $158 million
  appeared as **Texas PAC's** Q3 *summary* receipts.
- So the sentence in the October report and the itemization describe different
  things. The Post-General report is the first filing that could close the gap,
  by itemizing the payer.

**What you do with that:**

- Read the pack. If the itemized receipt now names the payer, say so, quote the
  filing's own figures, and date the finding.
- If it still does not, say exactly that: the summary reports the money, the
  itemization has not reached the payer, and the routing is described by
  reporting rather than by the schedule. Do not launder a press description into
  "the filing shows."
- **Do not edit `senate-race-report-2026-10-18.md` or any other published file.**
  You write one article. If the filing contradicts the October sentence, the
  article says what the filing shows and links it; correcting the older piece is
  a separate, manual decision.

## Angle and structure

The brief recommends its angle 1 (**the coat check**) with angle 3's closing
verdict (**the purchase order**), and angle 2 (**the price of a seat**) as a
table inside rather than the spine. Follow that.

1. **The lede** — a bold **Question:** / **Answer:** pair. The question is what
   the money came to and what it bought; the answer is a verdict, not a summary.
2. **What the money came to** — the cycle total across the vehicles the pack
   covers, with each committee's own summary figure beside it. Say which report
   each number comes from, and name the report type. If a committee's itemized
   Musk money and its summary receipts differ, show both and explain the
   difference rather than choosing silently.
3. **The coat check** — money enters one committee and leaves it the same size,
   for one state. What an intermediary does to accountability: the payer's name
   stops being attached to the expenditure. This is the piece.
4. **The purchase order** — what the money asked for and what it got, race by
   race, from the Schedule E rows and the called results. **If a race is still
   uncalled, report the uncalled state.** Do not project, and do not write "likely."
5. **The price of a seat** — one table: cost per vote in the races the money
   entered, against the comparables the sources support. A table, not a section
   of prose.
6. **The strongest objection, answered** — the best case for "it didn't work, so
   it doesn't matter," met in argument. This is where the piece earns its
   hearing.
7. **Sources** — every linked claim, in the piece's own citation apparatus.

**No ad-hominem.** The subject's personal conduct, habits and character are out,
even where they are true and public. A person appears as the actor in an event,
never as the object of a verdict. The rule and its reason are in
`skills/essay-watch.md` under "No ad-hominem, including in the headlines it
quotes": character is the exit a reader takes for free, and it is a *true* exit,
which is what makes it useful to the side you are arguing against.

## House style

- Tone: personal stakes, historical context, contemporary urgency. Not yelling,
  not lecturing. Think *with* the reader.
- A figure that changes after publication is a figure the reader cannot check.
  Attribute every number to the filing it came from, with its report type and
  period.
- Em-dashes: no more than 3 in the prose you write. Not counted: a dash inside
  quotation marks, and a dash standing as a date or number range (the en-dash is
  the right mark there). `python3 scripts/check-emdashes.py --file <path>`.
- **Never end a sentence with a preposition**, in body prose or in `title`,
  `description` and `hero_caption`. `python3 scripts/check-prepositions.py --file <path>`.
- A direct quotation carries a link that contains the quoted wording, verified by
  fetching it. A quotation whose wording cannot be linked is attributed in prose
  instead, without quotation marks.
- **NEVER construct a URL.** Fetch it, confirm it is the page being cited, then
  write it. If a source cannot be retrieved, cite it in prose without a link.
- **Anchor text names the thing cited.** `[FEC filing, October 15](url)`, never
  `[text](url)` or `[here](url)`: the online link gate compares your anchor
  against the fetched page's own title, and a placeholder leaves nothing to
  compare.
- Closing attribution line, exactly:
  `*PRH | [huffmanwrites.org](https://www.huffmanwrites.org) | © Philip Huffman*`

## The plate (fixed, copied verbatim, do not generate one)

This piece carries plate **152**, commissioned with the job. Copy these four
fields byte for byte:

```yaml
hero_desktop: "img/articles/152-musk-money_16x9.webp"
hero_mobile: "img/articles/152-musk-money_4x5.webp"
hero_alt: "A book of pale marble lies open on a dark polished stone table, its blank pages faintly veined and edged in gold, a scatter of small gold counters and gold dust resting in the gutter beneath it, against a deep midnight navy darkness."
hero_caption: "The accounting is written after the fact."
```

Do not invent, edit, or regenerate them. The runner's frontmatter gate compares
all four against `152-musk-money` and fails on any other value.

## Output

- File: **`content/posts/civics/the-musk-money.md`**. The `civics` section: this
  piece sits in the sequence the other three already occupy, and it is not a
  SendFox newsletter.
- Frontmatter:
  ```yaml
  ---
  title: "<the piece's own title; no date in it, it is not an installment>"
  description: "<one sentence naming the total and the verdict>"
  date: 2026-12-06T09:00:00-06:00
  author: Philip Huffman
  lastmod: 2026-12-06T09:00:00-06:00
  draft: false
  featuredOnHome: true
  hero_desktop: "img/articles/152-musk-money_16x9.webp"
  hero_mobile: "img/articles/152-musk-money_4x5.webp"
  hero_alt: "<the hero_alt above, verbatim>"
  hero_caption: "The accounting is written after the fact."
  tags:
    - civics
    - politics
    - elections
    - money
  ---
  ```
- **`draft: false` is required.** This publishes on the run; a `draft: true` here
  is a gate failure, because the commit and push would succeed and the deploy
  would carry nothing.
- **`featuredOnHome: true` is required.** The home feed shows five posts and
  takes them from flagged posts only; without it the piece publishes and reaches
  no reader from the home page.
- **The `date` must not be ahead of the wall clock.** Hugo's `buildFuture: false`
  silently skips a future-dated page: the build succeeds and the page is simply
  absent. Run `date -u` before writing the stamp, and leave it behind that clock.
- Do **not** run `hugo`, `git`, or any gate script other than the two prose
  checkers; they are outside your allow-list and the runner runs them
  immediately after this session, recording the real exit codes in the log.
  Do not claim in your summary that a gate passed.
- Do **not** commit, push, or touch SimpleBrain, `SESSION_STATE.md`, or any other
  published article. The runner owns all of that.

## After the run

`scripts/musk-money-report-runner.sh` writes the SESSION_STATE entry from the real
gate results, commits the article and the entry together, pushes, verifies the
push landed, checks the live page's own `<title>`, and mirrors the piece to
SimpleBrain. A gate failure aborts the push and reverts nothing else.

Then the job is finished: uninstall it
(`launchctl bootout gui/$UID ~/Library/LaunchAgents/com.huffmanwrites.musk-money-report.plist`)
and delete `scripts/com.huffmanwrites.musk-money-report.plist`. A scheduled no-op
still logs a line every December 6 and still occupies a row in the table.
