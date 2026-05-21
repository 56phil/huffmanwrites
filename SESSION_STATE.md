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

---

## Pending / Next Actions

### 1. Newsletter Hero Images
**Status:** All 19 newsletter/digest posts have hero images wired. Done.

### 2. Book Cover Refresh
**Status:** Resolved — May 21, 2026  
**Action:** Updated 5 book covers from latest LaTeX repo `cover/assets/base.png` sources:
- The Stoic Citizen: `tsc/cover/assets/base.png` → `assets/img/books/stoic-citizen-v2.jpg`
- Unstuck: `unstuck/cover/assets/base.png` → `assets/img/books/unstuck-v3.jpg`
- The Stoic CGM: `cgm/cover/assets/base.png` → `assets/img/books/stoic-cgm-v3.jpg`
- Misaligned: `Misaligned/cover/assets/base.png` → `assets/img/books/misaligned-v2.jpg`
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

## Last Updated
2026-05-21 (CSP fix, lastmod on all content, spelling/grammar fixes, fetchpriority on heroes, newsletter hero images confirmed complete, 5 book covers refreshed from LaTeX base.png sources, new researched civics essay on high-level corruption added with APA sources)
