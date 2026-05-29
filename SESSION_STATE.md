# Session State — HuffmanWrites

> Auto-maintained continuity file. Read this at session start before asking "where were we?"

---

## Project Overview

Hugo site (`huffmanwrites`) using PaperMod theme. Domain: huffmanwrites.org  
Primary content: books (Stoicism/civics), standalone articles, weekly newsletters.

---

## Completed (Previous Sessions)

### Hero Images — Articles
- **10 article hero image pairs** delivered to `static/img/articles/`
  - Files: `1 ror`, `2 ipd`, `3 lfg`, `4 ans`, `5 woke`, `6 fragile`, `7 pbd`, `8 rcs`, `9 coj`, `10 albania` (each with 16x9 + 4x5 variants)
- **Responsive hero layout** added via `layouts/_default/single.html`
  - `<picture>` element with mobile/desktop source switching at `767px`
  - `hero_desktop`, `hero_mobile`, `hero_alt`, `hero_caption` frontmatter fields
- **Hero CSS** added to `assets/css/phbooks.css`: `.post-hero`, `.post-hero-img`, `.post-hero-caption`
- **All 10 posts wired** with frontmatter (alt text + captions from `image-assignments.md`)

### Content Cleanup
- **Deleted 7 empty non-Constitution stubs**
- **Wrote content for 9 Constitution stubs** (tiered: First Amendment = full essay; others = medium/shorter explainers)
- **Kept** `all-my-books.md` as functional alternate entry point to `/books/`

### Book Infrastructure (Previous Sessions)
- `layouts/books/single.html` — hero image + book cover + blurb + metadata
- `layouts/books/section.html` — book listing page
- `layouts/shortcodes/book.html` + `book_catalog.html` — cover grid shortcodes
- `assets/css/phbooks.css` — `.book-caption`, `.hero-caption`, `.book-media`, etc.
- All 9 books have `hero_caption` (for hero) and `image_caption` (for cover)
- All 9 `{{< book >}}` shortcodes in `content/books/_index.md` have `caption="..."`

### Image Assignments
- All article hero image pairs generated and wired as WebP
- All newsletter hero image pairs generated and wired as WebP
- `hero-image-workflow.md` skill in `skills/` documents generation conventions

### Content Cleanup
- Deleted 7 empty non-Constitution stubs
- Wrote content for 9 Constitution stubs
- Kept `all-my-books.md` as functional alternate entry point to `/books/`

### Maintenance — May 22, 2026
- Replaced `assets/img/books/on-proportion-v3.jpg` and `unstuck-v3.jpg` with updated cover images
- Rebuilt with `hugo --minify`; Hugo regenerated webp versions with new hashes for both books
- No gallery or template changes needed — book shortcodes use `resources.Get` to auto-process source JPGs
- Added subtitle "Growing up with the Cold War" to On Proportion: regenerated cover from LaTeX (`cover.md` subtitle field), updated site cover JPG, added `subtitle:` frontmatter to book detail page (`content/books/on-proportion/index.md`), updated catalog shortcode in `content/books/_index.md`
- Fixed subtitle alignment on cover: patched `generate_cover.py` line 1023 to use `title_center_x` instead of `center_x` so subtitle follows the same `hc_front_title_offset_x_inches` shift as the title; regenerated cover and updated site JPG
- Adjusted author name positioning: HC shifted right from -0.20 to +0.125, PB from 0.00 to +0.325; title offset adjusted to -0.30 HC, +0.05 PB; all covers regenerated

### Maintenance — May 21, 2026
- Fixed CSP `form-action` to allow SendFox newsletter signups
- Added `lastmod` frontmatter to all 26 content files missing it (git-based dates)
- Fixed spelling/grammar in 8 posts (doubled words, typos, missing colon, wrong title)
- Added `fetchpriority="high"` to hero images in `single.html` and `books/single.html`
- Updated SESSION_STATE.md to reflect current project reality
- Updated 5 book covers from LaTeX cover/assets/base.png sources (Stoic Citizen, Unstuck, Stoic CGM, Misaligned, On Proportion); Hugo serves all as WebP via book.html shortcode

### Civics Essay — May 21, 2026
- Added `content/posts/civics/corruption-at-the-summit.md`
  - Title: "Corruption at the Summit: When Public Power Serves Private Gain"
  - Approx. 2,300-word researched civics essay on high-level government corruption
  - Includes clear thesis, structured supporting argument, conclusion, and APA-style sources
  - Sources include Transparency International U.S., OECD, Pew Research Center, World Bank Worldwide Governance Indicators, and Congressional Research Service on the Supreme Court ethics code
- Added the new essay to `content/posts/civics/_index.md` under "Justice and Liberty"
- Verified with `hugo --gc --minify`; build completed successfully with only existing Hugo deprecation warnings

### Hermes Essay — May 21, 2026
- Added `content/posts/essays/optimal-use-of-hermes.md`
  - Title: "The Optimal Use of Hermes: From Tool to Editorial Operation"
  - Approx. 2,200-word essay on the mental model shift from treating AI as a drafting assistant to treating a persistent AI agent as an editorial operation
  - Covers skills feedback loop, delegation judgment, cron autonomy, and the unchanged limits of AI
  - Builds on the earlier "On AI as a Writing Assistant" essay with practical detail from weeks of Hermes use
  - Auto-listed by PaperMod section pages — no manual _index.md entries needed
- Verified with `hugo --minify`; build 173 pages, 0 errors

### Additional Essays — Later May 21, 2026
- Committed and pushed `content/posts/essays/AI.md` (AI history essay, ~4,370 words)
- Committed and pushed `content/posts/essays/sources-optimal-use-of-hermes.md` (sources/companion to the Hermes essay)
- Both added in commit `acfda65`; push to `main`

### Citation Validation — May 21, 2026
- Ran full citation validation pass on the AI history essay (`content/posts/essays/AI.md`)
- Findings: 6 fabrications (invented robot "Shumana", fabricated Stanford Cart developers, fake RAND report author, wrong first name for Geoffrey Hinton, hallucinated co-author names in Nature reference), wrong paper cited, wrong ages for Minsky/McCarthy, 27 missing references
- Report saved to `/Users/prh/Vault/_Inbox/citation-validation-2026-05-21.md` (Vault, not the Hugo project)

### Fix: AI.md Metadata + Sources Frontmatter — May 21, 2026
- `content/posts/essays/AI.md` was committed with content from the Hermes essay instead of the AI history essay. Overwritten with correct AI history content and proper Hugo frontmatter.
- `content/posts/essays/sources-optimal-use-of-hermes.md` was missing Hugo frontmatter entirely. Added title, description, date, author, lastmod, tags.
- Hugo build verified clean; committed and pushed as `b9509b5`.

### Unpublish: AI.md — May 21, 2026
- Set `draft: true` on `content/posts/essays/AI.md` at user request — the essay contains several factual errors (fabricated robot name, wrong developer names, hallucinated reference author names, etc.). Unpublished until corrections can be applied.
- Committed and pushed as `6b5e42e`.

---

### AI History Essay — May 26, 2026
- Full section-by-section factual review of `content/posts/essays/AI.md`
- Removed fabricated robot "Shumana", invented Stanford Cart names, fabricated RAND study author "Richard S. Lukas", and fabricated co-authors in Silver et al. and Mnih et al. references
- Corrected: SNARC (Edmonds/1951), Minsky/McCarthy ages, BDI attribution, Geoffrey Hinton name, OpenAI Five year, DQN Atari count, Strategic Computing Initiative year, AutoGen year, Brynjolfsson et al. attribution, HAL 9000 description, Rosenblatt citation, Silver et al. year/volume/pages
- Set `draft: false`; committed and pushed as `30a2e62`

## Pending / Next Actions

### 1. Newsletter Hero Images
**Status:** All 19 newsletter/digest posts have hero images wired. Done.

### 2. Book Cover Refresh
**Status:** Resolved — May 21, 2026  
- The Stoic Citizen: `tsc/cover/assets/base.png` $\\rightarrow$ `assets/img/books/stoic-citizen-v3.jpg`
- The Stoic CGM: `cgm/cover/assets/base.png` $\\rightarrow$ `assets/img/books/stoic-cgm-v4.jpg`tizen-v3.jpg`
- The Stoic CGM: `cgm/cover/assets/base.png` $\\rightarrow$ `assets/img/books/stoic-cgm-v4.jpg`oks/stoic-citizen-v3.jpg`
- The Stoic CGM: `cgm/cover/assets/base.png` $\\rightarrow$ `assets/img/books/stoic-cgm-v4.jpg`stoic-citizen-v3.jpg`
- The Stoic CGM: `cgm/cover/assets/base.png` $\\rightarrow$ `assets/img/books/stoic-cgm-v4.jpg`
- On Proportion: `proportion/cover/assets/base.png` → `assets/img/books/on-proportion-v3.jpg`
**LaTeX repo root:** `/Users/prh/Developer/LaTeX/AllMyBooks/`
**Covers served as WebP:** Hugo's `book.html` shortcode processes source JPGs through `resources.Get` + `Resize "600x webp"`, so all book covers are served as `.webp` at build time.
**Remaining books** (Letters, Stoic Backgammon, A Life Made Whole, Raise'm Right): No `base.png` in their LaTeX repos — covers left untouched.

### 3. `all-my-books` Page
**Status:** Kept, not deleted  
**Note:** Renders via `book_catalog` shortcode. Duplicates `/books/` but serves as alternate entry point. No action unless user wants to consolidate.

---

## Architecture Notes

### Key Layouts
- `layouts/_default/single.html` — all posts (articles + newsletters). Hero picture block with `fetchpriority="high"`.
- `layouts/books/single.html` — book detail pages with hero image + `fetchpriority="high"`
- `layouts/books/section.html` — book listing
- `layouts/shortcodes/book.html` — individual book cover in catalog
- `layouts/shortcodes/book_catalog.html` — grid of all books
- `layouts/partials/extend_head.html` — CSP headers, GoatCounter analytics, OG image fallback, phbooks custom CSS (SendFox form-action whitelisted in CSP)

### CSS File
- `assets/css/phbooks.css` — custom styles (post-hero, book-caption, hero-caption, book-media classes)

### Image Directories
- `static/img/books/` — book covers
- `static/img/articles/` — article/newsletter hero images; use WebP for new hero assets

### Build
- `hugo --gc --minify` builds cleanly (170 pages, 0 errors)
- Hugo v0.161.1+extended

---

## Visual Identity (Established)

- **Palette:** Parian marble textures, deep midnight navy backgrounds, glowing gold accents
- **Lighting:** Dramatic cinematic
- **Style:** Conceptual/metaphorical, not literal
- **Aspect ratios:** 16:9 for heroes, 4:5 for mobile variants
- **Captions:** Distinct from alt text. Poetic/philosophical second layer of meaning.

---

## Content Inventory

### Books (9)
unstuck, life-made-whole, stoic-citizen, stoic-cgm, misaligned, letters, stoic-backgammon, on-proportion, raisem-right

### Standalone Articles (~36)
15 with hero images wired. 20 without (some may never need them).

### Newsletters (19)
All 19 have hero images wired.

### Constitution Series (9, all written)
First Amendment (full essay), Constitution overview, Constitution's Legacy, Second, Third, Fourth, Seventh, Eighth, Fourteenth.

---

## User Preferences

- Tone: Personal stakes + historical context + contemporary urgency. Not yelling, not lecturing. Think *with* the reader.
- First Amendment gets full essay length; narrower amendments get shorter explainers.
- `hero_caption` for hero images, `image_caption` for book covers. Never mix them.
- Use WebP for new hero images.
- Keep `all-my-books.md` as alternate entry point.
- Delete empty stubs unless Constitution-related.
- Gallery link hover colors (`blue`/`red`) are intentional -- do not suggest changing them.
- Always check for spelling/grammar errors before committing and pushing.

---

## Environment Notes

- `upg` = user alias for updating tools (not available in assistant shell)
- Session continuity = this file + compacted summary
- Primary local checkout: `/Users/prh/Developer/huffmanwrites/`
- Codex may work from detached worktrees under `/Users/prh/.codex/worktrees/...`; push with `git push origin HEAD:main` when appropriate.

---

## Maintenance Log

- 2026-05-23: Sent newsletter "What We Owe the Fallen" (1 campaign(s)) via SendFox API, created Hugo page, committed and pushed.

### High-Contrast Theme — May 26, 2026
- Added toggleable neurodivergent-friendly high-contrast mode (`data-theme="highcontrast"`)
- Half-circle icon button injected into header `.logo-switches` via `extend_footer.html` (DOMContentLoaded)
- Preference persisted in `localStorage` key `"pref-hc"`; early-activation script in `extend_head.html` prevents flash on reload
- Auto-activates on `prefers-contrast: more` (system-level preference)
- Patched PaperMod's theme-toggle to clear `pref-hc` so regular dark/light toggle cleanly exits HC mode
- CSS (`assets/css/highcontrast.css`): near-black bg `#0D0D0D`, warm cream text `#F2EDD8`, gold focus rings `#FFD700`, sky-blue links, Atkinson Hyperlegible font, line-height 1.88, reduced-motion support
- Atkinson Hyperlegible added to existing Google Fonts import in `custom.css` (no extra network request)
- Committed as `528217c`
- Accent color changed from gold `#FFD700` to deep amber `#D4820A` (commit `3da4402`)

### Site Improvements — May 27, 2026
- Transitioned newsletter signup from static footer area to a high-visibility CTA block on the home page with enhanced typography and copy.
- Implemented "Start Here" curated content pathways in `content/posts/_index.md` to guide new readers through the site's core pillars (Stoicism, Civics, Essays).
- Refined Gallery (`layouts/_default/gallery.html`) by cleaning up legacy hover colors and ensuring consistent theme-based styling for gallery links.
- Mission statement kept as standalone `/mission/` page (not on home page)

### Book Catalog Layout — May 28, 2026
- Fixed book cover aspect ratio distortion on `all-my-books` page: added `height: auto` to `.phbooks-cover img` (previously only CSS `width` was set, while HTML `height` attribute from Hugo's image processing held the cover at its processed height, causing squishing)
- Resized book cover thumbnails from 60px wide to 80×120px fixed with `object-fit: cover`
- Restructured `book_catalog.html` shortcode and `phbooks.css` to use a float-right layout: cover anchored top-right, all description text wrapping to the left and below
- Hugo image resize updated from `120x` to `160x` (2× retina for 80px display)

## Book Descriptions Implementation — May 29, 2026

### Overview
Added compelling descriptions to book cards on the Books page to motivate readers to click "Learn More".

### Implementation Details
- **Book Shortcode Enhancement**: Updated `layouts/shortcodes/book.html` to include `description` parameter
- **CSS Styling**: Added comprehensive styling in `assets/css/custom.css` for book descriptions
- **Content Updates**: Added motivational descriptions to each book card in `content/books/_index.md`
- **Layout Refinement**: Created compact, professional card layout with 120×180 pixel book covers

### Change History
1. **Initial Implementation (e0b6cf9)**: Added description parameter and basic styling
2. **CSS Specificity Fix (3c2337b)**: Enhanced CSS to address visibility issues
3. **Aggressive CSS Fix (98d1d73)**: Added !important rules to ensure visibility
4. **Extreme Visibility Fix (c09a219)**: Added debugging visuals and test page
5. **Final Layout Refinement (9942bf5)**: Created compact, professional layout with 120×180 covers

### Results
✅ **COMPLETED**: Book descriptions now visible with professional, compact layout
✅ Book covers sized to 120×180 pixels as requested
✅ Clear, readable descriptions below subtitles
✅ Responsive design for all devices
✅ Motivational content to encourage "Learn More" clicks

## Last Updated
2026-05-29 (Book descriptions implementation: compact 120×180 layout, motivational content)
2026-05-28 (Book catalog: aspect ratio fix, 80×120 covers, float-right text-wrap layout)
2026-05-27 (Added Goodreads + LinkedIn social icons)
2026-05-26 (High-contrast / neurodivergent theme toggle)
2026-05-23 (Sent newsletter: What We Owe the Fallen)
2026-05-22 (SendFox newsletter automation: cron job, processing script, pending/ + archive/ directories, personal access token, SendFox API integration for Hugo page creation + campaign send + git commit/push)
2026-05-21 (CSP fix, lastmod on all content, spelling/grammar fixes, fetchpriority on heroes, newsletter hero images complete, 5 book covers refreshed from LaTeX base.png sources, researched civics essay on high-level corruption, essay on optimal use of Hermes Agent)
