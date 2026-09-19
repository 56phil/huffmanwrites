# Skill: Senate Race Report

Weekly report on all 35 U.S. Senate races in the 2026 cycle (33 regular Class 2 seats plus the Florida and Ohio special elections), produced every Sunday at 0700 CT through November 2, 2026. Election Day is November 3, 2026.

## When this runs

- Scheduled by launchd: `com.huffmanwrites.senate-report` (plist source: `scripts/com.huffmanwrites.senate-report.plist`; runner: `scripts/senate-report-runner.sh`).
- The runner invokes Claude Code headless in this repo with this skill. Runs: Sundays September 6 through November 1, 2026 (9 runs). The runner self-disables after November 2, 2026.
- If a report for today's date already exists, update it in place (same-day re-run).

## Provider policy (Philip, 2026-09-06)

- **No Anthropic or OpenAI resources.** The only AI API keys available are FAL and Ollama. Do not call api.anthropic.com, api.openai.com, or any Anthropic/OpenAI endpoint; do not use the OpenAI key for anything.
- The model runs on **Ollama, local or cloud** (cloud resources are fine). The runner currently points at the local Ollama daemon (`http://localhost:11434`), which serves both local models and `:cloud` models; model `deepseek-v4-flash:cloud` (must match `ollama list` exactly). Auth uses `OLLAMA_API_KEY` from `.zshrc`; the runner extracts it because launchd does not source the shell.
- FAL (`FAL_KEY` in `.zshrc`) is available for image generation if a future report ever needs it; the weekly report does not use hero images.

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
- Tier 4: Kansas: Roger Marshall (R) vs. Adam Hamilton (D) — Hamilton ~18%, the margin seat; Florida special (appointed Ashley Moody, R); Louisiana (OPEN, Cassidy lost primary — **Julia Letlow** is the R nominee); Mississippi (Hyde-Smith); **Montana (OPEN — Steve Daines withdrew in March 2026; Alme is the R nominee)**; **South Carolina (OPEN — Lindsey Graham died in July 2026; his sister Darline Graham is the R nominee)**
- Safe R: Alabama (Tuberville), Arkansas (Cotton), Idaho (Risch), Kentucky (McConnell), Oklahoma (Mullin), South Dakota (Rounds), Tennessee (Hagerty), West Virginia (Capito), Wyoming (Barrasso)

> **Baseline corrections (verified, do not revert).** An earlier version of this file named Daines for Montana, Graham for South Carolina, and "nominee TBD" for Louisiana. Those were wrong and were corrected in the published Sept 6 report after research verification: **Daines withdrew in March 2026** (Alme is the nominee), **Lindsey Graham died in July 2026** (Darline Graham, his sister, is the nominee), and **Letlow** is Louisiana's nominee. The published weekly reports are the authoritative carry-forward baseline — when this list and a published report disagree, the report wins. Still re-verify each week; this note records what was already corrected so the error is not reintroduced.

## Research phase

1. Read the previous week's report (`content/posts/essays/senate-race-report-*.md`, newest first) to carry the baseline forward. **The published reports are the authoritative baseline; the race list above is only a starting sketch.** Where they disagree on a name, a nominee, or a rating, the report wins — it was fact-checked at write time and this list may lag. Never introduce a candidate from this list that the most recent report does not name.
2. **Get the ratings FIRST, with the script — do not try to fetch the forecasters directly.** Run:
   ```
   python3 scripts/fetch-senate-ratings.py
   ```
   This prints a markdown table of the competitive races with **Cook, IE, Sabato, RCP, DDHQ and Silver** columns, each stamped with its own as-of date. Use it for the ratings table and for the ratings claims in the prose.
   - **Why the script exists:** cookpolitical.com, centerforpolitics.org and realclearpolitics.com all return **HTTP 403** to automated fetch, so a table sourced directly "from Cook" would be uncitable. The script reads Wikipedia's aggregate ratings table instead, which carries every forecaster in its own column with per-column dates, and parses it correctly. Do not burn turns trying to fetch those three directly.
   - **Inside Elections is the exception, and the script already uses it.** `insideelections.com` serves its own 2026 ratings as JSON, and the script reads it via `urllib` (note: **curl is Cloudflare-blocked with a 403 there while `urllib` with a UA *plus a Referer* returns 200** — do not "simplify" that call to curl). Its JSON is authoritative for the IE column and carries `previous_rating` and `shift`, which the aggregate table lacks.
   - `--moves` prints the moves **Inside Elections itself reports** (previous vs current rating, with dates) across all 35 races. This is the best available answer to "what moved recently," because it survives a lost local baseline — and it is genuinely informative: as of Sept 19 it shows **12 moves this cycle**, including ME `Tilt R → Toss-up` (Sept 17), OH `Tilt R → Toss-up` and NH `Tilt D → Toss-up` (Sept 3), and NC `Toss-up → Tilt D` marked **FLIP** (Aug 6).
   - `--changes` diffs against this repo's stored baseline, which only knows moves since the baseline was first saved. Prefer `--moves` for the prose; use `--changes` to detect drift in the other five forecasters.
   - `--all` for all 35 races, `--json` for structured output.
   - **The as-of dates differ per forecaster** (Cook updates weekly, Sabato less often). Never restamp the whole table with today's date — that is a factual error. The script supplies the real dates; carry them through.
3. Web-search the latest on every competitive race and scan the safe ones: Cook Political Report, Sabato's Crystal Ball, RealClearPolitics, FiveThirtyEight, prediction markets, FEC filings, and local/state news. Corroborate key claims with at least two sources. Search results and secondary coverage *quote* the forecasters, so the paywalled/blocked pages can still be sourced that way — but the ratings table itself comes from the script.
   - **Kansas coverage:** Kansas City Star and KCUR are the preferred local sources (Philip, September 8, 2026) — check them first for Kansas race news, alongside Kansas Reflector and Sunflower State Journal.
   - **National and international context:** NPR and PBS are the preferred sources (Philip, September 8, 2026) for national and international stories that shape the races.
3. Track: rating changes, polling movement, fundraising, endorsements, candidate news, debates, and races entering or leaving the competitive tier.

## Article structure

1. **The lede** — bold **Question:** / **Answer:** pair framing the week's state of the race for control (Democrats need a net gain of four; a 50-50 Senate belongs to Vance).
2. **What changed this week** — prose, the most important developments across all races in order of significance, with dates.
3. **The defense** — the 13 Democratic-held seats; a paragraph each on MI, GA, MN, NH; the safe nine in a sentence or two.
4. **The offense, tiered** — NC; OH and TX; ME, AK, IA, NE; KS, FL, LA, MS, MT, SC; the safe nine in a sentence. One short paragraph per competitive race.
5. **The math** — forecasters' consensus vs. prediction markets; the paths to 51; the Kansas connection (Hamilton as the margin seat).
6. **The ratings table** — include the ratings table **every week**, in the "math" section. It carries the competitive races (the script's default output: Alaska, Georgia, Iowa, Maine, Michigan, New Hampshire, North Carolina, Ohio, Texas, plus any race the forecasters have moved into Tossup/Tilt/Lean), one row per race, one column per forecaster, with the **per-forecaster as-of dates** from the script beneath it. This replaces the old "only if a rating changed" rule (Philip, September 19, 2026): the table is now standing furniture of the article, not a change report.
   - Use `--changes` to find moves since last week, and **name them in the prose** — a move is still the most newsworthy thing in the section when one occurs. When no forecaster moved, say so plainly rather than implying the table is unchanged because nothing is happening; two consecutive weeks of model- and market-driven movement without a ratings move is itself the story.
   - Do not expand this into a 35-row table; the competitive set is the right size for article prose. `--all` exists if a claim needs a safe-seat rating.
   - **Explain the columns the first time the table appears**, in a line or two directly beneath it. Two of them are not self-explanatory and the reader should not have to leave the article to decode them (Philip asked what they meant, September 19, 2026):
     - **PVI** — Cook Partisan Voting Index: how far a state leans from the nation as a whole, computed from the **2020 and 2024 presidential two-party vote share**, weighted toward 2024. It measures a **historical baseline, not the current race**, and Cook says so itself: "whereas race ratings reflect our outlook for which party will win the next election ... the Cook PVI takes a longer view." It is the only backward-looking column in the table, and the weakest predictor of the nine: rank-correlating PVI against how competitive the forecasters actually call these races gives **+0.23**. It earns its place as **contrast** — it is what makes "Tossup in an `R+6` state" legible — not as a forecast. Do not present it as though it tells the reader how the race is going.
       - **Two traps that make PVI look inconsistent with margins quoted elsewhere.** (1) It is denominated in **vote share for one party, not margin**, so it is roughly **half** the size of a margin-style lean: Cook calls Texas `R+6` while Silver's partisan lean — a margin measure — calls the same state `R+11`. Both are right; they are different denominators (Silver says so explicitly in the FLIPR methodology). Never place a PVI number next to a margin figure without saying which is which. (2) It ignores **elasticity** — how hard a state swings when the nation swings. Maine is `D+4` yet its Senate seat has swung between parties; Georgia is `R+1` yet rated `Likely D`. A state's lean and its swinginess are different properties.
     - **IE** — Inside Elections, Nathan Gonzales's nonpartisan newsletter (formerly the Rothenberg Political Report). One of several forecasters, listed alongside Cook and Sabato.
     - **The rating scale**, strongest to weakest: **Solid/Safe** (not competitive) → **Likely** (clear edge, upset possible) → **Lean** (small edge, still competitive) → **Tilt** (slight edge, highly competitive) → **Tossup** (no edge). DDHQ publishes win probabilities that map onto this: Solid >95%, Likely 80–95%, Lean 65–80%, Tossup 35–65% for either party.
     - **`Tilt` is Inside Elections' own rating** — Cook, Sabato and DDHQ do not use it (Ballotpedia lists it `N/A` for all three). So a `Tilt` appearing only in the IE column is not a disagreement with the others; it is IE using a finer scale. Say so if the prose is tempted to call it one.
     - **`(flip)`** marks a rating that forecasts a change of party from the current holder.
7. **The close** — personal stakes and a forward look to Election Day, in the voice of the canonical essays.

## Output

- File: `content/posts/essays/senate-race-report-YYYY-MM-DD.md` (date = run date).
- Frontmatter: `title` ("Senate Race Report: <Month Day, Year>"), `description` (one sentence, article-style), `date` (run time, CT), `author: Philip Huffman`, `lastmod`, `draft: true`, `tags: [politics, senate, essays, civics]`.
- Date guard: the `date` must never be in the future when the article is published. Hugo's default `buildFuture: false` silently skips future-dated content (the build succeeds but the page is absent). The weekly draft is dated on its run day, so publishing the same day is safe; if Philip publishes later, the date is already past and still safe. Never pre-date an article.
- No hero image (weekly text report). No newsletter/sendfox fields.
- Verify: `hugo --gc --minify` builds with 0 errors. Do NOT run this yourself — the runner performs the
  verification build immediately after this session ends and records the result in the log (the agent's
  permission allow-list intentionally omits hugo, since an exact-match rule denies the redirect and
  `&&` compound forms you would naturally reach for). Write the article; the script verifies the build.
- Leave the file uncommitted. Do NOT copy to SimpleBrain (that happens at publish). Do NOT commit or push.

## After the election

The final scheduled run is Sunday, November 1, 2026. The runner self-disables after November 2, 2026. A post-election report is out of scope unless Philip asks.
