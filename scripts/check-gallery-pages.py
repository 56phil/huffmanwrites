#!/usr/bin/env python3
"""Guard the gallery pagination contract.

The gallery landing page has two independent sources of truth for its page
count:

  1. `data/gallery.yml` — the item list. The layout derives totalPages from
     its length: ceil(len / itemsPerPage).
  2. `content/gallery/page/N.md` — hand-written stubs, one per page. Hugo
     only generates `/gallery/page/N/` if stub N exists.

Hugo's paginator is not used here, so nothing reconciles the two. When the
item count crosses an itemsPerPage boundary, the layout starts rendering a
link to a page whose stub was never created, and that link 404s.

That is not hypothetical. On 2026-09-18 commit 2fe605b took the gallery from
95 to 97 items, making page 9 required. No `9.md` was added, so every gallery
page linked to `/gallery/page/9/` and the deployed page 8 "Next" button
dead-ended in a 404. It had happened four times before (pages 6, 7, and 8
were each added only after the fact), which is why this is a script.

The item count is read from the layout rather than hardcoded so this check
cannot silently drift from the page size the layout actually uses.

Exit codes:
  0  contract satisfied
  1  one or more page stubs missing (the failure this exists to catch)
  2  could not determine the contract (missing input, unparseable layout)

Usage:
  check-gallery-pages.py           # verify; exit 1 on mismatch
  check-gallery-pages.py --fix     # create any missing stubs, then verify
  check-gallery-pages.py --quiet   # only report problems
"""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GALLERY_DATA = REPO / "data" / "gallery.yml"
GALLERY_LAYOUT = REPO / "layouts" / "_default" / "gallery.html"
STUB_DIR = REPO / "content" / "gallery" / "page"

# The stub body below mirrors the existing stubs byte-for-byte in structure.
# Every stub carries the same title/description; only lastmod differs.
STUB_TEMPLATE = """---
title: "Art Gallery"
layout: "gallery"
description: "A visual journey through the themes and insights of HuffmanWrites."
lastmod: {lastmod}
---
"""


def _die(msg: str, code: int = 2) -> "None":
    print(f"gallery-pages: ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def items_per_page() -> int:
    """Read itemsPerPage out of the layout.

    Single source of truth: if someone changes the layout's page size, this
    check follows automatically instead of asserting a stale constant.
    """
    if not GALLERY_LAYOUT.is_file():
        _die(f"layout not found: {GALLERY_LAYOUT.relative_to(REPO)}")
    text = GALLERY_LAYOUT.read_text(encoding="utf-8")
    m = re.search(r"\$itemsPerPage\s*:=\s*(\d+)", text)
    if not m:
        _die(
            "could not find '$itemsPerPage := <n>' in "
            f"{GALLERY_LAYOUT.relative_to(REPO)} — the layout changed shape; "
            "update this guard to match."
        )
    n = int(m.group(1))
    if n <= 0:
        _die(f"layout declares a non-positive itemsPerPage ({n})")
    return n


def item_count() -> int:
    """Count gallery entries.

    Counts top-level `- image:` keys rather than parsing YAML so the check
    needs no PyYAML dependency and matches how the layout sees the data
    (`len .Site.Data.gallery`). Quoted and unquoted values both match.
    """
    if not GALLERY_DATA.is_file():
        _die(f"gallery data not found: {GALLERY_DATA.relative_to(REPO)}")
    text = GALLERY_DATA.read_text(encoding="utf-8")
    return len(re.findall(r"^\s*-\s+image:\s*\S", text, re.MULTILINE))


def existing_stubs() -> "set[int]":
    if not STUB_DIR.is_dir():
        _die(f"stub directory not found: {STUB_DIR.relative_to(REPO)}")
    nums = set()
    for p in STUB_DIR.glob("*.md"):
        if p.stem.isdigit():
            nums.add(int(p.stem))
    return nums


def main() -> int:
    ap = argparse.ArgumentParser(description="Guard the gallery pagination contract.")
    ap.add_argument(
        "--fix",
        action="store_true",
        help="create missing stubs (uses today's date for lastmod)",
    )
    ap.add_argument("--quiet", action="store_true", help="only report problems")
    args = ap.parse_args()

    per_page = items_per_page()
    items = item_count()
    if items == 0:
        _die("gallery data contains no items — refusing to guess the contract")

    total_pages = (items + per_page - 1) // per_page
    required = set(range(2, total_pages + 1))
    present = existing_stubs()
    missing = sorted(required - present)
    # A stub past the last needed page is not a 404 risk, but it means the
    # gallery shrank and stale stubs are serving empty pages. Surface it.
    surplus = sorted(p for p in present - required if p > total_pages)

    if not args.quiet:
        print(
            f"gallery-pages: {items} items / {per_page} per page "
            f"= {total_pages} pages (page 1 is the index)"
        )

    if args.fix and missing:
        today = _dt.date.today().isoformat()
        for n in missing:
            path = STUB_DIR / f"{n}.md"
            path.write_text(STUB_TEMPLATE.format(lastmod=today), encoding="utf-8")
            print(f"gallery-pages: created {path.relative_to(REPO)}")
        present |= set(missing)
        missing = []

    if missing:
        print(
            "gallery-pages: FAIL — missing page stub(s): "
            + ", ".join(f"{n}.md" for n in missing),
            file=sys.stderr,
        )
        print(
            "  The gallery layout derives its page count from data/gallery.yml, "
            "but Hugo only builds /gallery/page/N/ when the stub exists.\n"
            "  Every gallery page links to the missing page, so those links 404.\n"
            "  Fix: scripts/check-gallery-pages.py --fix",
            file=sys.stderr,
        )
        return 1

    if surplus:
        print(
            "gallery-pages: WARN — stub(s) beyond the last required page: "
            + ", ".join(f"{n}.md" for n in surplus),
            file=sys.stderr,
        )

    if not args.quiet:
        print("gallery-pages: OK — every required page stub is present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
