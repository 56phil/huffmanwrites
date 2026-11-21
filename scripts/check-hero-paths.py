#!/usr/bin/env python3
"""Every image path must resolve, in the home its renderer reads.

Why this exists, and why it is not redundant with `check-render-integrity.py`:

`check-render-integrity.py` catches a broken image too, but it needs a full
`hugo` build and it runs once a week from the site-audit job. The reports that
carry heroes are written by **scheduled jobs** that publish or draft with no
human review, and their runners do not build the `public/` tree. A path with a
typo in it is invisible to all of them:

  - `hugo` does **not** fail on a missing image. The build succeeds.
  - The page returns 200 and renders an empty box where the image should be.
  - The runner's own gates (quotes, links, dashes, prepositions) do not read
    frontmatter image paths.

So the defect ships and the first person to see it is a reader. This gate costs
nothing and closes it.

Three rules, each from a failure that shipped, and each stated as **which home
the renderer reads** rather than "somewhere in the repo":

  1. **Every path resolves somewhere.** `hero`, `hero_desktop`, `hero_mobile`,
     `image`, `image_desktop` and `image_mobile` are read by two different
     pipelines: `partials/img.html` and the book card shortcodes resolve through
     `resources.Get`, which reads `assets/`, while the post, section and gallery
     layouts emit `<img src="{{ .Params.image }}">` verbatim, which is served
     from `static/`. A path that resolves in NEITHER renders nothing, so the
     gate requires one of the two homes to hold the file. This rule alone is
     not enough, because "one of the two" is a different question from "the one
     its renderer reads" — which is what rules 2 and 3 answer.

  2. **A book cover must be in `assets/`.** A book page's `image` is rendered
     only through `resources.Get`: `partials/img.html` (via
     `layouts/books/single.html`), `shortcodes/book.html` and
     `shortcodes/book_catalog.html`. A cover placed only in `static/` does not
     fail loudly in the page layout: `img.html` warns and falls back to a raw
     `src` pointing at the file, so the page shows the **unresized source**
     instead of the processed WebP it asks for — while `shortcodes/book.html`
     calls `.Resize` on a nil resource and takes the whole build down. Measured
     2026-10-08: the covers lived in two homes, one of
     them stale — `static/img/books/unstuck.jpg` and
     `assets/img/books/unstuck.jpg` had **different bytes**, so the site served
     art the build never rendered. Those copies were removed, and this rule is
     what keeps the second home from coming back. A cover present in BOTH homes
     is reported: as a failure when the bytes differ (the reader can see the
     wrong image), as a note when they are identical.

  3. **A post's hero, and any non-book page's image, must be in `static/`** —
     the mirror of rule 2, in the opposite home. `layouts/_default/single.html`
     emits `<img src="/{{ .Params.hero_desktop }}">`, `_default/gallery.html`
     reads `$p.Params.hero_desktop`, `schema_json.html` emits
     `{{ .Params.image | absURL }}`, and the challenge and podcast lists emit
     `<img src="{{ .Params.image }}">` — every one of them a raw path, which
     only `static/` publishes. **No layout resolves a post image through
     `resources.Get`.** So a hero placed only in `assets/` passed the old
     "resolves in either home" test and then rendered an empty box on a live
     page, exactly the failure rule 2 exists to prevent for covers.

     The second half is the finding behind the rule, measured 2026-11-21: the
     duplication of article plates across both homes was described in this
     repo as a requirement of "the processing pipeline", and it was not one —
     `img.html`'s only call sites are the book cover grid and the book pages.
     Of 230 files in `assets/img/articles/`, 22 are book heroes that
     `resources.Get` really reads, 78 were referenced by nothing at all, and
     130 duplicated a `static/` copy (12 of them with different bytes, the
     `unstuck.jpg` trap in the other direction). The rule is therefore: one
     home per image class, and an `assets/` copy of an article plate is drift.
     A non-book page whose path exists in both homes is reported as a note, not
     a failure: the reader sees the `static/` copy either way.

Exit codes:
  0  every path resolves, every cover is in assets/, every post image is in
     static/
  1  a path resolves nowhere, a cover is missing from assets/ or duplicated
     with different bytes, or a post image is missing from static/
  2  cannot run (no content tree)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONTENT = REPO / "content"
ASSETS = REPO / "assets"
STATIC = REPO / "static"

PATH_FIELDS = ("hero", "hero_desktop", "hero_mobile", "image", "image_desktop", "image_mobile")
FIELD_RE = re.compile(
    r'^(hero|hero_desktop|hero_mobile|image|image_desktop|image_mobile):\s*"?([^"\n]+?)"?\s*$',
    re.M,
)


def frontmatter(text: str) -> str:
    """The leading `---` block, or "" when the file has none."""
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[:end] if end != -1 else ""


def is_book(path: Path) -> bool:
    """`content/books/<slug>/index.md` — the pages whose `image` is a cover."""
    return path.parent.parent == CONTENT / "books" and path.name == "index.md"


def homes(value: str) -> list[str]:
    """Which of the two image homes hold this path. Empty means neither does."""
    rel = value.lstrip("/")
    out = []
    for name, root in (("static", STATIC), ("assets", ASSETS)):
        if (root / rel).is_file():
            out.append(name)
    return out


def rel_of(path: Path) -> str:
    """Repo-relative for display; a path outside the repo is shown as given
    (`--file` and the tests both pass temp paths)."""
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return path.as_posix()


def audit_file(path: Path) -> tuple[list[str], list[str], int]:
    """(problems, notes, paths_inspected) for one content file."""
    problems: list[str] = []
    notes: list[str] = []
    checked = 0
    rel = rel_of(path)
    fm = frontmatter(path.read_text(encoding="utf-8", errors="ignore"))

    for field, raw in FIELD_RE.findall(fm):
        value = raw.strip().strip("'\"")
        if not value or value.startswith(("http://", "https://")):
            continue
        checked += 1
        found = homes(value)

        if not found:
            problems.append(
                f"{rel}: {field} -> {value} (not in assets/ or static/)"
            )
            continue

        if is_book(path):
            if field == "image":
                if "assets" not in found:
                    problems.append(
                        f"{rel}: {field} -> {value} (a book cover must be in assets/; "
                        f"the cover is rendered only through resources.Get, so a "
                        f"static/ copy publishes unprocessed art)"
                    )
                elif "static" in found:
                    a = (ASSETS / value.lstrip("/")).read_bytes()
                    s = (STATIC / value.lstrip("/")).read_bytes()
                    if a != s:
                        problems.append(
                            f"{rel}: {field} -> {value} exists in assets/ and static/ "
                            f"with different bytes (the site serves the static/ copy; "
                            f"the build renders the assets/ one)"
                        )
                    else:
                        notes.append(
                            f"{rel}: {field} -> {value} is duplicated in static/ "
                            f"(identical bytes; remove the static/ copy)"
                        )
            continue

        # Rule 3. Every non-book renderer emits the path verbatim
        # (`single.html`, `gallery.html`, `schema_json.html`, the challenge and
        # podcast lists), so `static/` is the home that serves it and `assets/`
        # serves nothing. An `assets/`-only path reaches the reader as an empty
        # box on a page that still returns 200.
        if "static" not in found:
            problems.append(
                f"{rel}: {field} -> {value} is in assets/ but not static/ "
                f"(no post layout resolves images through resources.Get; the "
                f"page emits the path verbatim, so this renders an empty box)"
            )
        elif "assets" in found:
            notes.append(
                f"{rel}: {field} -> {value} is duplicated in assets/ "
                f"(nothing reads it there; remove the assets/ copy)"
            )

    return problems, notes, checked


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", action="append", default=[],
                    help="check only this content file (repeatable)")
    ap.add_argument("--quiet", action="store_true", help="only report problems")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    files = ([Path(f).resolve() for f in args.file] if args.file
             else sorted(CONTENT.rglob("*.md")))
    if not files:
        print("hero-paths: ERROR: no content files found — is this the site repo?",
              file=sys.stderr)
        return 2

    problems: list[str] = []
    notes: list[str] = []
    checked = 0
    for path in files:
        if not path.is_file():
            problems.append(f"{path}: no such file")
            continue
        p, n, c = audit_file(path)
        problems += p
        notes += n
        checked += c

    if notes and not args.quiet:
        print(f"hero-paths: {len(notes)} duplicate(s) to clean up")
        for note in notes:
            print("  note: " + note)

    if args.verbose and not args.quiet:
        print(f"hero-paths: inspected {len(files)} file(s)")

    if problems:
        print("hero paths do not resolve:")
        for p in problems:
            print("  " + p)
        print(f"coverage: {checked} paths")
        return 1

    if not args.quiet:
        print("hero-path check: OK — every hero and cover path names a file that exists")
    print(f"coverage: {checked} paths")
    return 0


if __name__ == "__main__":
    sys.exit(main())
