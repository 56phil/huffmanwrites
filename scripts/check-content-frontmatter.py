#!/usr/bin/env python3
"""Frontmatter fields that the layouts depend on must be present and non-empty.

Why this exists:

Several templates key off frontmatter fields, and Hugo does not fail when one is
missing — it renders a blank spot or falls back to an unintended default, and
the build still succeeds. `check-report-frontmatter.py` covers the recurring
report *series* and their hero plates; nothing covered the ordinary content
tree. Each rule below is a shipped-or-latent failure:

  R1  `lastmod`. CLAUDE.md states every Hugo post should carry it. A post
      without it has no "last updated" signal and drifts out of any freshness
      ordering silently.

  R2  `sort_key`. The book-summary list (`layouts/posts/summaries/list.html`)
      orders the hub with `ByParam "sort_key"`. A summary missing the key is
      not rejected — it sorts by zero-value and lands wherever Hugo's fallback
      puts it, quietly misordering a section whose whole purpose is order.

  R3  book fields. `content/books/<slug>/index.md` renders through
      `layouts/books/single.html`, which reads `title`, `subtitle`, `image`,
      `image_desktop`, `image_mobile`, `image_alt`, `hero_caption`,
      `image_caption`, `link`, `lastmod`. A missing one produces an empty hero,
      a broken cover, or an absent caption on a page no other gate reads. Two
      fields carry a documented exception:

        * `link` is required only when the page is not marked unreleased (no
          `availability:` key). A book not yet released has no purchase URL;
          `layouts/books/single.html` already guards the button with
          `{{ if .Params.link }}`, so an unpublished book rendering no button is
          correct, and a *published* book with no `link` is the defect.

        * `subtitle` may be ABSENT, but never blank. *The Stoic Citizen* has no
          subtitle: its printed cover sets `subtitle: ''` (measured 2026-10-08 in
          the book's own cover configuration,
          `LaTeX/AllMyBooks/tsc/cover/cover.md`). Inventing a subtitle here would
          put a line on the site that the book does not carry, so an absent key
          is respected. A key that is present and empty is still a violation:
          that is a mangled field rather than a design.

  R4  hero vs cover caption. CLAUDE.md: `hero_caption` is for the hero image,
      `image_caption` is for the cover, and the two must never be the same.
      An equal pair means one was copy-pasted and the page shows the wrong
      description under one of the two images.

Exit codes:
  0  every rule holds
  1  at least one violation
  2  cannot run (the content tree is missing)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONTENT = REPO / "content"
POSTS = CONTENT / "posts"
SUMMARIES = POSTS / "summaries"
BOOKS = CONTENT / "books"

# The ten fields `layouts/books/single.html` reads off a book page.
BOOK_FIELDS = (
    "title", "subtitle", "image", "image_desktop", "image_mobile",
    "image_alt", "hero_caption", "image_caption", "link", "lastmod",
)


def frontmatter(text: str) -> str:
    """The leading `---` block, or "" when the file has none."""
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[:end] if end != -1 else ""


def field_value(fm: str, name: str) -> "str | None":
    """The single-line value of `name`, quotes stripped, or None if absent.

    None means the key is not present at all; "" means present and empty. The
    two are the same defect here — a rule that requires a field fires on both —
    but keeping them distinct lets a caller tell "missing" from "blank".
    """
    m = re.search(rf'^{re.escape(name)}:[ \t]*(.*)$', fm, re.M)
    if not m:
        return None
    return m.group(1).strip().strip("'\"").strip()


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return path.as_posix()


def audit_file(path: Path) -> list[str]:
    """Return the violation lines for one content file (empty when clean)."""
    fm = frontmatter(path.read_text(encoding="utf-8", errors="ignore"))
    r = rel(path)
    problems: list[str] = []

    # R1: every post carries a non-empty lastmod.
    if POSTS in path.parents and path.name != "_index.md":
        if not field_value(fm, "lastmod"):
            problems.append(f"{r}: R1 lastmod missing or empty")

    # R2: every book summary carries a non-empty sort_key.
    if path.parent == SUMMARIES and path.name != "_index.md":
        if not field_value(fm, "sort_key"):
            problems.append(f"{r}: R2 sort_key missing or empty")

    # R3 + R4: book pages.
    if path.parent.parent == BOOKS and path.name == "index.md":
        unreleased = bool(field_value(fm, "availability"))
        for f in BOOK_FIELDS:
            if f == "link" and unreleased:
                # A book not yet released has no purchase URL; the layout
                # omits the button, so an absent link is correct here.
                continue
            if f == "subtitle":
                # Absent is allowed (`The Stoic Citizen` has no subtitle — its
                # printed cover sets `subtitle: ''`); present and empty is not,
                # because that is a mangled field rather than a design.
                if field_value(fm, "subtitle") == "":
                    problems.append(f"{r}: R3 book field 'subtitle' present but empty")
                continue
            if not field_value(fm, f):
                problems.append(f"{r}: R3 book field {f!r} missing or empty")
        hero = field_value(fm, "hero_caption")
        cover = field_value(fm, "image_caption")
        if hero and cover and hero == cover:
            problems.append(
                f"{r}: R4 hero_caption equals image_caption ({hero!r})")

    return problems


def scope_files() -> list[Path]:
    """Content files any rule can apply to, sorted, each read exactly once."""
    out = [
        p for p in POSTS.rglob("*.md")
        if p.name != "_index.md"
    ]
    out += [p for p in sorted(BOOKS.glob("*/index.md"))]
    return sorted(set(out))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", action="append", default=[],
                    help="check only this content file (repeatable)")
    ap.add_argument("--quiet", action="store_true", help="only report problems")
    args = ap.parse_args()

    if not CONTENT.is_dir():
        print(f"content frontmatter: cannot run — {CONTENT} does not exist",
              file=sys.stderr)
        print("coverage: 0 files")
        return 2

    if args.file:
        files = [(Path(f) if Path(f).is_absolute() else (REPO / f)).resolve()
                 for f in args.file]
    else:
        files = scope_files()

    problems: list[str] = []
    for path in files:
        problems += audit_file(path)

    for p in problems:
        print(p)

    if not args.quiet:
        print(f"content frontmatter: {len(files)} file(s) checked")

    if problems:
        if not args.quiet:
            print(f"content frontmatter: {len(problems)} violation(s)")
        print(f"coverage: {len(files)} files")
        return 1

    if not args.quiet:
        print("content frontmatter: OK — every required field is present and "
              "the hero and cover captions differ")
    print(f"coverage: {len(files)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
