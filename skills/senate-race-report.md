# Skill: Senate Race Report

Weekly report on all 35 U.S. Senate races in the 2026 cycle (33 regular Class 2 seats plus the Florida and Ohio special elections), produced every Sunday at 0700 CT through November 2, 2026. Election Day is November 3, 2026.

## When this runs

- Scheduled by launchd: `com.huffmanwrites.senate-report` (plist source: `scripts/com.huffmanwrites.senate-report.plist`; runner: `scripts/senate-report-runner.sh`).
- The runner invokes Claude Code headless in this repo with this skill. Runs: Sundays September 6 through November 1, 2026 (9 runs). The runner self-disables after November 2, 2026.
- If a report for today's date already exists, update it in place (same-day re-run).

## Mission

Produce a fact-checked, house-style ARTICLE on the state of every Senate race, what changed in the past week, and the current math for control of the Senate. The article is a DRAFT for Philip to review, edit, and publish. Do NOT commit, push, send, or copy anything.

## House style

- Tone: personal stakes + historical context + contemporary urgency. Not yelling, not lecturing. Think *with* the reader.
- This is an ARTICLE, not a data report: prose is the spine. Model the voice and structure on `content/posts/essays/the-path-to-51.md` (the Senate-race essay: the math, the tiers, the paths) and `content/posts/essays/kansas-senate-2026-the-case-for-adam-hamilton.md` (the Kansas deep-dive).
- Open with the house lede: a bold **Question:** / **Answer:** pair framing the week's state of the race for control, exactly as the two canonical essays do.
- Em-dash limit: no more than 3 per file. Prefer commas, colons, semicolons, or splitting sentences.
- Every load-bearing claim (dates, names, figures, ratings, poll numbers, fundraising) MUST be verified against a source; cite with `[^n]` footnotes and a `## Notes` section. Flag anything unverifiable.
- Closing attribution: `*PRH | [huffmanwrites.org] | © Philip Huffman*`.

## The 35 races (baseline as of September 2026 — verify every name each week)

Democratic-held (13):
- Safe: Colorado (Hickenlooper), Delaware (Coons), Illinois (Durbin), Massachusetts (Markey), New Jersey (Booker), New Mexico (Luján), Oregon (Merkley), Rhode Island (Reed), Virginia (Warner)
- Georgia: Jon Ossoff (D) vs. Mike Collins (R) — Ossoff favored ~93%
- Michigan (OPEN, Peters retired): Abdul El-Sayed (D) vs. Mike Rogers (R) — D ~65%, the most competitive Democratic seat
- Minnesota (OPEN, Smith retired): Peggy Flanagan (D) favored ~91%
- New Hampshire (OPEN, Shaheen retired): Chris Pappas (D) vs. John E. Sununu (R) and Scott Brown (R) — D ~84%

Republican-held (22):
- Tier 1: North Carolina (OPEN, Tillis retired): Roy Cooper (D) vs. Michael Whatley (R) — Cooper ~91%, the anchor pickup
- Tier 2: Ohio special: Sherrod Brown (D) vs. Jon Husted (R) — near even, Husted ~55%; Texas: Ken Paxton (R) vs. James Talarico (D) — Paxton ~51%
- Tier 3: Maine: Susan Collins (R) vs. Troy Jackson (D) — Collins ~70%; Alaska: Dan Sullivan (R) vs. Mary Peltola (D) — Sullivan ~65%, ranked-choice, same-name spoiler; Iowa (OPEN, Ernst retired): Ashley Hinson (R) vs. Josh Turek (D) — Hinson ~61%; Nebraska: Pete Ricketts (R) vs. Dan Osborn (I) — Osborn ~30%, the wildcard
- Tier 4: Kansas: Roger Marshall (R) vs. Adam Hamilton (D) — Hamilton ~18%, the margin seat; Florida special (appointed Ashley Moody, R); Louisiana (Cassidy lost primary — nominee TBD); Mississippi (Hyde-Smith); Montana (Daines); South Carolina (Graham)
- Safe R: Alabama (Tuberville), Arkansas (Cotton), Idaho (Risch), Kentucky (McConnell), Oklahoma (Mullin), South Dakota (Rounds), Tennessee (Hagerty), West Virginia (Capito), Wyoming (Barrasso)

## Research phase

1. Read the previous week's report (`content/posts/essays/senate-race-report-*.md`, newest first) to carry the baseline forward.
2. Web-search the latest on every competitive race and scan the safe ones: Cook Political Report, Sabato's Crystal Ball, RealClearPolitics, FiveThirtyEight, prediction markets, FEC filings, and local/state news. Corroborate key claims with at least two sources.
3. Track: rating changes, polling movement, fundraising, endorsements, candidate news, debates, and races entering or leaving the competitive tier.

## Article structure

1. **The lede** — bold **Question:** / **Answer:** pair framing the week's state of the race for control (Democrats need a net gain of four; a 50-50 Senate belongs to Vance).
2. **What changed this week** — prose, the most important developments across all races in order of significance, with dates.
3. **The defense** — the 13 Democratic-held seats; a paragraph each on MI, GA, MN, NH; the safe nine in a sentence or two.
4. **The offense, tiered** — NC; OH and TX; ME, AK, IA, NE; KS, FL, LA, MS, MT, SC; the safe nine in a sentence. One short paragraph per competitive race.
5. **The math** — forecasters' consensus vs. prediction markets; the paths to 51; the Kansas connection (Hamilton as the margin seat).
6. **The close** — personal stakes and a forward look to Election Day, in the voice of the canonical essays.

If any race's rating changed this week, include one compact table of just those races (state, rating, change). Do NOT include a full 35-row table; that is report furniture, not article prose.

## Output

- File: `content/posts/essays/senate-race-report-YYYY-MM-DD.md` (date = run date).
- Frontmatter: `title` ("Senate Race Report: <Month Day, Year>"), `description` (one sentence, article-style), `date` (run time, CT), `author: Philip Huffman`, `lastmod`, `draft: true`, `tags: [politics, senate, essays, civics]`.
- Date guard: the `date` must never be in the future when the article is published. Hugo's default `buildFuture: false` silently skips future-dated content (the build succeeds but the page is absent). The weekly draft is dated on its run day, so publishing the same day is safe; if Philip publishes later, the date is already past and still safe. Never pre-date an article.
- No hero image (weekly text report). No newsletter/sendfox fields.
- Verify: `hugo --gc --minify` builds with 0 errors.
- Leave the file uncommitted. Do NOT copy to SimpleBrain (that happens at publish). Do NOT commit or push.

## After the election

The final scheduled run is Sunday, November 1, 2026. The runner self-disables after November 2, 2026. A post-election report is out of scope unless Philip asks.
