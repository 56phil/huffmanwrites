# Skill: Kansas Post-Debate Piece

Standalone essay on the September 12, 2026 Kansas State Fair Senate debate
(Adam Hamilton vs. Roger Marshall), published the morning after. This is a
content decision Philip approved on September 6, 2026. Run it the evening of
September 12, after the debate ends.

## Context (grounded, as of Sept 6)

- **Debate:** Saturday, September 12, Kansas State Fair. Confirmed by both
  campaigns (Sunflower State Journal, Sept 2026; Kansas Reflector, Aug 19).
- **Candidates:** Adam Hamilton (D, pastor, Church of the Resurrection) vs.
  Roger Marshall (R, incumbent, first term).
- **Pre-debate state:**
  - Global Strategy Group poll (Aug 12-16): Hamilton 44-43.
  - Inside Elections moved Kansas Solid R → Likely R on Sept 3.
  - New super PAC (People Over Politics Action Fund) attacking Marshall on the
    Epstein files (Sunflower State Journal, Sept 2026).
  - Letter spat: Hamilton addressed his letter to Marshall in Sarasota, FL;
    Marshall answered addressing his to Hamilton at the Lake of the Ozarks, MO.
  - Marshall's record (from the Sept 1 essay): 98% Trump voting record, 2020
    certification objection, hydroxychloroquine promotion, three anti-Ukraine
    votes, Sarasota vacation home, FEC complaint over Hamilton's church
    communications.
- **History caution (must appear in the piece):** Kansas has not elected a
  Democratic senator since 1932. September polls showed competitiveness in
  2014 and 2020; Republicans won both by double digits.
- **Prior pieces:** `content/posts/essays/kansas-senate-2026-the-case-for-adam-hamilton.md`
  (Sept 1) and the Sept 6 Senate Race Report. The post-debate piece is a
  standalone sequel, not a repeat of either.

## Research Checklist (night of Sept 12)

Verify every load-bearing claim against a primary or named source before
writing. Sources to check: Kansas Reflector, Kansas City Star, KCUR, Sunflower
State Journal, Lawrence KS Times, Wichita Eagle, AP, local TV debate coverage.

1. **The debate itself:** date/time confirmed, format (moderator, length,
   topics), whether both candidates appeared, any notable moments (gaffes,
   exchanges, audience reaction).
2. **Key exchanges:** the two or three exchanges that define the night —
   quote them accurately and attribute them.
3. **Post-debate polls:** any new Kansas poll released after the debate
   (GSG, Emerson, etc.). If none, say so plainly — do not invent one.
4. **Ratings moves:** did Cook, Sabato, or Inside Elections move Kansas after
   the debate? (Inside Elections moved it Sept 3; a post-debate move would be
   news.)
5. **Money:** any new FEC filings, super PAC activity, or ad buys announced
   around the debate.
6. **The letter spat:** did either candidate reference it on stage? Did the
   campaigns release new letters?
7. **Fact-check verdicts:** did any outlet fact-check the debate? Cite their
   findings.

## Writing Conventions

- **Tone:** personal stakes + historical context + contemporary urgency.
  Not yelling, not lecturing. Think *with* the reader.
- **Structure:** the Sept 1 essay's shape works — a question/answer opening,
  thematic sections, an honest-weaknesses section, a close. The post-debate
  piece should be tighter: what happened, what it means, what it doesn't mean.
- **Em-dash limit:** no more than 3 per file. Prefer commas, colons,
  semicolons, or splitting sentences.
- **Footnotes:** numbered, named sources (publication + date), matching the
  Sept 6 report's style. Every load-bearing claim gets one.
- **Attribution line:** `*PRH | [huffmanwrites.org](https://huffmanwrites.org) | © Philip Huffman*`
- **Date guard:** publish date is September 13, 2026. Do NOT pre-date the
  file; Hugo's `buildFuture: false` silently skips future-dated content.
- **Copyedit + fact check before commit:** spelling, grammar, punctuation,
  flow, em-dash count, and every load-bearing claim verified against a source.

## Hero Image (FAL, not OpenAI)

- **Next ID:** 70 (highest existing is 69). Slug: `kansas-senate-debate-2026`.
- **Files:** `static/img/articles/70-kansas-senate-debate-2026_16x9.webp` and
  `_4x5.webp`.
- **Aesthetic (locked):** Parian marble textures, deep midnight navy
  backgrounds (#131E39), glowing gold accents (#D4820A), dramatic cinematic
  lighting (chiaroscuro), gold filigree, conceptual/metaphorical — NOT
  literal. No text in the image.
- **FAL endpoint:** `POST https://queue.fal.run/fal-ai/flux/dev` with
  `Authorization: Key $FAL_KEY` (from keychain `huffmanwrites-fal` or
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
  The gallery does not auto-populate.

## Publish Flow (one commit, pushed once)

1. Write the piece with `draft: true` first; review it.
2. Flip `draft: false`; set `date`/`lastmod` to 2026-09-13.
3. Clean build: `hugo --gc --minify` — must be 0 errors.
4. Add the SESSION_STATE.md maintenance entry (September 13).
5. Single commit: content file + hero WebPs + `data/gallery.yml` +
   SESSION_STATE entry. Push once. No follow-up commits.
6. Copy the published post to `~/SimpleBrain/raw/` (flat directory):
   `cp content/posts/essays/kansas-senate-debate-2026.md ~/SimpleBrain/raw/`.

## SimpleBrain Translate Loop

1. Run the translate flow on the raw file (per `~/SimpleBrain/translate.md`).
2. Result goes to `wiki/articles/` (it is an essay, not a report).
3. Move the raw file to `~/SimpleBrain/raw/archive/` (never delete).
4. Commit in the SimpleBrain repo, push.

## Fallbacks

- **Debate postponed/cancelled:** do not publish a fabricated account. Pause,
  tell Philip, and offer a pre-debate preview piece instead.
- **No post-debate polls:** state that plainly in the piece; the debate
  coverage and ratings/money news carry it.
- **FAL key fails:** stop and flag it (per the ninety-days skill's policy);
  do not retry auth errors. Philip supplies a new key.
