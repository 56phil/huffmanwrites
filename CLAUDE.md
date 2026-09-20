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

Hugo v0.165.0+extended is installed via Homebrew at `/opt/homebrew/bin/hugo`. The CI workflow (`.github/workflows/hugo.yml`) pins v0.165.0 — the extended variant is required for Dart Sass and image processing.

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
- `content/challenge/`, `content/podcast/`, `content/community/`, `content/api/` — "Blue Sky" initiatives (see SESSION_STATE.md). All have custom layouts under `layouts/<section>/list.html`. (There was a `content/shop/` merchandise section until 2026-09-19; it was retired in full — no shop route, no storefront, no merchandise assets.)

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
- `SESSION_STATE_ARCHIVE.md` — every entry before September 2026, moved out verbatim on 2026-09-20 when the combined file reached 2,023 lines (reading it at session start meant reading three months of history to reach the current entry). Nothing was deleted. **Search it with `grep` when you need an earlier decision, commit hash, or rationale** — it is complete, and it is the only place those answers live.

## Conventions

- **Tone:** Personal stakes + historical context + contemporary urgency. Not yelling, not lecturing. Think *with* the reader.
- **First Amendment** content gets full essay length; narrower amendments get shorter explainers.
- **`hero_caption`** is for the hero image; **`image_caption`** is for the book cover. Never mix them.
- **New hero images** must be WebP. Use the `[NN]-[slug]_16x9.webp` / `_4x5.webp` naming convention.
- **Book summaries** must include `sort_key` frontmatter (LC order: "Last, First") so the list template's `ByParam "sort_key"` keeps them in order. Established format: Executive Summary, 5 Core Arguments (numbered), thematic section, A Respectful Disagreement, Bottom Line, closing quote, `*PRH | [huffmanwrites.org] | © Philip Huffman*` attribution. Tone: positive, yet critical.
- **All Hugo posts** should have `lastmod` frontmatter (git-based date is fine).
- **All post images** lazy-load except hero images, which use `loading="eager" fetchpriority="high"`.
- **Copyedit + fact check every piece of content before it is committed.** Copyedit: spelling, grammar, punctuation, flow, and the em-dash limit (**no more than 3 in the prose you write**; prefer commas, colons, semicolons, or splitting sentences). Two categories are **not counted** against that limit, because they are not the editor's prose: (1) an em-dash **inside quotation marks** — a quotation's internal punctuation belongs to its author or translator, and rewriting it to save a mark would corrupt the quotation the citation gate exists to protect (the Thiel "franchise to women — two constituencies… libertarians —" line is the model case, and the same exemption covers a quoted title or description in frontmatter); (2) an em-dash standing as a **date or numeric range**. That second exemption is a guard rather than a licence: the **en-dash** (`–`) is the correct mark for a range (`1903–1977`, `Aug 25–31`, `53–47`), which is what the site already uses, so an em-dash between dates is a typo to fix rather than a dash to keep. Count with `python3 scripts/check-emdashes.py` (`--file <path>`, `--list` for the corpus, `--check` for the baseline ratchet). Fact check: every load-bearing claim (dates, names, figures, attributions) verified against a source; correct or flag anything unverifiable before publishing. This gate applies to essays, digests, summaries, and any other content.
- **Quotations from translated works must name the translator, the translation, and the year.** "Marcus Aurelius, *Meditations*, 6.21" is an incomplete citation: it credits the author and hides the translation, and the translation determines every word inside the quotation marks. Renderings diverge materially — 6.21 reads "convince or shew me… gladly change" (Chrystal, 1902), "prove and bring home to me… amend" (Haines, 1916), and "reprove me… gladly retract" (Casaubon, 1634) — so an unqualified citation cannot be checked, and a reader who looks it up will conclude the quote is wrong. Cite as `Author, *Work*, §N (trans. Name, Year)`. This applies to the Stoic epigraphs (Marcus Aurelius, Epictetus, Seneca) in every digest, and to any classical, scriptural, or foreign-language source. Verify the wording against the **named** translation at source, and keep the quoted text verbatim, including archaic spelling. **Never paraphrase inside quotation marks:** if no direct rendering of the passage is available, either find one or drop the quotation marks and attribute the idea in prose. Note that several older Stoic epigraphs on the site are famous loose paraphrases ("You have power over your mind—not outside events") circulating without a source text; those must be labeled as paraphrases, not presented as translations.
- **An attribution naming an author the source does not name is a fabrication.** The URL rules above catch an invented link. They cannot catch an invented **name**: on 2026-09-19 the "best time to plant a tree" adage was credited to "O'Toole" with two correct, live links, and neither source contains that name — it is the surname of the researcher who runs Quote Investigator, not the saying's source. Every link check passed. **Before writing a name into an attribution, find that name in the source you are linking**, not in your memory of who investigates the topic. If the source lists candidates, use one of them or say the source is anonymous. A wrong attribution misleads a reader more than a missing one, because it looks checkable.
- **Do not attribute a rendering to a translator without testing it against that translation.** The same session found an epigraph credited to "George Long, 1862" that was in fact Elizabeth Carter's wording, and a Nietzsche line quoted in a familiar paraphrase that appears nowhere in the linked Ludovici translation. `Author, *Work*, §N (trans. Name, Year)` is only a citation if the words between the quotation marks are that translator's. Test the site's exact rendering as a substring of the named translation before writing the name (normalize whitespace first, per the rule above); if it does not match, either quote the rendering that does, or drop the translator's name and label the wording a paraphrase.
- **Every direct quotation must carry a resolvable source link in the piece's own citation apparatus.** Verified-at-source is an assertion; a URL is evidence, and a reader (or the next session) can check it after the fact. Record the link in the file's existing apparatus: the `## Sources` list in digests and essays, the footnote block in pieces that use footnotes, or inline for short-form posts. Three rules on what counts: (1) **the link must contain the quoted wording** — point at the specific translation, edition, or passage, never at a landing page, a publisher's catalog page, or an encyclopedia article *about* the work; (2) the link must be **live at publish time** (check for HTTP 200 — Gutenberg ebook pages, Wikisource book pages, and court/agency documents all qualify); verify the wording by **normalizing whitespace first** (`re.sub(r"\s+", " ", text)`): PDFs, HTML, and hard-wrapped plain text all break lines mid-sentence, so a literal substring test reports a false miss on a source that does contain the quotation (the Vaughan PDF of Carter's *Enchiridion* wraps "…in our control and\nothers not"). Extract PDF text with `pdftotext` before searching; (3) for a work where the quoted rendering exists in no linkable text, that is a finding, not a nuisance — either quote a rendering you can link (the `stoic-backgammon-summary.md` pattern, which quotes the sourced Long rendering alongside the paraphrase) or drop the quotation marks and attribute the idea in prose. A quotation whose wording cannot be linked should not appear as a quotation. **This is enforced:** `scripts/check-quotes.py` runs as a pre-deploy CI gate and fails the build on any attribution that names no translator (for a translated author) or has no URL-bearing line naming that author. Pre-rule quotations are listed in `scripts/quote-baseline.txt`, keyed by a hash of the quoted text — **editing one withdraws its exemption**, so the rule catches up as each file is next touched. Run `python3 scripts/check-quotes.py` before committing content; add `--online` to also fetch each link and confirm it really contains the quoted wording.
- **NEVER construct a URL. Fetch it, or do not cite it.** A URL may be written only after the page has actually been retrieved and confirmed to be the thing being cited. Do not build a URL from the pattern of a real one, do not infer a slug from a headline, and do not guess a date-and-slug from a story's publication date. This is the single most dangerous failure in the repo because the result is **invisible to every ordinary check**: the ID is real, the domain is right, the link returns HTTP 200, and the reader lands on an unrelated article. Three such fabrications shipped before this rule (found 2026-09-19): a "Trump's name removed from the Kennedy Center facade" citation that resolves to a story about pollinator gardens in Oklahoma; a *How Democracies Die* book link that resolves to a children's novel; and a New Republic "Peter Thiel and mimetic desire" article that resolves to a piece about campus consent laws. All three had correct IDs and invented slugs. **If a source cannot be retrieved, either cite it in prose without a link, replace it, or drop the claim.** An absent citation is honest; a plausible-looking wrong one is not.
- **A link that resolves to the wrong page is a fabrication, and CI now fails on it.** `scripts/check-links.py --check` runs in the deploy workflow and rejects placeholder URLs (`[ID]`, `TODO`, `example.com`) and any URL recorded in `scripts/check-links-blocklist.txt` as proven to land somewhere other than the cited article. Run `python3 scripts/check-links.py --online` before publishing to fetch every cited URL and report what it actually finds; a `REDIRECT` verdict where the slug changed is the fabrication signature, and a `200` is not proof of correctness.
- **There is no merchandising and no shop route.** `content/shop/`, `layouts/shop/`, `static/img/shop/` and the merchandise print masters were retired in full on 2026-09-19 (Philip: "No more merchandising"), along with the `Shop` entry in the main menu. Do not reintroduce a shop section, a product page, a marketplace link, or a `Shop` nav item without an explicit instruction to rebuild that surface. The credo is a statement, not a product line.
- **Any button whose text color differs from the site's link colors needs an explicit `:visited:hover` override.** `phbooks.css` carries a global `a:visited:hover { color: red }` (the intentional classic blue/red gallery-link hover — do not remove it). It out-specifies a plain `.<class>:hover` because it includes the `a` type selector, so it will repaint such a button's text invisible. This bug shipped twice on the old shop buttons before it was found.
- **One commit per publish.** The content file and its SESSION_STATE.md entry go in a single commit, pushed once. No follow-up "session state" commits after a content commit.
- **Post-commit SimpleBrain flow.** After the publish commit is pushed: (1) copy the published post to `~/SimpleBrain/raw/content/posts/<section>/` (resolves through the `~/SimpleBrain` symlink to `/Users/prh/Developer/SimpleBrain`); (2) translate it per `~/SimpleBrain/translate.md` — write the full article (frontmatter stripped, `# Title` heading) to `~/SimpleBrain/wiki/articles/<slug>.md` with a `---` + `Source: huffmanwrites.org/posts/<section>/<slug>/` footer, and add a `[[articles/<slug>|Title]]` line to the Recent Highlights section of `~/SimpleBrain/wiki/index.md` (prune the oldest highlight if the list grows past ~7); (3) move the raw file to `~/SimpleBrain/archive/` (flat, never delete); (4) commit and push the SimpleBrain repo (`git -C ~/SimpleBrain commit` + push). The SimpleBrain repo is separate from huffmanwrites; its commits do not trigger the site deploy.
- **Gallery link hover colors** (`blue`/`red`) are intentional — do not suggest changing them.
- **`all-my-books.md`** is kept as an alternate entry point to `/books/` (renders via `book_catalog` shortcode). Do not delete.
- **Empty non-Constitution stubs** should be deleted. Constitution stubs are kept and written up.

## Deployment

GitHub Pages, deployed automatically on push to `main` via `.github/workflows/hugo.yml`. The workflow installs Hugo 0.165.0 extended, builds with `hugo --gc --minify --baseURL "${{ steps.pages.outputs.base_url }}"`, and uploads `./public` as a Pages artifact. `static/CNAME` ensures the custom domain `huffmanwrites.org` is preserved.

To deploy from a detached worktree (e.g. Codex): `git push origin HEAD:main`.

## Newsletter sends

Digests are sent via the SendFox API using a token stored in `.sendfox_token` (gitignored). After a digest is sent, the corresponding file in `pending/` is moved to `pending/archive/` and a Hugo content page is created in `content/posts/digests/`. SendFox form submissions are whitelisted in the CSP `form-action` directive.
