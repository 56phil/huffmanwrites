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


def page_count(items: int, per_page: int) -> int:
    """Pages needed for `items`, rounded UP.

    Rounding down leaves the final page unbuilt while the paginator still links
    to it, which is a live 404 — the 2026-09-18 page 9 incident. Named and
    separated so a test can call this rule rather than restating its formula:
    a test that recomputes the arithmetic passes even when this function is
    wrong.
    """
    if per_page <= 0:
        _die(f"items per page must be positive, got {per_page}")
    return (items + per_page - 1) // per_page


def latest_entries() -> "list[tuple[str, str, bool]]":
    """(title, glob, has_link_fallback) for every card resolving to the newest
    installment.

    A recurring series shows one card and that card must lead to the current
    installment, so the entry carries `latest: /posts/<section>/<series>-*` and
    the layout resolves it at build time (2026-09-26). The third element matters
    because `latest` only overrides `link` **on a match**: a card whose glob
    matches nothing keeps whatever `link` it carries, so a fallback is what
    keeps it from being a picture with no destination.
    """
    text = GALLERY_DATA.read_text(encoding="utf-8")
    blocks = [b for b in re.split(r"(?=^\s*-\s+image:)", text, flags=re.M) if b.strip()]
    out = []
    for b in blocks:
        m = re.search(r"^\s*latest:\s*(\S+)\s*$", b, re.M)
        if not m:
            continue
        t = re.search(r"^\s*title:\s*(.+?)\s*$", b, re.M)
        has_link = bool(re.search(r"^\s*link:\s*\S", b, re.M))
        out.append((t.group(1).strip().strip('"') if t else "?", m.group(1).strip(),
                    has_link))
    return out


def latest_problems() -> "tuple[list[str], list[str]]":
    """(failures, notes) for the `latest` globs.

    A `latest` glob that matches nothing fails SILENTLY: the layout leaves the
    card on whatever `link` it also carries, so a typo'd prefix leaves a card
    pointing at a stale destination rather than at the series. The pre-`latest`
    mechanism had a different failure — a fixed `link` at a post that does not
    exist renders a link that 404s — and both are worth catching.

    The two cases are separated by what can actually be tested:

      - **The directory does not exist** -> FAILURE. `/posts/essay/` for
        `/posts/essays/` is a typo, and it can never match anything.
      - **The directory exists but nothing matches** -> NOTE. This is the
        legitimate not-yet-started series (the docket report before its first
        run on 2026-10-03). It is indistinguishable from a stem typo by matching
        alone, so it is surfaced rather than failed; whether the card is still
        useful depends on the `link` fallback, which is why the note reports
        what the card will actually do.
    """
    failures: list[str] = []
    notes: list[str] = []
    for title, glob, has_fallback in latest_entries():
        dirname = Path(glob.rstrip("*")).parent.as_posix().lstrip("/")
        stem = Path(glob.rstrip("*")).name
        # The glob is written as a site path (/posts/essays/foo-*); content
        # lives under content/ with the same shape.
        search_dir = REPO / "content" / dirname
        if not search_dir.is_dir():
            failures.append(
                f"{title}: latest glob '{glob}' points at content/{dirname}/, "
                "which does not exist — this can never match a page."
            )
            continue
        matches = [p for p in search_dir.rglob("*.md") if p.name.startswith(stem)]
        if not matches:
            if has_fallback:
                notes.append(
                    f"{title}: latest glob '{glob}' matches nothing yet, so the "
                    "card is falling back to its `link`. Expected until the "
                    "series starts; a typo would look the same."
                )
            else:
                notes.append(
                    f"{title}: latest glob '{glob}' matches nothing yet AND the "
                    "card has no `link` fallback — it renders a caption and a "
                    "picture with no way through to any post."
                )
    return failures, notes


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

    total_pages = page_count(items, per_page)
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

    # `latest` globs: a real typo fails, an unstarted series is only noted.
    latest_fail, latest_notes = latest_problems()
    for note in latest_notes:
        print(f"gallery-pages: NOTE — {note}")
    if latest_fail:
        print("gallery-pages: FAIL — bad `latest` glob(s):", file=sys.stderr)
        for f in latest_fail:
            print(f"  {f}", file=sys.stderr)
        return 1

    if not args.quiet:
        print("gallery-pages: OK — every required page stub is present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
