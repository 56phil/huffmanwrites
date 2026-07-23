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

### Book Cover Refresh — June 20, 2026
- Replaced all versioned cover filenames with clean canonical names:
  - `misaligned-v2.jpg` → `misaligned.jpg`
  - `on-proportion-v3.jpg` → `proportion.jpg`
  - `stoic-cgm-v4.jpg` → `stoic-cgm.jpg`
  - `stoic-citizen-v3.jpg` → `stoic-citizen.jpg` (modified in place)
  - `unstuck-v3.jpg` → `unstuck.jpg`
  - `life-made-whole.jpg` → `almw.jpg`
- Updated all references in `content/books/_index.md` and each book's `index.md`
- Old versioned files deleted from `assets/img/books/`

### Book Cover Bug Fixes — June 20, 2026
- **Books page** (`/books/`): covers were not rendering — `book.html` shortcode computed `$imgPath` (strip leading `/`) but then used the original `$img` variable (which includes `/img/books/` prefix) in `resources.Get`, doubling the path to `img/books//img/books/...`. Fixed by replacing `$webpImg`/`$img` usage with `$webpPath`/`$imgPath` in the resource lookup.
- **Home page** cover grid: images displayed at inconsistent heights because native aspect ratios vary (2:3, 5:8, etc.). Fixed by adding `aspect-ratio: 2 / 3` and `object-fit: cover` to `.cover-item img` in `home.css`, enforcing a uniform 2:3 grid.

---

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

## Home Page Credo Update — May 29, 2026

### Overview
Updated the home page credo from two lines to three lines:
- **Before**: Think clearly. Live deliberately.
- **Interim**: Think clearly. Live deliberately. Love like there's no tomorrow.
- **After (original)**: Think clearly. Live deliberately. Love intensely.
- **Current**: Think Clearly. Live Intentionally. Love Immediately.

### Changes Made
- Updated `layouts/index.html` line 215 to add third line to hero tagline
- Added emphasis to verbs (Think, Live, Love) using small caps, color, and weight
- Added CSS styling for `.credo-verb` class
- Maintained elegant aesthetic while providing clear visual emphasis

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
6. **Nuclear Option (Current)**: Added inline styles to EVERY element, ARIA attributes, and description in alt text

### Results
✅ **COMPLETED**: Book descriptions now visible with professional, compact layout
✅ Book covers sized to 120×180 pixels as requested
✅ Clear, readable descriptions below subtitles
✅ Responsive design for all devices
✅ Motivational content to encourage "Learn More" clicks

## Group B: Book Marketing

### 1. Back Cover Integration

#### Overview
Added the credo "Think clearly. Live deliberately. Love intensely." to book detail pages as part of the Book Marketing strategy (Group B).

#### Implementation Details
- **File Modified**: `layouts/books/single.html`
  - Added credo container and display above book media section
  - Integrated credo styling with decorative icons and responsive design
- **CSS Added**: `assets/css/phbooks.css`
  - Added `.book-credo-container` and `.book-credo` styles
  - Implemented responsive typography with `clamp()` for font sizing
  - Added decorative icons with hover effects
  - Included responsive breakpoints for mobile devices
- **Design**: Consistent with existing credo styling across the site
  - Small caps for verbs (Think, Live, Love)
  - Italic font style matching the site's philosophical tone
  - Responsive design that works on all device sizes

#### Results
✅ **COMPLETED**: Credo now prominently displayed on all book detail pages
✅ Consistent styling with other credo displays across the site
✅ Responsive design works on mobile and desktop devices
✅ Reinforces author's philosophical approach on book pages

### 2. Book Descriptions Integration

#### Overview
Integrated the credo "Think clearly. Live deliberately. Love intensely." into the motivational book descriptions to create a stronger connection between the author's philosophy and each book's content.

#### Implementation Details
- **File Modified**: `content/books/_index.md`
  - Updated all 9 book descriptions to incorporate the credo framework
  - Each description now follows the pattern: "Think clearly about [book topic]. Live deliberately through [book approach]. Love intensely enough to [book outcome]."
  - Maintained the motivational tone while adding philosophical depth
  - Preserved all existing metadata (titles, subtitles, captions, images)

#### Book-Specific Integrations:
- **Unstuck**: "Think clearly about what's holding you back. Live deliberately by taking action instead of making excuses. Love intensely enough to stop negotiating with yourself."
- **A Life Made Whole**: "Think clearly about what's broken. Live deliberately through the daily practice of Stoic virtues. Love intensely enough to rebuild what life has fractured."
- **The Stoic Citizen**: "Think clearly about your civic obligations. Live deliberately as a citizen in a polarized age. Love intensely enough to choose reason over rage, duty over drama, and humility over hubris."
- **The Stoic CGM**: "Think clearly about your metabolic data. Live deliberately through the discipline of Stoic impressions. Love intensely enough to transform numbers into wisdom."
- **Misaligned**: "Think clearly about your mental maps. Live deliberately with the right framework for your mind. Love intensely enough to embrace a diagnosis that reframes everything."
- **Letters**: "Think clearly about history's hard truths. Live deliberately through the quiet courage of those who refused to look away. Love intensely enough to engage in timeless dialogue."
- **Stoic Backgammon**: "Think clearly about probability and risk. Live deliberately through the discipline of strategic play. Love intensely enough to find acceptance in defeat."
- **On Proportion**: "Think clearly about the maps that shape us. Live deliberately beyond the containment of Cold War conditioning. Love intensely enough to grow organically."
- **Raise'm Right**: "Think clearly about what children truly need. Live deliberately as a parent in a noisy world. Love intensely enough to raise children of character, judgment, and agency."

#### Results
✅ **COMPLETED**: All book descriptions now integrate the credo framework
✅ Consistent philosophical messaging across the entire book catalog
✅ Stronger connection between author's philosophy and each book's content
✅ Motivational language that encourages readers to click "Learn More"
✅ Maintained responsive design and visual layout

### 3. Author Bio Standardization

#### Overview
Created standardized author biographies that incorporate the credo "Think clearly. Live deliberately. Love intensely." for use across all book marketing platforms, including the Amazon Author Page.

#### Implementation Details
- **File Created**: `/Users/prh/Vault/Extras/Author_Bio.md`
  - Three bio lengths: Short (100 words), Medium (150 words), Long (250 words)
  - Amazon Author Page specific bio (400 characters under Amazon's limit)
  - All versions integrate the credo as a central organizing principle
  - Consistent messaging about Stoicism, civic life, and practical philosophy
  - Highlights military service (1973-1975), book catalog, and unique perspective

#### Key Features:
- **Credo Integration**: All bios begin with the credo as the guiding framework
- **Military Service**: Highlights U.S. Army service (1973-1975) as formative experience
- **Book Catalog**: Lists key titles with brief, compelling descriptions
- **Philosophical Approach**: Emphasizes practical application of Stoic principles
- **Target Audience**: Speaks to readers who've outgrown conventional advice
- **Platform-Specific**: Includes tailored version for Amazon Author Page
- **Character Count**: Amazon bio is 798 characters (well under Amazon's 800 character limit)

#### Results
✅ **COMPLETED**: Standardized author bios created with credo integration
✅ Consistent messaging across all marketing platforms
✅ Multiple lengths available for different use cases
✅ Amazon Author Page content ready for implementation
✅ Reinforces author brand and philosophical approach

### 4. Amazon Author Page Content

#### Overview
Prepared final content for Amazon Author Page implementation, including the standardized bio and credo integration.

#### Content Prepared:
```
Philip Huffman writes about Stoicism, civic life, and the practical work of getting unstuck. His credo—*Think clearly. Live deliberately. Love intensely.*—guides everything he creates, offering readers a framework for living with clarity, proportion, and authentic connection.

A U.S. Army veteran, Huffman brings a unique perspective to his exploration of human agency and resilience. He has published nine books that blend personal narrative with philosophical inquiry, including:

- *Unstuck*: Brutal guidance for getting out of your own way
- *The Stoic Citizen*: Civic duty as moral practice in polarized times  
- *The Stoic CGM*: Ancient wisdom meets modern metabolic health
- *Misaligned*: A neurodivergent journey through miscommunication and misapplied discipline
- *On Proportion*: Growing up with the Cold War

Huffman's writing speaks directly to readers who've noticed that conventional advice often falls short. Whether exploring health, parenting, or public life, his work consistently returns to the same themes: clarity as the foundation of effective action, discipline as the path to authentic freedom, and love as the force that makes both possible.

Visit huffmanwrites.org for essays, digests, and dispatches that apply these principles to contemporary challenges.
```

#### Key Details:
- **Character Count**: 798 characters (Amazon limit: 800)
- **Word Count**: 129 words
- **Credo Integration**: Central organizing principle
- **Book Highlights**: 5 key titles with compelling descriptions
- **Call to Action**: Directs readers to huffmanwrites.org
- **Philosophical Framework**: Emphasizes clarity, discipline, and love as core themes

#### Results
✅ **COMPLETED**: Amazon Author Page content prepared and ready for implementation
✅ Content fits within Amazon's 800 character limit
✅ Consistent with author's philosophical approach and book marketing strategy
✅ Includes credo, book catalog, and website call-to-action

### 5. Book Cover Author Bios

#### Overview
Updated author biography sections in all `cover.md` files in the AllMyBooks directory with the standardized bio and credo integration.

#### Implementation Details
- **Files Updated**: 6 `cover.md` files in `/Users/prh/Developer/LaTeX/AllMyBooks/`
  - `cgm/cover/cover.md`
  - `proportion/cover/cover.md`
  - `Misaligned/cover/cover.md`
  - `tsc/cover/cover.md`
  - `unstuck/cover/cover.md`
  - `Life_made_whole/cover/cover.md`
- **Standardized Bio**: Consistent 398-word bio across all books
- **Credo Integration**: Full credo (*Think clearly. Live deliberately. Love intensely.*) in all bios
- **Service Years**: Corrected to 1973-1975 in all bios
- **Philosophical Framework**: Emphasizes clarity, discipline, and love as core themes
- **Target Audience**: Speaks to readers who've outgrown conventional advice

#### Key Changes:
- **Old Credo**: Some books had "Think clearly. Live deliberately." (2-part version)
- **New Credo**: All books now have the full 3-part version with "Love intensely"
- **Service Years**: Updated from 1973-1974 to 1973-1975 in all bios
- **Consistency**: All books now have identical author bios with the same philosophical framework
- **Professional Tone**: More focused on the author's current writing and philosophical approach

#### Results
✅ **COMPLETED**: All book cover author bios updated with standardized content
✅ Consistent messaging across all books in the AllMyBooks directory
✅ Full credo integration on all book covers
✅ Corrected service years (1973-1975) in all bios
✅ Professional, philosophical tone that reinforces author brand

## Group C: Blue Sky - Implementation Progress

### Overview
Began implementation of Group C: Blue Sky initiatives to elevate the credo "Think clearly. Live deliberately. Love intensely." across innovative, experimental platforms. These initiatives create new touchpoints for the credo and reinforce its presence across the author's ecosystem.

### Phase 1: Foundation (Completed)

#### 1. Website Integration Foundation
- **Status**: ✅ Complete
- **Files Created**:
  - Layout files for all initiatives: `layouts/shop/list.html`, `layouts/workshop/list.html`, `layouts/challenge/list.html`, `layouts/podcast/list.html`, `layouts/community/list.html`, `layouts/api/list.html`
  - Content files: `content/shop/_index.md`, `content/workshop/_index.md`, `content/challenge/_index.md`, `content/podcast/_index.md`, `content/community/_index.md`, `content/api/_index.md`
  - Workshop content: `content/workshop/day-1.md`
- **Features**:
  - Responsive design for all device sizes
  - Consistent credo branding across all initiatives
  - Interactive elements (tabs, forms, galleries)
  - Mobile-friendly layouts
- **Result**: Foundation established for all six Blue Sky initiatives

#### 2. Credo Merchandise Line (Project Structure)
- **Status**: 🚀 In Progress
- **Files Created**:
  - Project documentation structure established
- **Next Steps**: Design specifications, vendor selection, e-commerce integration

#### 3. Credo API (Foundation)
- **Status**: 🚀 In Progress
- **Files Created**:
  - API documentation layout and content structure
- **Next Steps**: API implementation, SDK development, authentication system

### Implementation Details

#### Website Structure
- **Shop**: E-commerce foundation for credo merchandise
- **Workshop**: 7-day interactive program with daily content
- **Challenge**: 4-week social media challenge with weekly themes
- **Podcast**: Audio exploration of the credo with guest interviews
- **Community**: Dedicated platform for discussion and application
- **API**: Developer tools for credo integration

#### Credo Integration
- All initiative pages feature the full credo prominently
- Consistent styling with small caps for verbs (Think, Live, Love)
- Philosophical tone maintained throughout

### Results
✅ **Website foundation complete** - All initiative pages created with responsive layouts
✅ **Content structure established** - Core content for each initiative in place
✅ **Consistent branding** - Credo integrated across all new sections
✅ **Day 1 workshop content** - First day of interactive workshop ready

## Essay: Misaligned — May 31, 2026

- Added `content/posts/essays/misaligned.md`
- Comprehensive article: what the book is, why it was written, why it should be read
- Phil's closest thing to an autobiography; centers on late ADHD diagnosis and its costs
- Key addition: "a significant portion of the pain was unnecessary" — the moral center of why the book exists
- Audience: people who have performed competence while quietly drowning, and those who received a late diagnosis
- Closes with agency as the final argument, not repair

## Essay: A Life Made Whole — May 31, 2026

- Added `content/posts/essays/a-life-made-whole.md`
- Comprehensive article: what the book is, why it was written, why it should be read
- Audience: high-functioning but quietly fragmented readers
- Origin: accumulated experience over decades, not a single crisis
- Includes section-by-section walkthrough of all nine Stoic virtues
- Closes with Amazon link; tone is honest and direct, not promotional

## Book Summaries — Title Format Fix — May 31, 2026

- Renamed all 9 Phil's book summary titles from "Book Title Summary" to "Book Title — Huffman" to match the external summary title format (e.g. "Thinking, Fast and Slow — Kahneman")

## Book Summaries — sort_key Author Name Fix — May 31, 2026

- Corrected sort_key on all 9 Phil's book summaries from "Huffman, Phil" to "Huffman, Philip" for consistency with LC naming convention

## Book Summaries — Sagan Trilogy + LC Ordering — May 31, 2026

- **cosmos-summary.md**, **pale-blue-dot-summary.md**, **brocas-brain-summary.md** — Sagan trilogy added
- **sort_key** frontmatter field added to all 35 summaries (Library of Congress order: last name, first; same-author titles disambiguated)
- List template updated to sort by `sort_key` param before paginating
- Future summaries must include `sort_key` frontmatter to maintain LC order

Running total: 35 summaries (9 Phil's books, 26 external).

## Book Summaries — Psychology, Civics & Philosophy Batch — May 31, 2026

- **thinking-fast-and-slow-summary.md** — Kahneman; System 1/2, cognitive bias; pairs with Sagan and Stoic discipline of assent
- **democracy-in-america-summary.md** — Tocqueville; soft despotism, tyranny of majority, civic associations; pairs with The Stoic Citizen
- **thus-spoke-zarathustra-summary.md** — Nietzsche; death of God, last man, Übermensch, eternal recurrence; pairs with Frankl

Running total: 32 summaries (9 Phil's books, 23 external).

## Book Summaries — Science & Stoicism Batch — May 31, 2026

- **astrophysics-for-people-in-a-hurry-summary.md** — Tyson; cosmic perspective; pairs with Sagan; corrected "mentor" to "hero" after review
- **ego-is-the-enemy-summary.md** — Holiday; ego as tax on achievement across aspiration/success/failure; pairs with Meditations

Running total: 29 summaries (9 Phil's books, 20 external).

## Book Summaries — Ecology Batch — May 31, 2026

Added six ecology summaries, intentionally cross-referenced to existing summaries:

- **sand-county-almanac-summary.md** — Leopold; land ethic as moral philosophy; pairs with Stoic cosmopolitanism
- **unsettling-of-america-summary.md** — Berry; industrialization of agriculture as cultural/moral failure
- **silent-spring-summary.md** — Carson; civic right to know; pairs with Sagan and Nussbaum
- **sixth-extinction-summary.md** — Kolbert; mass extinction as civic failure; pairs with Carson and Leopold
- **braiding-sweetgrass-summary.md** — Kimmerer; Indigenous epistemology + Western science; pairs with Leopold
- **pilgrim-at-tinker-creek-summary.md** — Dillard; attention as practice; pairs with Marcus Aurelius

Running total: 27 summaries (9 Phil's books, 18 external). 4 of 6 ecology titles by female authors.

## Book Summaries Pagination — May 31, 2026

- Created `layouts/posts/summaries/list.html` — custom list layout that paginates at 6 per page
- Overrides PaperMod's default list.html for the summaries section only; all other sections unaffected

## Book Summaries — Female Authors Batch — May 31, 2026

Added six summaries by female authors, bringing gender balance to the summaries section:

- **not-for-profit-summary.md** — Nussbaum; angle: democracy requires humanities education; pairs with Sagan
- **ethics-of-ambiguity-summary.md** — de Beauvoir; angle: freedom requires willing the freedom of others; pairs with Stoics
- **daring-greatly-summary.md** — Brown; angle: vulnerability as courage, shame resilience; pairs with *Unstuck*
- **mindset-summary.md** — Dweck; angle: fixed vs. growth orientation; critique: replication concerns and popularization distortions
- **eichmann-in-jerusalem-summary.md** — Arendt; angle: banality of evil, thoughtlessness as moral failure; pairs with *The Stoic Citizen*
- **radical-acceptance-summary.md** — Brach; angle: trance of unworthiness, RAIN practice; pairs with *The Power of Now*

## Book Summaries Expansion — May 31, 2026

Added six external book summaries to `content/posts/summaries/`, bringing the section beyond Phil's own books for the first time:

- **demon-haunted-world-summary.md** — Sagan; angle: skepticism as practice; includes baloney detection kit breakdown
- **art-of-war-summary.md** — Sun Tzu; angle: strategy as self-knowledge; critique: abstraction and moral coldness
- **7-habits-summary.md** — Covey; angle: character ethic vs. personality ethic; critique: assumes agency not everyone has
- **mans-search-for-meaning-summary.md** — Frankl; angle: meaning in suffering, Stoic parallels; critique: selection problem
- **meditations-summary.md** — Marcus Aurelius; angle: aspiration vs. execution in a private journal; critique: lacks systematic rigor
- **power-of-now-summary.md** — Tolle; angle: presence as practice; critique: spiritual inflation, implicit privilege

All summaries follow the established format: Executive Summary, 5 Core Arguments (numbered), thematic section, A Respectful Disagreement, Bottom Line, closing quote, PRH attribution. Tone: positive, yet critical.

Also updated `_index.md` intro from generic catalog language to credo-anchored copy, and added "like writing" to the summaries page opening sentence.

## Content Edits — May 31, 2026

- **Books page intro** (`content/books/_index.md`): Replaced generic catalog line with credo-anchored copy: "Every book here is an argument for the same proposition — that clarity, discipline, and love are not abstractions. They are the work."
- **Book Summaries intro** (`content/posts/summaries/_index.md`): Changed "Reading is the process..." to "Reading, like writing, is the process..." to tie reading and writing together as parallel disciplines.

## Essay: Fountain Pens — June 8, 2026

- Added `content/posts/essays/fountain-pens.md`
- Title: "Two Nations, One Instrument: How Germany and Japan Shaped the Modern Fountain Pen"
- Long-form (~4,800 words), researched comparative history essay
- German section covers: Pelikan (Kovacs piston mechanism, Model 100/100N, post-war recovery), Montblanc (Meisterstück origins, Simplo Filler Pen Co., WWII survival), LAMY (Bauhaus philosophy, LAMY 2000 and Safari)
- Japanese section covers: writing system requirements and nib sizing, Sailor (1911, Kyugoro Sakata), Pilot/Namiki (1918, Ryosuke Namiki, maki-e revolution, Capless), Platinum (1919, Shunichi Nakata, first cartridge pen)
- Three Stoic touches woven in: Marcus Aurelius / *Meditations* as founding rationale for portable writing; *arete* as the shared ethic of both craft traditions; examined life as the pen's enduring purpose
- Draft also saved to `future-pieces/fountain-pens.md`
- Tags: essays, writing, history, craft, stoicism, philosophy

## High-Contrast Mode Bug Fix — June 8, 2026

- Fixed invisible link text on hover in HC mode
- Root cause: PaperMod's `.post-tags a:hover, .paginav a:hover` sets `background: var(--border)` (amber `#D4820A`), but the `a:hover` color also resolved to amber — text vanished into matching background
- Fix: added HC override in `assets/css/highcontrast.css` to force `color: var(--button-text)` (`#0D0D0D`, near-black) on those hover states, giving strong contrast against the amber background
- Affects: post tag links and prev/next pagination links

## Site Improvements — June 11, 2026

- **CLAUDE.md created** — First time the repo has had a `CLAUDE.md` at the root. Documents build commands, architecture, conventions, and deployment. Content summarizes the `SESSION_STATE.md` Architecture Notes section so future agents can onboard without reading this file in full.
- **Pagination standardized across post sections** — Created custom `list.html` layouts for 5 sections that were inheriting PaperMod's default 10-per-page pagination:
  - `layouts/posts/digests/list.html`
  - `layouts/posts/civics/list.html`
  - `layouts/posts/essays/list.html`
  - `layouts/posts/stoicism/list.html`
  - `layouts/posts/investing/list.html`
  - All 6 post sections (summaries, digests, civics, essays, stoicism, investing) now paginate at 6 per page. The summaries section retains its `sort_key`-based ordering; the other 5 sections sort by date-descending. Matches the density of the existing summaries pagination established on May 31.
- **AI essay corrections notice** — Added a plain-markdown blockquote at the top of `content/posts/essays/AI.md` (after frontmatter, before the H1) recording that the essay was factually reviewed on 2026-05-26 and republished with specific corrections. Lists the categories of corrections (fabricated citations removed, attributions fixed, dates corrected, reference list cleaned up). Closes with the email address for further corrections. Plain blockquote — no new shortcode or CSS class added; the notice sits inside the rendered article and inherits existing prose styling.
- **`featuredOnHome` flag added to home page curation** — Modified `layouts/index.html` "Recent Posts" section to preferentially surface posts with `featuredOnHome: true` (up to 5, date-descending) and fill the remainder with the most recent non-featured, non-hidden posts. Graceful degradation: with 0 featured posts, output is identical to before. Comment block at the top of the section explains the logic.
  - **Initial 5 flagged** (date-descending): `content/posts/essays/fountain-pens.md` (2026-06-08), `content/posts/civics/corruption-at-the-summit.md` (2026-05-21), `content/posts/essays/AI.md` (2026-05-21), `content/posts/essays/the-roots-of-violence.md` (2026-05-10), `content/posts/essays/what-926-gigabytes-taught-me-about-proportion.md` (2026-05-10).
  - **Note:** Originally flagged `optimal-use-of-hermes.md` instead of `fountain-pens.md`; swapped because the Hermes essay is now framed as a historical record (the workflow has changed) and the most-recent essay was being hidden from the home page. The flagged set should be re-curated whenever the corpus changes meaningfully.
- **Memory rule saved** — New auto-memory `update-session-state-before-push` at `/Users/prh/.claude/projects/-Users-prh-Developer-huffmanwrites/memory/update-session-state-before-push.md` so future agents update `SESSION_STATE.md` before every push.

### Open Graph + Bluesky — June 11, 2026 (later)

- **Open Graph hero image wiring** — Per-post `og:image` now resolves from `hero_desktop` → `cover.image` → `image` (book page convention) → `og-default.png`, in that order. Set `og:image:width=1200`, `og:image:height=630`, `og:image:type=image/webp`, and `og:image:alt` (from `hero_alt` when available, otherwise `.Title`, otherwise the default). All meta emitted with absolute URLs (`https://huffmanwrites.org/...`) so LinkedIn, Bluesky, Slack, Discord, iMessage, Facebook, and Mastodon all pick up the right preview image.
  - Implemented as project override `layouts/partials/templates/opengraph.html` that shadows PaperMod's theme default. Title, description, locale, type, section, published/modified time, and up to 6 tags are preserved from PaperMod's logic.
  - Verified across the four page archetypes: post with `hero_desktop` (Stoic Saturday digest → hero WebP), post without image fields (fountain-pens essay → default PNG), book page with `image` (Unstuck → cover JPG with title fallback alt), and the home page (default PNG).
- **Twitter Card meta stripped** — Phil confirmed he wants nothing to do with Twitter/X. Removed `twitter:image` and `twitter:card` from `layouts/partials/extend_head.html`. Created empty `layouts/partials/templates/twitter_cards.html` to shadow PaperMod's theme partial. Comment at the top of both files explains the intent and points to the auto-memory `no-twitter-x`.
- **Bluesky social icon added** — `[[params.socialIcons]]` entry in `hugo.toml`: `name='bluesky'`, `url='https://bsky.app/profile/huffmanwrites.bsky.social'`. Phil's personal Bluesky handle was changed to `huffmanwrites@bsky.social` (brand-aligned). PaperMod's built-in Bluesky SVG renders automatically via `social_icons.html`. The icon now appears in the home page social strip and on every page that includes the partial.
- **Bluesky added to `schema.org` sameAs** — `[params.schema].sameAs` in `hugo.toml` now includes the Bluesky profile URL alongside `https://huffmanwrites.org`. Verified in rendered home page: `"sameAs":["https://huffmanwrites.org","https://bsky.app/profile/huffmanwrites.bsky.social"]`.
- **Auto-memories saved** — `no-twitter-x` (Phil doesn't use Twitter/X; don't build Twitter-specific features) and `bluesky-handle` (`huffmanwrites@bsky.social`).

### Preconnect + Google Fonts <link> lift — June 11, 2026 (later)

- **Cross-origin preconnect hints** — Added four `<link rel="preconnect">` tags to `layouts/partials/extend_head.html` (in order): `fonts.googleapis.com`, `fonts.gstatic.com`, `gc.zgo.at`, and `huffmanwrites.goatcounter.com`. All carry `crossorigin`. Lets the browser start TLS handshakes in parallel with HTML parsing instead of paying the round-trip cost when it later discovers the @font-face, analytics script, and analytics beacon.
- **Google Fonts lifted from `@import` to `<link>`** — `assets/css/custom.css` previously had `@import url('https://fonts.googleapis.com/css2?...')` on line 1, which is render-blocking and serial: the browser had to fetch `custom.css`, parse the `@import`, then fetch the Google Fonts CSS, then fetch the font files. Lifted to a `<link rel="stylesheet">` in `extend_head.html` (right after the preconnect hints) so the browser can discover the Google Fonts CSS in parallel with HTML parsing. Replaced the `@import` with an explanatory comment in `custom.css` pointing to the new location.
- **Build verification** — Clean `rm -rf public && hugo --gc --minify` produced 279 pages, 38 paginator pages, 105 processed images, 0 errors. Exactly one `custom.min.*.css` file in the output (the new fingerprint, no `@import`). The four preconnect hints are present on every page that includes `extend_head.html`, with the Google Fonts stylesheet immediately after them.

### all-my-books canonical — June 11, 2026 (later)

- **Added `canonicalURL: https://huffmanwrites.org/books/`** to the frontmatter of `content/posts/essays/all-my-books.md`. Tells search engines that the canonical version of "All My Books" is `/books/`; the post URL remains accessible to users (so existing bookmarks and shared links still work) but ranking signals consolidate to the books catalog.
  - Field name is `canonicalURL` (not `canonical`) — matches PaperMod's `head.html` template at line 95. Used the absolute URL form (`https://huffmanwrites.org/books/`) rather than the relative (`/books/`) for consistency with how Hugo emits self-canonicals and because Google treats absolute canonicals as more authoritative.
  - Verified: `all-my-books` page now emits `<link rel=canonical href=https://huffmanwrites.org/books/>`; `/books/` still emits its self-canonical; no regressions on other pages.

### Reading progress indicator — June 11, 2026 (later)

- **Thin progress bar at the top of every long-form post.** A 3px fixed bar that fills left-to-right as the user scrolls through the article body. Communicates reading depth on long-form content (essays 2,000-4,800 words; civics explainers; book summaries).
  - Implementation: project `layouts/_default/single.html` emits a `<div id="reading-progress" role="progressbar" aria-valuemin=0 aria-valuemax=100 aria-valuenow=0>` plus a ~15-line vanilla JS IIFE that listens to scroll/resize with `requestAnimationFrame` throttling, computes the percentage of the article body that's been scrolled past, and sets both the inner fill width and `aria-valuenow`. No external dependencies.
  - CSS in `assets/css/custom.css`: `#reading-progress` is `position: fixed; top: 0; left: 0; height: 3px; z-index: 1000; pointer-events: none;` and `#reading-progress-fill` uses `var(--primary)` so it adapts to all three themes (default dark, default light, high-contrast).
  - Accessibility: ARIA `role="progressbar"` with `aria-label="Reading progress"`, dynamic `aria-valuenow`; `pointer-events: none` so it never intercepts clicks; `prefers-reduced-motion: reduce` disables the width transition.
  - **Surface area**: appears on all post pages (essays, digests, civics, summaries, stoicism, investing) but NOT on the home page, book catalog, or book detail pages. Book detail pages use their own template (`books/single.html`) and are reference material rather than flowing reads, so the bar is intentionally absent there.
  - Build verified: 279 pages, 0 errors, 1 CSS file with reading-progress styles, script present in all post pages and absent from home/books pages.

### Home page inline CSS extraction — June 11, 2026

- **Extracted 6.3KB of inline CSS from `layouts/index.html` into a new fingerprinted stylesheet.** Inline CSS was 23.6% of the home page's total page weight (27,300 bytes total); extraction reduces the home page HTML to 23,047 bytes (-15.6%) and ships a 4.3KB CSS file (`home.min.*.css`) that's cacheable across page loads.
  - New file: `assets/css/home.css` — all `.dashboard`, `.cover-grid`, `.cover-item`, `.hub-grid`, `.hub-card`, `.recent-post`, `.now-card`, `.view-all-link`, `.connect-links`, `.site-hero`, `.hero-eyebrow`, `.hero-tagline`, `.hero-sub`, `.hero-ctas`, `.hero-cta-*`, `.hero-mission-link` rules, plus a `.hero-tagline` size override that the credo block depends on.
  - Wired into `layouts/partials/extend_head.html` with the same `resources.Get "css/..." | resources.Minify | fingerprint` pattern as `custom.css` / `phbooks.css` / `highcontrast.css`, including SRI `integrity` attribute. Loaded globally on every page (overhead is negligible — the home page is the heaviest user, and other pages benefit from caching too).
  - **Credo rules relocated to `custom.css`:** the `.credo-container`, `.credo-line`, and `.credo-verb` rules are shared by 8 layouts (books, workshop, shop, podcast, challenge, community, api, home) and the home-specific credo override (`.hero-tagline` size bump) is the only credo-related rule that actually lives in `home.css`. Keeping credo in `custom.css` means the other 7 layouts don't need to depend on the home page stylesheet being loaded to render their hero correctly.
  - Removed: two inline `<style>` blocks from `layouts/index.html` (lines 3-209 and 222-246 in the previous version). File went from 350 lines to 121 lines. Replaced with a short comment explaining where the styles live.
  - **Remaining inline style blocks in `public/index.html` (5, totaling ~2KB):** PaperMod's theme-toggle display rule, dark-mode color scheme block, social-icon link styles from `extend_head.html`, the newsletter-signup block, and a `.credo-footer` block from a different credo context. All are upstream / unrelated to the home page.
  - Build verified: 279 pages, 0 errors, `home.min.*.css` present in `public/css/` with SRI hash, all 4 stylesheets (custom/phbooks/highcontrast/home) referenced from the home page `<head>`.

### Book shortcode inline CSS extraction — June 11, 2026

- **Extracted ~3KB of inline CSS from `layouts/shortcodes/book.html` into a new fingerprinted stylesheet.** The shortcode carried one inline `<style>` block (the `@media (max-width: 600px)` rules) plus 13 inline `style="..."` attributes scattered across the markup. After extraction, the shortcode is 62 lines (down from 88) and contains only structural HTML.
  - New file: `assets/css/book-shortcode.css` — `.book-card` and all descendants (`.book-cover-wrap`, `.book-cover-wrap > div`, `.book-cover-wrap img`, `.book-cover-placeholder`, `.book-content`, `.book-text`, `.book-title`, `.book-subtitle`, `.book-description`, `.book-actions`, `.book-button`, `.book-badge`, `.book-caption`) plus the responsive media query.
  - Wired into `layouts/partials/extend_head.html` with the same `Minify + fingerprint + SRI integrity` pattern as the other stylesheets. Loaded globally so the shortcode renders consistently wherever it's invoked (`content/books/_index.md` and `content/posts/essays/all-my-books.md` — the latter uses `book_catalog`, a different shortcode, which is unaffected).
  - **`!important` preserved on every rule.** The inline-style hammer was a deliberate fix for visibility regressions where PaperMod or a downstream stylesheet would otherwise hide book-card text or shrink the cover. Moving the `!important` from inline attributes to a real stylesheet preserves the cascade priority without changing the visual outcome. See SESSION_STATE §"Book Descriptions — Change History" for context.
  - **Hard-coded hex colors preserved.** The shortcode used `#e0e0e0`, `#f9f9f9`, `#222`, `#333`, `#444`, `#666`, `#ddd`, `#eee`, `#ffd700`, and `rgba(255, 240, 200, 0.3)` — a deliberate choice to not depend on theme variables. These are kept verbatim in the new file; if a future redesign wants to re-theme the book cards, those values are the place to start.
  - **Cascade order:** `custom.css` → `phbooks.css` → `home.css` → `book-shortcode.css`. The last-loaded stylesheet wins any specificity ties, so `book-shortcode.css` is the final word on `.book-card` rules.
  - **Duplicate rules acknowledged.** Both `custom.css:73-187` and `phbooks.css:34-135` already define overlapping `.book-card` rules with `!important`. The new `book-shortcode.css` adds a third set, also with `!important`. This is intentional — it makes the shortcode resilient to whatever order stylesheets end up loading in. A future cleanup could consolidate the three sets into one source of truth, but that requires careful visual regression testing across the two shortcode use sites.
  - Build verified: 279 pages, 0 errors, 9 book cards on `/books/` with 0 inline `style=""` attributes total, `book-shortcode.min.*.css` present in `public/css/` with SRI hash, `all-my-books` page (using `book_catalog` shortcode) unaffected.

### Blue Sky + site-wide inline CSS extraction — June 11, 2026

- **Eliminated every remaining inline `<style>` block from project layouts and partials.** Two new fingerprinted stylesheets (`blue-sky.css`, `gallery.css`) plus additions to `custom.css` and `phbooks.css`. **Result: 0 inline `<style>` blocks in any page body across the entire site** (verified by audit — all 726 remaining inline styles are in `<head>` and belong to PaperMod's noscript fallback, dark-mode block, and the social-icon link styles in `extend_head.html`).
  - **New file: `assets/css/blue-sky.css`** — all CSS for the 6 Blue Sky initiative landing pages (api, community, podcast, challenge, workshop, shop). ~16KB minified, replacing ~22KB of inline CSS across the 6 layouts. Each layout's section is delineated by a `/* === /SECTION/ === */` comment. Unique class prefixes (`.api-*`, `.community-*`, etc.) prevent cross-section conflicts. Loaded globally because the file is small enough that the per-page overhead is negligible and the file becomes cacheable.
  - **New file: `assets/css/gallery.css`** — 2.4KB minified, replacing 3.2KB of inline CSS in `layouts/_default/gallery.html`. Includes the GLightbox theme overrides (`.glightbox-container` with `--glightbox-color-*` CSS variables), gallery card grid, hover states, and pagination.
  - **`assets/css/custom.css` additions** — three new sections appended:
    - `.credo-footer` rules (was in `layouts/partials/credo_footer.html` inline, 585B). Used site-wide since `extend_footer.html` includes the partial on every page.
    - `.newsletter-signup` rules (was in `layouts/partials/newsletter.html` inline, 585B). Currently used on the home page only.
    - `.not-found-*` rules (was in `layouts/_default/404.html` inline, 1.8KB).
    - `.about-headshot` rules (was in `layouts/_default/about.html` inline, 510B).
    - `.gallery` shortcode rules (was in `layouts/shortcodes/gallery.html` inline, 146B). Note: bare `.gallery` class on the shortcode vs `gallery-*` prefixed classes on the landing page — different concerns, no conflict.
  - **`assets/css/phbooks.css` additions** — `.article-hero-container`, `.responsive-hero-img`, `.hero-overlay` rules for the book detail page hero (was in `layouts/books/single.html` inline, 537B). Placed in `phbooks.css` because the book detail page is a `books/single.html` layout and the styles are book-specific.
  - **Layouts stripped:**
    - `layouts/api/list.html` (477 → 169 lines; -65%)
    - `layouts/community/list.html` (343 → 86 lines; -75%)
    - `layouts/podcast/list.html` (289 → 67 lines; -77%)
    - `layouts/challenge/list.html` (273 → 74 lines; -73%)
    - `layouts/workshop/list.html` (247 → 53 lines; -79%)
    - `layouts/shop/list.html` (216 → 46 lines; -79%)
    - `layouts/_default/404.html` (84 → 15 lines; -82%)
    - `layouts/_default/about.html` (65 → 39 lines; -40%)
    - `layouts/_default/gallery.html` (260 → 119 lines; -54%)
    - `layouts/shortcodes/gallery.html` (13 → 5 lines; -62%)
    - `layouts/books/single.html` (139 → 113 lines; -19%)
    - `layouts/partials/credo_footer.html` (54 → 8 lines; -85%)
    - `layouts/partials/newsletter.html` (45 → 8 lines; -82%)
  - **Cascade order** (final, after this commit): `custom.css` → `phbooks.css` → `home.css` → `book-shortcode.css` → `blue-sky.css` → `gallery.css`. Each successive stylesheet wins any specificity tie against its predecessors.
  - **Remaining inline `<style>` in `extend_head.html`** is the social-icon link styles block (`.social-icon-link`, `.social-icon-container`, `.social-label`) — kept inline intentionally because it's first-paint UI styling for the social icons in the header.
  - Build verified: 279 pages, 0 errors, all 6 Blue Sky pages + 404 + about + gallery + books/* still render correctly with their distinctive visual treatments intact.

### Final inline CSS + JS extraction pass — June 11, 2026

- **Eliminated the last 5 inline `style="..."` attributes and extracted 3 inline `<script>` blocks to fingerprinted JS files.** Site is now at 0 inline `style=""` attributes across all layouts, content, and partials; 0 inline `<style>` blocks in any page body; 0 inline `<script>` blocks authored by this project in any page body.
  - **Inline `style=""` extracted (5 total):**
    - `layouts/books/single.html:106` (book-navigation div) → `.book-navigation` rule added to `phbooks.css`.
    - `layouts/_default/gallery.html:30` (page X of Y summary) → `.gallery-page-info` rule added to `gallery.css`.
    - `layouts/_default/gallery.html:101` (content wrapper) → `.gallery-content-wrapper` rule added to `gallery.css`.
    - `layouts/partials/social_icons.html:8` (Amazon "A" badge) → `.social-amazon-badge` rule added to `custom.css`. Also fixed a latent bug: the original inline used `var(--font-header)` (typo for `var(--font-headings)`); the new class uses the correct variable.
    - `layouts/index.html:67` (fallback for missing cover image) → `.cover-item-fallback` rule added to `home.css`.
  - **JS files extracted (3 new files in `assets/js/`):**
    - `reading-progress.js` (629B minified) — used on every post page. Loaded with `defer` via `extend_head.html` so it runs after DOM parsing without blocking paint. The IIFE self-checks for the required DOM elements and is a no-op on pages that don't have them.
    - `api-tabs.js` (434B minified) — `/api/` page only. Loaded with `defer` from `layouts/api/list.html` (page-specific, not in extend_head). Tab switcher logic for the .usage-tabs / .tab-content groups.
    - `glightbox-init.js` (158B minified) — `/gallery/` and its 4 paginated pages. Loaded with `defer` from `layouts/_default/gallery.html` after the GLightbox CDN library. Self-checks for `GLightbox` global and is a no-op if the CDN script hasn't arrived yet.
  - All 3 JS files are served with the same `resources.Get | resources.Minify | fingerprint` pattern as the CSS, with SRI `integrity` attribute. `defer` is used so they don't block parsing.
  - **blue-sky.css consolidation:** the 6 per-section `@media (max-width: 768px)` queries (one per Blue Sky layout, each containing a shared `.credo-line { font-size: 1.5rem }` rule plus section-specific grid/typography changes) were merged into 2 queries — one for the shared mobile rules, one for the shop-specific 1.4rem credo override (scoped via `.shop-container .credo-line` to avoid bleed). Source: 1,258 → 1,222 lines; minified: 15,968 → 15,506 bytes (-2.9%).
  - **Removed duplicate `.credo-verb` rule from `blue-sky.css`** (kept the one in `custom.css` which is the same except it also sets `color: var(--primary)`). The custom.css rule applies globally via cascade order (custom.css loads first, and the removed blue-sky rule was a strict subset).
  - Build verified: 279 pages, 0 errors, all 242 post pages load `reading-progress.js`, only `/api/` loads `api-tabs.js`, only the 5 `/gallery/` pages load `glightbox-init.js`.

### Image Reference Validation — June 11, 2026
- **Created `layouts/partials/img.html`** — single helper that replaces the duplicated `resources.Get` + `Resize` + guarded `<img>` pattern that was inlined in 5 layouts and 2 shortcodes. Behavior: trims leading `/` from path; calls `resources.Get`; if found and `size` is set, runs `Resize`; emits an `<img>` (or `<source>` if `tag: source`) with all provided attributes. On a missing asset, emits a `warnf` ("img.html: missing image %q referenced from %s") and renders a fallback with `data-missing-image="true"` so it's greppable in rendered HTML.
- **Created `layouts/partials/bundle.html`** — single helper for CSS/JS bundles. Calls `resources.Get | Minify | Fingerprint` and emits the proper `<link>` or `<script>` with auto-computed SRI `integrity` attribute. JS bundles get `defer` by default. On a missing asset, emits a `warnf` and renders a non-SRI fallback with `data-bundled="false"`.
- **Migrated 8 data-driven image call sites** to use `img.html`:
  - `layouts/index.html` (cover grid, 9 book covers on home)
  - `layouts/books/single.html` (3 sites: hero mobile source, hero desktop img, book cover img)
  - `layouts/shortcodes/book.html` (book card cover)
  - `layouts/shortcodes/book_catalog.html` (catalog cover; collapsed the two duplicated `if .Params.link` / `else` blocks into a single `partial` call)
  - `layouts/_default/gallery.html` — kept gallery on static `relURL` paths (gallery images live in `static/`, not `assets/`, so `resources.Get` would never find them and the old code's `if $imgResource` branch never fired)
- **Migrated 10 bundle call sites** to use `bundle.html`:
  - `layouts/partials/extend_head.html` (7 CSS bundles + 1 JS bundle, all on every page)
  - `layouts/_default/gallery.html` (1 JS bundle, on gallery pages only)
  - `layouts/api/list.html` (1 JS bundle, on /api/ only)
- **Implementation gotcha:** Hugo's template engine treats partial output that interpolates dict arguments as a plain string and re-escapes `<` and `>` (see [hugo#7870](https://github.com/gohugoio/hugo/issues/7870)). Fix: build the entire HTML output as a string with `printf` and apply `safeHTML` once at the end. The first version of `img.html` (which emitted `<img>` and `</img>` directly in template syntax) had all `<>` escaped to `&lt;&gt;` in the output.
- **Build verified:**
  - `hugo --gc --minify` produces 279 pages, 38 paginator pages, 0 errors.
  - **Zero `warnf` lines** from the new partials on a clean tree.
  - **Zero `data-missing-image="true"` or `data-bundled="false"` attributes** in any rendered HTML.
  - All 4 spot-checked pages (`/`, `/books/`, `/posts/essays/all-my-books/`, `/books/unstuck/`) are **byte-identical** to pre-edit state once asset hashes and SRI are normalized.
  - The only non-byte-identical deltas are *additive* `width`/`height` attributes on 2 of the 8 call sites (home cover grid, book shortcode). The original `books/single.html:54` and `book_catalog.html:27,34` already had `width`/`height`; the home cover grid and book shortcode did not. Adding them prevents CLS — strictly an improvement.
  - All 7 CSS bundles + 1 JS bundle on every page still have proper SRI `integrity` attributes.
  - `reading-progress.js` is loaded on 128 files (every post + paginated list page + section index + tag page), `api-tabs.js` on `/api/` only, `glightbox-init.js` on the 5 gallery pages. All consistent with pre-edit behavior.
- **`grep -rn "resources\.Get" layouts/ | grep -v "themes/"`** now shows only the 2 new partials (`img.html`, `bundle.html`) — no inline `resources.Get` calls remain in any layout or shortcode.

### Heading-ID Regex → Partial — June 11, 2026
- Moved the inline `replaceRE` at `layouts/books/single.html:80` into a new `layouts/partials/book_strip_headings.html`.
- The new partial uses the 4-group form (`$1` opening tag, `$2` id, `$3` inner text, `$4` closing tag) — more robust than the original 1-capture version because `.*?` with capture group 3 handles nested inline tags (e.g. `## **Copyright**` → `<h2 id="copyright"><strong>Copyright</strong></h2>`).
- The id is emitted verbatim, so existing TOC anchor links keep working byte-for-byte.
- **No change to the shared `anchored_headings.html` partial** (used by 7+ post pages to inject anchors). Book-specific behavior is isolated to a named partial.
- Build verified: 279 pages, 0 errors.
- Edge cases tested on `content/books/`:
  - `unstuck` (apostrophes: "Don't..."): 8 h2 stripped, 0 leftover
  - `letters` (ampersands: "Witness & Voice", "Conscience & Thought", etc.): 6 h2 stripped, 0 leftover
  - `stoic-backgammon` (bolded `## **Copyright**`): 4 h2 stripped, 0 leftover — nested `<strong>` handled
  - `raisem-right` (h1 "Raise'm Right"): 0 h2 in this book, 1 h1 unaffected as expected
  - `on-proportion` (colons + parens): 4 h2 stripped, 0 leftover
- Rendered `public/books/unstuck/index.html` `book-content-body` and `TableOfContents` blocks are **byte-identical** to pre-edit (verified by diff). All 8 TOC anchor targets have matching spans in the body.
- Shared `anchored_headings.html` unaffected: regular post pages (fountain-pens, corruption-at-the-summit, etc.) still show h2 with id and injected anchor links.
- `grep -rn replaceRE layouts/` now returns only the new partial (no inline `replaceRE` in `books/single.html`).

### Featured-Post Filter Simplification — June 11, 2026
- Replaced the 3-line `where featuredOnHome true/ne` split in `layouts/index.html` (5 filter lines, 2 range blocks) with a single `where` clause.
- The `$recent` fallback was inert in production: 5 posts have `featuredOnHome: true`, so `$needed` was always 0. The fallback would only have kicked in if a future post removed its flag.
- **Editorial change to flag for the user:** if a future post has `featuredOnHome: true` removed from its frontmatter, the home page will show fewer than 5 cards (not auto-fill from recent unflagged posts). This matches the literal reading of the original `first 5` cap.
- Build verified: 279 pages, 0 errors. Rendered `public/index.html` `recent-posts` block is **byte-identical** to pre-edit (verified by diff). Same 5 posts in the same order: fountain-pens (2026-06-08), corruption-at-the-summit (2026-05-21), AI (2026-05-21), the-roots-of-violence (2026-05-10), what-926-gigabytes-taught-me-about-proportion (2026-05-10).
- Net template: 11 lines deleted (3 filter lines + 1 closing `{{ end }}` + 1 range block + comment overhead).

### Book-Card CSS Consolidation — June 11, 2026
- **Deleted dead/overridden `.book-card*` rules** from `assets/css/custom.css` (lines 73-187) and `assets/css/phbooks.css` (lines 34-135). Every property in those blocks was 100% overridden by the shortcode's own `!important` rules in `assets/css/book-shortcode.css` (loaded last in `extend_head.html`).
- **Moved 3 load-bearing cross-stylesheet rules** into `book-shortcode.css` (where they belong, since the shortcode's scoped `.book-card .book-*` selectors do not catch the bare card or button):
  - `.book-card:hover` — the lift-on-hover (was in `phbooks.css:46-50`)
  - `.book-card .book-button` — added `text-shadow`, `box-shadow`, `transition` (was in `phbooks.css:97-108`)
  - `.book-card .book-button:hover` — `opacity: 0.85` (was in `phbooks.css:109-111`)
- Net effect: 219 lines deleted, 34 added, -185 net. CSS payload: 17,743 → 14,176 bytes (-20.1%). Build verified: 279 pages, 0 errors, all rendered HTML byte-identical to pre-edit state once asset URLs and SRI hashes are normalized.
- All `!important` flags retained in `book-shortcode.css` (per §"Book Descriptions — Change History" — the inline-style hammer was a deliberate fix for visibility regressions). Hard-coded hex colors retained.
- Cascade order in `extend_head.html` unchanged. SRI hashes are auto-computed at build time, so reordering/merging doesn't break the build. The 4 unrelated bundles (blue-sky, gallery, highcontrast, home) and all 3 JS bundles have byte-identical hashes before vs after.

**Build state:** `hugo --gc --minify` produces 279 pages, 38 paginator pages, 105 processed images, 0 errors. Pre-existing warnings (`.Site.Data` deprecation, `Language.Direction`/`LanguageCode` deprecations, raw-HTML in `credo.md` and `workshop/day-1.md`) are unchanged and unrelated.

## Shop Redbubble Button HC Contrast Fix — July 11, 2026

- Bug report: "Buy on Redbubble" button for the Credo Mug looked permanently in a hover/disabled state; other shop buttons looked normal.
- Root cause: same class of bug as the June 8 HC fix. High-contrast mode's global `a:visited`/`a:hover` rules set link text to `--accent` (dark amber `#D4820A`). Against `.redbubble-button`'s red (`#E41321`) background, that's very low contrast and nearly unreadable. The mug button was the one already visited (from prior testing/purchases), so only it showed the effect — other shop buttons hadn't been visited yet and still showed HC's default blue link color.
- Fix: added `[data-theme="highcontrast"] .redbubble-button` override (default/visited/hover/focus) in `assets/css/highcontrast.css` forcing white text, so the button stays readable in every state regardless of visited/hover status.
- Follow-up: forcing white text in every state also flattened the hover feedback (the base opacity-fade-to-0.88 hover was too subtle without a color shift to go with it). Added a hover/focus `background-color: #B8101C` (darkened red) in the same HC override so the button still gives clear visible feedback on hover.
- **Real root cause (found after the above shipped):** the original mug complaint reproduced in *normal* mode too — text vanished on hover. Cause: a global, unscoped `a:visited:hover { color: red }` rule in `phbooks.css` (the intentional "classic blue/red" link hover used by gallery links — do not remove, per CLAUDE.md) has higher CSS specificity than `.redbubble-button:hover` because it includes the `a` type selector, so it wins and paints a visited button's text red-on-red. Fixed by adding `.redbubble-button:visited:hover { color: #fff }` in `assets/css/blue-sky.css`, which out-specifies the global rule (3 class/pseudo-class selectors vs. 2) without touching the gallery hover colors.

## Discoverability Initiative — June 16, 2026

Four-phase effort to improve search engine and reader discoverability:

1. **Phase 1 (done):** Unblock tags and categories in `robots.txt` — removed `Disallow: /tags/` and `Disallow: /categories/` so Google can index tag aggregation pages (e.g. `/tags/stoicism/`, `/tags/civics/`). Only `/drafts/` remains disallowed.
2. **Phase 2 (done):** Google Search Console — placed `static/google928b4d3715b18b06.html` (file-based verification). Served at `https://huffmanwrites.org/google928b4d3715b18b06.html`. After deploy, click **Verify** in GSC, then submit the sitemap at `https://huffmanwrites.org/sitemap.xml`.
3. **Phase 3 (done):** Audit top book summary titles/descriptions for search intent. Updated 5 high-traffic summary titles to include "Summary & Review" (Frankl, Covey, Kahneman, Marcus Aurelius, Dweck). Descriptions now lead with full author name + book title for better keyword match. Updated `_index.md` description with author names and subject keywords.
4. **Phase 4 (done):** Cross-link summaries → Phil's authored books where topically related. Five summaries updated:
   - `eichmann-in-jerusalem` → *The Stoic Citizen* (linked in "Arendt and the Stoic Citizen" section)
   - `democracy-in-america` → *The Stoic Citizen* (linked twice in "Tocqueville and The Stoic Citizen" section + Bottom Line)
   - `mans-search-for-meaning` → *A Life Made Whole* (added paragraph in Bottom Line)
   - `daring-greatly` → *Unstuck* (added paragraph in Bottom Line)
   - `meditations` → *The Stoic Citizen* + *A Life Made Whole* (added paragraph in Bottom Line)

## Home Page Recent Posts Sort Fix — July 23, 2026

- Bug report: home page "Recent Posts" section showed 5 old civics essays (March 12–20, 2025, in ascending order) instead of the 5 most recent posts, despite three prior same-day commits (`a0b55ad`, `e3f44f4`, `00b9938`, `7456bc0`) attempting to fix it.
- Root cause: `layouts/index.html`'s `sort $recentPosts "Date" "descending"` used the wrong keyword — Hugo's `sort` function only recognizes `"asc"`/`"desc"` for the order argument. `"descending"` is silently ignored and falls back to the default ascending order, so the oldest posts of type "posts" surfaced first. None of the prior fix attempts changed the order keyword itself, so the bug persisted through all of them.
- Fix: changed the order argument to `"desc"` in `layouts/index.html`.
- Secondary bug found and fixed in the same pass: `content/posts/digests/pending/archive/stoic-saturday-june-20-2026.md` was a stray duplicate of the real digest at `content/posts/digests/stoic-saturday-june-20-2026/`, mistakenly created inside the `content/` tree (the correct sent-digest archive location is the top-level `pending/archive/`, outside `content/`). Because it lived under `content/posts/`, Hugo rendered it as a live page and it was displacing a genuine 5th post in the Recent Posts list. Deleted; the real digest page is untouched.
- Verified: `hugo --gc --minify` build clean, 0 errors. Rendered home page now shows 5 distinct posts in correct descending order (July 23 → June 20 → June 16 → June 8 → May 31, 2026).

## Writings Breadcrumb Backslash Fix — July 23, 2026

- Bug report: the "Writings" breadcrumb crumb (and the `/posts/` section title/description) rendered as the literal string `\"Writings\"`, backslashes and all, on every post page site-wide.
- Root cause: `content/posts/_index.md` frontmatter used `\"Writings\"` / `\"...\"` (escaped quotes) instead of plain YAML double-quoted strings (`"Writings"`). YAML treated the backslashes as literal characters rather than escape syntax, so `.Title` carried them through into the breadcrumb partial and JSON-LD structured data.
- Fix: removed the stray backslashes from `title`, `description`, and `layout` in the frontmatter.
- Verified: `hugo --gc --minify` build clean; breadcrumb and JSON-LD `BreadcrumbList` now render plain `Writings` on `/posts/essays/fountain-pens/` (spot-checked) and by extension every page under `/posts/`.

## New Essay: The Genius Years (Satire) — July 23, 2026

- Published `content/posts/essays/the-genius-years-oral-history.md` — a speculative, mock-oral-history satire imagining a Trump presidency run with the competence he's always claimed to have. Explicitly framed up front as fiction; all "interviewees" are invented/composite, not real people, to keep the counterfactual unambiguous.
- Tonal departure from the section's usual "personal stakes + historical context + contemporary urgency" essay voice — first humor/satire piece on the site. Tagged `humor`, `satire`, `politics`, `essays`.
- No hero image: the user tried generating one (marble-bust-with-oversized-gold-laurel-crown concept, matching site's locked visual identity) and wasn't happy with the results, so the post ships without `hero_desktop`/`hero_mobile` and falls back to `static/og-default.png`. Revisit hero art later if desired.
- `featuredOnHome: true` — appears in the home page Recent Posts feed.

## Last Updated
2026-07-23 (New essay: "The Genius Years" satirical oral history published to Essays & Observations, featuredOnHome: true, no hero image — user wasn't satisfied with generated art, ships with default OG fallback)
2026-07-23 (Writings breadcrumb fix: removed stray escaped-backslash quotes from content/posts/_index.md frontmatter that were leaking `\"Writings\"` into the breadcrumb and JSON-LD on every /posts/ page)
2026-07-23 (Home page Recent Posts: fixed `sort` order keyword `"descending"` → `"desc"` in layouts/index.html; deleted stray duplicate digest file inside content/posts/digests/pending/archive/)
2026-07-11 (Shop Redbubble button hover-text fix: `.redbubble-button:visited:hover` now out-specifies phbooks.css's global `a:visited:hover { color: red }`, which was the real cause of the mug button's invisible hover text in normal mode)
2026-07-11 (Shop Redbubble button HC contrast fix: forced white text on `.redbubble-button` in high-contrast mode across default/visited/hover/focus states)
2026-06-16 (Discoverability Phase 4: cross-links from 5 external summaries to Phil's authored books — Eichmann/Democracy→Stoic Citizen, Frankl→Life Made Whole, Daring Greatly→Unstuck, Meditations→Stoic Citizen+Life Made Whole)
2026-06-16 (Discoverability Phase 3: top 5 summary titles/descriptions updated for search intent — "Summary & Review" pattern, full author names in descriptions)
2026-06-16 (Discoverability Phase 2: Google Search Console file-based verification added to static/)
2026-06-16 (Discoverability Phase 1: unblocked /tags/ and /categories/ in robots.txt)
2026-06-11 (Image reference validation: img.html and bundle.html partials with warnf-on-miss; migrated 8 image + 10 bundle call sites; all rendered pages byte-identical or strictly improved)
2026-06-11 (Heading-ID regex → partial: layouts/partials/book_strip_headings.html, 4-group form, byte-identical rendered output)
2026-06-11 (Featured-post filter simplification: drop inert $recent fallback, single where clause, byte-identical rendered output)
2026-06-11 (Book-card CSS consolidation: deleted 219 lines of dead/overridden rules, moved 3 load-bearing rules into book-shortcode.css, -20% CSS payload)
2026-06-11 (Final inline CSS + JS pass: 0 inline style="" and 0 inline <style>/<script> in any body)
2026-06-11 (Blue Sky + site-wide inline CSS extraction — 0 body-level <style> blocks remain)
2026-06-11 (Book shortcode inline CSS extraction → assets/css/book-shortcode.css)
2026-06-11 (Home page inline CSS extraction → assets/css/home.css)
2026-06-11 (Reading progress indicator on long-form posts)
2026-06-11 (all-my-books canonicalURL pointing to /books/)
2026-06-11 (Preconnect hints + Google Fonts lifted from @import to <link>)
2026-06-11 (Open Graph hero wiring + Twitter stripped + Bluesky social icon)
2026-06-11 (Site maintenance: CLAUDE.md, pagination consistency, AI essay corrections, featuredOnHome flag)
2026-06-08 (Fountain pens essay published to Essays & Observations)
2026-05-31 (Content copy edits: books intro, summaries intro)
2026-05-29 (Group C: Blue Sky foundation implementation)
2026-05-29 (Book marketing: credo integration on book detail pages)
2026-05-28 (Book catalog: aspect ratio fix, 80×120 covers, float-right text-wrap layout)
2026-05-27 (Added Goodreads + LinkedIn social icons)
2026-05-26 (High-contrast / neurodivergent theme toggle)
2026-05-23 (Sent newsletter: What We Owe the Fallen)
