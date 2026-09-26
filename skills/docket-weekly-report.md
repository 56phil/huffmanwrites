# Skill: Weekly Docket Report

A Saturday summary of the three federal dockets this site follows, produced every
Saturday at 0800 CT beginning **October 3, 2026**.

## When this runs

- Scheduled by launchd: `com.huffmanwrites.docket-weekly-report` (plist source:
  `scripts/com.huffmanwrites.docket-weekly-report.plist`; runner:
  `scripts/docket-weekly-report-runner.sh`).
- The runner invokes Claude Code headless in this repo with this skill.
- **The job's first scheduled run is Saturday, October 3, 2026.** The runner
  guards this: before that date it exits without running, so the job can be
  installed today without producing a report on Saturday, September 26. October
  3 *is* a Saturday, so the guard and the request line up.
- If a report for today's date already exists, update it in place (same-day
  re-run).

## Provider policy (Philip, 2026-09-06)

- **No Anthropic or OpenAI resources.** The only AI API keys available are FAL
  and Ollama. Do not call api.anthropic.com, api.openai.com, or any
  Anthropic/OpenAI endpoint.
- The model runs on **Ollama, local or cloud**. The runner points at the local
  Ollama daemon (`http://localhost:11434`), which serves both local models and
  `:cloud` models; model `deepseek-v4.1-flash:cloud` (must match `ollama list`
  exactly). Auth uses `OLLAMA_API_KEY` from `.zshrc`; the runner extracts it
  because launchd does not source the shell.
- FAL is available for images. This report does not generate one: it carries the
  **series plate** (see below), a fixed pair reused every week.

## Mission

Produce a fact-checked, house-style SUMMARY of the week in the three dockets,
and file it as a **draft** in the site's digest section for Philip to review,
edit, publish, or discard. Do NOT commit, push, send, or copy anything.

## The three dockets

| Key | Case | Where | What it decides |
|---|---|---|---|
| `beatty` | *Beatty v. Trump*, No. 1:25-cv-04480 (CRC) | D.D.C. (Judge Cooper) | Kennedy Center: whether a board can undo by vote what a statute established, and whether the Board's closure decisions stand |
| `phang` | *Phang v. Blanche*, No. 1:26-cv-01417 (EGS) | D.D.C. (Judge Sullivan) | Epstein Files Transparency Act: whether a disclosure law binds the department it names |
| `cadc` | *Phang v. Blanche*, D.C. Cir. No. 26-5299 (consol. 26-5334) | D.C. Circuit | Where both questions get answered on appeal; the stay ruling issues here |

## Step 1 — Get the week's filings from the script. Do not fetch the dockets by hand.

First, read last week's report if one exists, newest first:

```
ls content/posts/essays/docket-report-*.md
```

That is the authoritative carry-forward baseline. Where it and the registry
disagree about a case's posture, the **published report wins** — it was checked
at write time and the registry may lag. Never restate a case's posture from
memory; carry it forward from the last report and then correct it against this
week's filings.

Then get the week's filings:

```
python3 scripts/check-docket.py --report
```

This prints, for each case, everything filed in the window, the calendar dates
the window covered, and the calendar ahead. It is the spine of the report. Use it.

- `--days N` changes the window (default 7, which is the weekly cadence).
- `--since YYYY-MM-DD` sets an explicit start; overrides `--days`.
- `--ahead N` sets how far forward the calendar looks (default 7).
- `--case beatty` (repeatable) restricts to one case.
- `--json` for structured output.
- `--today YYYY-MM-DD` to test what a past Saturday would have shown.

**Why the script and not the docket pages.** The report must be reproducible and
the same script backs the twice-daily watcher, so the case registry in
`scripts/check-docket.py` is the single source of truth for what is watched. It
also carries the `known` map: a one-line note for each ECF number, so the report
names what ECF 91 *is* instead of printing a bare document number.

**The `known` map is the registry's memory and it only grows one way.** A filing
that appears with no note is a filing the registry has not been told about, and
the note is only as good as the last time someone read the document. So when a
filing matters, add its line to the `known` map for the relevant case as part of
this job — one sentence, what the document says, not what it is titled. That is
what makes next week's report cheaper than this week's and keeps the twice-daily
alert intelligible. Never write a note for a document you have not read.

**Two things the script does, and one it deliberately does not.**

- It reports every filing in the window, **oldest first**, including the minute
  orders. Judge Sullivan sets deadlines and schedules briefing by minute order,
  so a week that looks quiet on ECF numbers can be the week the case moved.
- It lists the **PDF URL the feed itself supplied** for each filing that has a
  RECAP copy, marked `([PDF](...))`. That link was observed, not constructed,
  so it is safe to cite.
- **It does not read the documents.** The one-line note is a pointer. You must
  open the substantive filings and read them. Budget your time for that: in a
  typical week two to four filings carry the story and the rest are procedural.

A **`Coverage warning`** in the output means the feed's oldest entry is newer
than the window start, so the feed cannot prove the window is complete. Say so
in the report rather than presenting a partial week as a full one.

## Step 2 — Read the primary documents.

For each filing that carries the story, fetch its PDF and read it. The URLs come
from `--report` output.

- **Verify the document by its own header**, not by the URL alone. A RECAP PDF's
  first page reads `Case 1:25-cv-04480-CRC Document 77 Filed 09/15/26`. Confirm
  that header names the case and the ECF number you think you are reading. A
  `200` is not proof: the single most dangerous failure in this repo is a URL
  with the right domain and the right ID that lands on the wrong document.
- `pdftotext -layout` for extraction. If you search extracted text for a
  quotation, use an **ordered word-window check**, not a literal substring test:
  running page headers interleave mid-sentence and mid-word.
- A filing with no PDF in the feed is sealed, not-yet-scraped, or a minute entry
  with no document. If it matters and you cannot read it, say that in the report
  rather than describing it from the docket summary alone.

## Step 3 — Check coverage.

Search for reporting on the week to find (a) anything the docket does not show,
such as an oral argument scheduled outside the docket, and (b) how the coverage
misframes the filings. The site's standing position is that **the docket is more
reliable than the coverage**, so where they conflict, the docket wins and the
report may say so.

- Cite coverage as coverage; cite the filings as the record.
- Every load-bearing claim (dates, names, numbers, quoted language) MUST be
  verified against the document or a source, with a link in the piece's own
  citation apparatus.
- **NEVER construct a URL.** Write a link only after fetching the page and
  confirming it is the thing cited.

## House style

- Tone: personal stakes + historical context + contemporary urgency. Not
  yelling, not lecturing. Think *with* the reader.
- This is a **summary**, not a data dump. Prose is the spine; the list of filings
  is evidence, not the piece. A reader should finish it knowing what changed and
  why it matters.
- Open with a bold **Question:** / **Answer:** pair framing the week.
- Em-dash limit: no more than 3 in the prose you write. Not counted: a dash
  inside quotation marks, and a dash standing as a date/number range (the
  en-dash is the right mark for a range; an em-dash there is a typo). Count with
  `python3 scripts/check-emdashes.py --file <path>`.
- **Never end a sentence with a preposition** (house rule, 2026-09-25). Applies
  to body prose and to the frontmatter display fields (`title`, `description`,
  `hero_caption`).
- A quotation from a translated work names the translator, the translation, and
  the year. Every direct quotation carries a resolvable link that contains the
  quoted wording.
- Closing attribution: `*PRH | [huffmanwrites.org] | © Philip Huffman*`.

## Report structure

1. **The lede** — a bold **Question:** / **Answer:** pair naming the week's most
   consequential development across the three dockets.
2. **The week's filings** — a short prose pass over what was filed, in order of
   significance, with the ECF number and date for each. Then the complete filing
   list for the week, one line per filing. A week with few filings says so; a
   week with none is a finding ("nothing moved, and here is why that matters").
3. **A section per docket.** State where each case stands in one or two
   sentences — the operative orders, what remains live — then the week's
   movement and what it changes. Carry forward the standing posture so a reader
   who missed last week is not lost.
4. **What to watch next week** — the calendar ahead, with dates. This is the
   part for which a weekly reader subscribes.
5. **Sources** — every linked claim, in the piece's citation apparatus.

## The series plate (fixed, copied verbatim — do not generate one)

Every Docket Report carries the **same** hero pair, commissioned once for the
series and reused for every weekly installment, the way a masthead is reused. It
is plate **104** and it is not a per-week choice:

```yaml
hero_desktop: "img/articles/104-docket-report_16x9.webp"
hero_mobile: "img/articles/104-docket-report_4x5.webp"
hero_alt: "A tall vertical stack of thick carved marble ledgers and sealed folios rises on a dark surface in deep midnight-blue darkness, pale Parian stone veined with fine grey marbling and weathered at the corners. One volume near the middle of the stack is drawn slightly out, and a narrow blade of intense amber-gold light spills from the opening gap and pools on the surface below."
hero_caption: "The record accumulates. One entry opens."
```

Copy these four fields exactly. **Do not invent, edit, or regenerate them** — put
them in the frontmatter byte-for-byte as written above. The plate belongs to the
series, not to the week, so two reports carrying the same image is the intended
result. Philip, 2026-09-26: "let's do for the other weekly reports what you did for
the Chiefs report by giving them their own hero images."

## Output

- File: `content/posts/essays/docket-report-YYYY-MM-DD.md` (date = run date).
  The `essays` section, mirroring the Senate race report: this is a dated
  reviewable piece, not a SendFox newsletter, and the digests section is wired
  to newsletter sends.
- Frontmatter:
  ```yaml
  ---
  title: "Docket Report: <Month Day, Year>"
  description: "One sentence naming the week's most significant development."
  date: <run time, CT>
  author: Philip Huffman
  lastmod: <same as date>
  draft: true
  hero_desktop: "img/articles/104-docket-report_16x9.webp"
  hero_mobile: "img/articles/104-docket-report_4x5.webp"
  hero_alt: "<the hero_alt above, verbatim>"
  hero_caption: "The record accumulates. One entry opens."
  tags: [civics, essays, law]
  ---
  ```
- Date guard: the `date` must never be in the future relative to the wall clock
  when the file is written. Hugo's default `buildFuture: false` silently skips
  future-dated content — the build succeeds and the page is simply absent, which
  is the failure that hides. At an 0800 CT run, stamp the run time; do not round
  it forward.
- The four **series-plate hero fields** (above) are required and are copied verbatim; the runner's `scripts/check-hero-paths.py` gate fails if a path names no file. No newsletter/sendfox fields.
- Verify: do NOT run `hugo` or the gate scripts yourself; they are not in your
  allow-list and the runner does them immediately after this session ends,
  recording the real results in the log. Do not claim in your summary that a
  gate passed. The runner runs two builds (production, and `--buildDrafts` to a
  scratch destination so the draft is actually rendered) plus the offline
  content gates.
- Leave the file uncommitted. Do NOT copy to SimpleBrain (that happens at
  publish). Do NOT commit or push.

## After the run

The report is a draft. Philip decides whether to publish. If he publishes it,
the normal publish path applies: the SimpleBrain flow, the SESSION_STATE entry,
one commit. That is not this job's work.
