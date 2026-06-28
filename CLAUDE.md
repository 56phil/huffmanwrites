# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hugo static site (`huffmanwrites`) using the [PaperMod](https://github.com/adityatelange/hugo-PaperMod) theme. Domain: `huffmanwrites.org` (CNAME committed at `static/CNAME`). Deployed to GitHub Pages via `.github/workflows/hugo.yml` on push to `main`.

The site is a personal publication platform for Philip Huffman — 9 published books (Stoicism, civics, neurodivergence), a weekly digest, a long-form essay section, a civics / Constitution series, and a growing library of book summaries. The site embodies the credo **"Think clearly. Live intentionally. Love deeply."** which appears on the home page, book detail pages, and the footer.

Visual identity (locked): Parian marble textures, deep midnight navy backgrounds (`#131E39`), glowing gold accents (accent color is deep amber `#D4820A`), dramatic cinematic lighting, conceptual/metaphorical imagery (not literal). Established in `skills/hero-image-workflow.md`.

## Common Commands

```bash
# Build the site (production)
hugo --gc --minify

# Build with a specific baseURL (e.g. for local preview)
hugo server --buildDrafts

# Clean rebuild (clears resources/_gen and removes stale fingerprints)
hugo --gc --minify
```

Hugo v0.162.1+extended is installed via Homebrew at `/opt/homebrew/bin/hugo`. The CI workflow (`.github/workflows/hugo.yml`) pins v0.147.0 — the extended variant is required for Dart Sass and image processing.

There are no automated tests, linters, or a package.json. The "test" is a clean `hugo --gc --minify` build with no errors.

## Architecture

### Content tree (`content/`)

- `content/_index.md` — the **mission** page (this is not the home page; the home page is rendered by `layouts/index.html`).
- `content/books/<slug>/index.md` — one directory per book. Required frontmatter: `title`, `subtitle`, `image`, `image_desktop`, `image_mobile`, `image_alt`, `hero_caption` (for hero), `image_caption` (for cover — never the same), `link` (Amazon), `lastmod`.
- `content/posts/` — section-based posts. Sub-sections:
  - `civics/` — Constitution / civics essays (First Amendment is the only full-length one; others are tiered explainers).
  - `essays/` — long-form essays and observations.
  - `stoicism/` — Stoic reflections.
  - `investing/` — investing & risk.
  - `digests/` — weekly/monthly digests (frontmatter includes `sendfox_subject` for newsletter sends).
  - `summaries/` — book summaries; the canonical structure is in `content/posts/summaries/_index.md`. Each summary uses `sort_key` (LC: "Last, First") for ordering. Summaries paginate at 6/page via `layouts/posts/summaries/list.html`.
- `content/shop/`, `content/workshop/`, `content/challenge/`, `content/podcast/`, `content/community/`, `content/api/` — "Blue Sky" initiatives (see SESSION_STATE.md). All have custom layouts under `layouts/<section>/list.html`.

### Layouts (`layouts/`)

- `layouts/index.html` — home page; contains the hero, credo, knowledge hubs, recent posts, library cover grid, and newsletter CTA. ~330 lines including inline `<style>`.
- `layouts/_default/single.html` — universal post template (articles + newsletters). Includes the responsive hero `<picture>` block driven by `hero_desktop` / `hero_mobile` / `hero_alt` / `hero_caption` frontmatter, and a "Further Reading" related-posts block (tag match first, then section match, capped at 4).
- `layouts/_default/baseof.html` — PaperMod base, extended via partials.
- `layouts/_default/gallery.html` — gallery index page.
- `layouts/books/single.html` — book detail page: hero + cover + blurb + credo + TOC + Amazon button + prev/next book navigation.
- `layouts/books/section.html` — book listing.
- `layouts/posts/summaries/list.html` — overrides PaperMod's list for the summaries section; paginates at 6 per page, sorted by `sort_key`.
- `layouts/shortcodes/book.html` — book card (used in `content/books/_index.md`). Loads images via `resources.Get` + `Resize "600x webp"` so all covers are served as WebP at build time. Heavy inline `!important` styles — the inline-style approach was a deliberate fix for visibility regressions (see SESSION_STATE.md §"Book Descriptions — Change History").
- `layouts/shortcodes/book_catalog.html` — full catalog grid.
- `layouts/shortcodes/section-hero.html`, `gallery.html`, `rawhtml.html` — other shortcodes.
- `layouts/partials/extend_head.html` — CSP headers (SendFox form-action whitelisted), GoatCounter analytics, Google Fonts import, OG image fallback, custom CSS includes (`custom.css`, `phbooks.css`, `highcontrast.css`), and the high-contrast early-activation script (reads `localStorage` key `pref-hc`; auto-enables on `prefers-contrast: more`).
- `layouts/partials/extend_footer.html` — injects the HC toggle button into PaperMod's `.logo-switches` via DOMContentLoaded, wires the toggle handler, and patches PaperMod's theme toggle to clear `pref-hc`.
- `layouts/partials/credo_footer.html` — the credo display in the footer.

### Styles (`assets/css/`)

- `custom.css` — PaperMod overrides, credo typography (`.credo-verb` small-caps, `.credo-line`).
- `phbooks.css` — book-related styles: `.post-hero`, `.post-hero-img`, `.post-hero-caption`, `.book-caption`, `.hero-caption`, `.book-media`, `.book-cover-wrap`, `.phbooks-cover`, `.book-credo-container`, `.book-credo`, `.book-toc`.
- `highcontrast.css` — high-contrast mode (`[data-theme="highcontrast"]`). Palette: near-black `#0D0D0D`, warm cream `#F2EDD8`, dark amber `#D4820A` borders/buttons, sky-blue links, Atkinson Hyperlegible font, line-height 1.88, reduced-motion support. HC mode overrides PaperMod hover states for `.post-tags a:hover` and `.paginav a:hover` (force `color: var(--button-text)` to prevent text vanishing into matching amber background).

### Images

- `static/img/books/` — book covers (source JPGs; served as WebP via `resources.Get` + `Resize`).
- `static/img/articles/` — article/newsletter hero images. Convention: `[NN]-[slug]_16x9.webp` and `[NN]-[slug]_4x5.webp` (NN = post ID, paired as desktop/mobile).
- `static/og-default.png` — default OG image for pages without `cover.image`.

### Custom skills (`skills/`)

- `hero-image-workflow.md` — generation + wiring conventions for hero images (aesthetic, naming, frontmatter mapping).
- `kdp_cover_designer.md` — references `scripts/cover_generator.py` (out-of-repo, in `/Users/prh/Developer/LaTeX/AllMyBooks/`) for the 6×9 KDP wraparound covers.

### Drafts and work-in-progress

- `future-pieces/` — draft essays (e.g. `fountain-pens.md` was drafted here before being published).
- `pending/` — newsletter drafts awaiting send. `TEMPLATE.md` is the digest template; sent digests move to `pending/archive/`. Each pending file has `sendfox_subject` frontmatter for the SendFox API send.
- `SESSION_STATE.md` — long-form project state, maintenance log, and architecture notes. **Read this at session start** to pick up continuity before asking "where were we?"

## Conventions

- **Tone:** Personal stakes + historical context + contemporary urgency. Not yelling, not lecturing. Think *with* the reader.
- **First Amendment** content gets full essay length; narrower amendments get shorter explainers.
- **`hero_caption`** is for the hero image; **`image_caption`** is for the book cover. Never mix them.
- **New hero images** must be WebP. Use the `[NN]-[slug]_16x9.webp` / `_4x5.webp` naming convention.
- **Book summaries** must include `sort_key` frontmatter (LC order: "Last, First") so the list template's `ByParam "sort_key"` keeps them in order. Established format: Executive Summary, 5 Core Arguments (numbered), thematic section, A Respectful Disagreement, Bottom Line, closing quote, `*PRH | [huffmanwrites.org] | © Philip Huffman*` attribution. Tone: positive, yet critical.
- **All Hugo posts** should have `lastmod` frontmatter (git-based date is fine).
- **All post images** lazy-load except hero images, which use `loading="eager" fetchpriority="high"`.
- **Always check spelling/grammar** before committing and pushing.
- **Gallery link hover colors** (`blue`/`red`) are intentional — do not suggest changing them.
- **`all-my-books.md`** is kept as an alternate entry point to `/books/` (renders via `book_catalog` shortcode). Do not delete.
- **Empty non-Constitution stubs** should be deleted. Constitution stubs are kept and written up.

## Deployment

GitHub Pages, deployed automatically on push to `main` via `.github/workflows/hugo.yml`. The workflow installs Hugo 0.147.0 extended, builds with `hugo --gc --minify --baseURL "${{ steps.pages.outputs.base_url }}"`, and uploads `./public` as a Pages artifact. `static/CNAME` ensures the custom domain `huffmanwrites.org` is preserved.

To deploy from a detached worktree (e.g. Codex): `git push origin HEAD:main`.

## Newsletter sends

Digests are sent via the SendFox API using a token stored in `.sendfox_token` (gitignored). After a digest is sent, the corresponding file in `pending/` is moved to `pending/archive/` and a Hugo content page is created in `content/posts/digests/`. SendFox form submissions are whitelisted in the CSP `form-action` directive.
