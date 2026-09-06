# Skill: Post-Election Senate Report

Capstone article on the 2026 Senate election results, published the morning
after Election Day (November 4, 2026). Philip requested this on September 6,
2026. It closes the Senate Race Report series (weekly runs ended November 1;
the runner self-disabled after November 2).

## When this runs

- **Election Day: Tuesday, November 3, 2026.** The report is drafted the
  evening of November 3 / morning of November 4, after results are in.
- Not scheduled by launchd — this is a one-off, run on Philip's word the
  morning after. (The senate runner self-disables after Nov 2 and must NOT be
  repurposed; this is a manual run.)
- If Philip asks for it before results are final, draft what is known and
  flag what is not.

## Context (baseline as of September 6, 2026 — verify everything on the night)

- **The math going in:** Democrats needed a net gain of four. A 50-50 Senate
  belongs to Vance (R). DDHQ modeled 51 R / 49 D; Kalshi ~53% R; Polymarket
  ~51% D. Six toss-ups: Texas, Ohio, Iowa, Michigan, Alaska, Maine.
- **The consensus path:** hold the defense (MI, GA, MN, NH), flip North
  Carolina (Cooper ~91%), win two of the coin flips (OH, TX), find a fourth
  seat in the long tail (ME, AK, IA, NE, KS).
- **The Kansas connection:** Hamilton was the margin seat. If the top three
  slipped, Kansas (or Nebraska through Osborn) decided 51.
- **The 35 races:** 13 D-held (9 safe + GA, MI, MN, NH), 22 R-held (NC, OH,
  TX, ME, AK, IA, NE, KS, FL, LA, MS, MT, SC + 9 safe R).
- **Complications to expect:** Alaska ranked-choice tabulation (may take
  days), Louisiana and Georgia runoffs (Dec 5 / Dec 2026) if no majority,
  recounts in close races. The control picture may be incomplete on Nov 4 —
  the report must say so plainly rather than declare a winner early.

## Research phase (night of Nov 3 / morning of Nov 4)

1. **Results:** every competitive race — NC, OH, TX, ME, AK, IA, NE, KS, MI,
   GA, MN, NH, plus FL, LA, MS, MT, SC. Use AP, state election boards, and
   Decision Desk HQ. Corroborate with at least two sources.
2. **Control:** which party holds the Senate, by what margin, and whether any
   race is uncalled (ranked-choice, runoff, recount). The single most
   important fact in the piece.
3. **The paths that materialized:** which of the consensus paths actually
   happened. Did the defense hold? Did NC flip? Which coin flips landed?
4. **The Kansas story:** did Hamilton win, lose close, or lose big? The
   September polls (GSG 44-43) vs. the result. The 1932 history (last Dem
   senator), the 2014/2020 September-poll-then-double-digit-loss pattern.
5. **The environment:** national popular vote, generic ballot, turnout,
   presidential approval — the context that explains the result.
6. **Surprises:** any race that defied the forecasters, either direction.
7. **What it means:** the practical consequences — committee control, the
   filibuster, confirmations, the 2028 map.

## House style

- Tone: personal stakes + historical context + contemporary urgency. Not
  yelling, not lecturing. Think *with* the reader.
- Open with the house lede: a bold **Question:** / **Answer:** pair framing
  the result and what it means. Model on the weekly reports and
  `the-path-to-51.md`.
- Em-dash limit: no more than 3 per file. Prefer commas, colons, semicolons,
  or splitting sentences.
- Every load-bearing claim (winners, margins, dates, control math) MUST be
  verified against a source; cite with `[^n]` footnotes and a `## Notes`
  section. Flag anything unverifiable or uncalled.
- Closing attribution: `*PRH | [huffmanwrites.org](https://huffmanwrites.org) | © Philip Huffman*`
- This is an ARTICLE, not a data dump: prose is the spine. One compact table
  of the competitive results (state, winner, margin, called/uncalled) is
  appropriate; do NOT include a full 35-row table.

## Article structure

1. **The lede** — Question/Answer pair: who won the Senate, by what margin,
   and what it means.
2. **The result** — the control math, stated plainly. Which races were
   called, which are pending (ranked-choice, runoff, recount).
3. **The defense** — did the 13 D-held seats hold? MI, GA, MN, NH in detail;
   the safe nine in a sentence.
4. **The offense, tiered** — NC, OH, TX, ME, AK, IA, NE, KS, and the rest.
   One short paragraph per competitive race: winner, margin, what it means.
5. **The Kansas story** — the margin seat, the 1932 history, the September
   polls vs. the result. This is the emotional and analytical core of the
   piece for Philip's readers.
6. **The math that materialized** — which path won, which didn't. The
   forecasters vs. the result (were the models right?).
7. **The close** — what the result means for the country, the next two
   years, and the 2028 map. Personal stakes, forward look.

## Hero image (FAL, not OpenAI)

- **Next ID:** 71 (highest existing is 70, reserved for the Kansas debate
  piece). Slug: `senate-election-2026-results`.
- **Files:** `static/img/articles/71-senate-election-2026-results_16x9.webp`
  and `_4x5.webp`.
- **Aesthetic (locked):** Parian marble textures, deep midnight navy
  backgrounds (#131E39), glowing gold accents (#D4820A), dramatic cinematic
  lighting (chiaroscuro), gold filigree, conceptual/metaphorical — NOT
  literal. No text in the image.
- **FAL endpoint:** `POST https://queue.fal.run/fal-ai/flux/dev` with
  `Authorization: Key $FAL_KEY` (keychain `huffmanwrites-fal` or
  `~/.secrets`), JSON `{"prompt": "...", "image_size": {"width": W, "height": H},
  "num_inference_steps": N, "output_format": "png"}`.
  - 16:9: 1536×1024. 4:5: 1024×1280.
  - Status: `GET https://queue.fal.run/fal-ai/flux/requests/<id>/status`
    (NO `/dev/` segment — that path returns 405). Result:
    `GET https://queue.fal.run/fal-ai/flux/requests/<id>` → `images[0].url`.
  - **4:5 is slow (~2.5 min): run with cell timeout disabled (`timeout: 0`).**
- **Post-process:** crop 16:9 to 1365×768, 4:5 to 896×1120, convert to WebP
  q92 via `cwebp`.
- **Wire frontmatter:** `hero_desktop`, `hero_mobile`, `hero_alt`,
  `hero_caption` (poetic/philosophical, matching the theme).
- **Gallery:** add a `data/gallery.yml` entry (image, title, caption, link).

## Publish flow (one commit, pushed once)

1. Write the piece with `draft: true` first; review it.
2. Flip `draft: false`; set `date`/`lastmod` to 2026-11-04. **Date guard:**
   never pre-date; Hugo's `buildFuture: false` silently skips future-dated
   content.
3. Clean build: `hugo --gc --minify` — must be 0 errors.
4. Add the SESSION_STATE.md maintenance entry (November 4).
5. Single commit: content file + hero WebPs + `data/gallery.yml` +
   SESSION_STATE entry. Push once. No follow-up commits.
6. Copy the published post to `~/SimpleBrain/raw/` (flat directory):
   `cp content/posts/essays/senate-election-2026-results.md ~/SimpleBrain/raw/`.

## SimpleBrain Translate Loop

1. Run the translate flow on the raw file (per `~/SimpleBrain/translate.md`).
2. Result goes to `wiki/reports/` (it is a report, not an article).
3. Move the raw file to `~/SimpleBrain/raw/archive/` (never delete).
4. Commit in the SimpleBrain repo, push.

## Fallbacks

- **Results incomplete (ranked-choice/runoff/recount):** do not declare a
  winner. State what is called, what is pending, and the scenarios. The
  report is still publishable — the pending races are part of the story.
- **Election contested or delayed:** pause, tell Philip, and offer a
  preview/explainer instead. Do not publish a fabricated result.
- **FAL key fails:** stop and flag it; do not retry auth errors. Philip
  supplies a new key.
