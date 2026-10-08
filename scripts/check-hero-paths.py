#!/usr/bin/env python3
"""Every image path in frontmatter must resolve, and a book cover must live in `assets/`.

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

Two rules, both from a failure that shipped:

  1. **Every path resolves somewhere.** `hero`, `hero_desktop`, `hero_mobile`,
     `image`, `image_desktop` and `image_mobile` are read by two different
     pipelines: `partials/img.html` and the book card shortcodes resolve through
     `resources.Get`, which reads `assets/`, while a few section layouts emit
     `<img src="{{ .Params.image }}">` verbatim, which is served from `static/`.
     A path that resolves in NEITHER renders nothing, so the gate requires one
     of the two homes to hold the file. It does NOT police the repo's existing
     duplication of article heroes across both homes (345 identical files, an
     established arrangement, because direct-`src` layouts need `static/` and the
     processing pipeline needs `assets/`).

  2. **A book cover must be in `assets/`.** A book page's `image` is rendered
     only through `resources.Get`: `partials/img.html` (via
     `layouts/books/single.html`), `shortcodes/book.html` and
     `shortcodes/book_catalog.html`. A cover placed only in `static/` therefore
     builds green, warns once, and renders the `Cover Coming Soon` placeholder on
     a published page. Measured 2026-10-08: the covers lived in two homes, one of
     them stale — `static/img/books/unstuck.jpg` and
     `assets/img/books/unstuck.jpg` had **different bytes**, so the site served
     art the build never rendered. Those copies were removed, and this rule is
     what keeps the second home from coming back. A cover present in BOTH homes
     is reported: as a failure when the bytes differ (the reader can see the
     wrong image), as a note when they are identical.

Exit codes:
  0  every path resolves and no book cover is duplicated with different bytes
  1  at least one path resolves nowhere, or a duplicated cover differs
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

        if field == "image" and is_book(path):
            if "assets" not in found:
                problems.append(
                    f"{rel}: {field} -> {value} (a book cover must be in assets/; "
                    f"the cover is rendered only through resources.Get, so a "
                    f"static/ copy publishes a placeholder)"
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
