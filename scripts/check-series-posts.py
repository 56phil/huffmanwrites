#!/usr/bin/env python3
"""Every published installment of a recurring series must be flagged for the home page.

Why this exists. `layouts/index.html` fills **Recent Posts** from the posts that
carry `featuredOnHome: true`, and more than five posts already carry it, so an
unflagged post never appears in that section *at all*. It publishes, returns 200,
sits in the archive, and is invisible from the home page — the failure is silent
in every ordinary check, because there is nothing broken to see.

That is what happened to the weekly Senate race report. Its skill listed the
frontmatter fields and simply omitted `featuredOnHome`, so the writer had no way
to know, the runner's gates did not read the field, and **five installments
published between 2026-09-06 and 2026-09-27 without ever reaching the home feed**.
Found by a human noticing the newest one was missing. The Chiefs report escaped it
only because its skill required the flag and `chiefs-report.py --validate` fails
the publish without it.

The rule here is derived, not hardcoded. `data/gallery.yml` declares a series
with a `latest` glob (the same declaration `layouts/_default/gallery.html` uses
to resolve a series card to its newest installment), so a new report series is
covered the moment its card is added — no edit to this file, and no way for the
list to drift out of step with what the site actually treats as a series.

Drafts are skipped: they are not published, so they have no home-feed obligation
until the day they are. A glob matching nothing published yet is a NOTE, not a
failure, for the same reason `check-gallery-pages.py` reports it that way — a
series that has not started is legitimate, and failing it would leave CI red
until its first report lands.

Exit codes:
  0  every published installment of every declared series is flagged
  1  at least one is not
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GALLERY = REPO / "data" / "gallery.yml"
CONTENT = REPO / "content"

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.S)
FLAG_RE = re.compile(r"^featuredOnHome:\s*(true|false)\s*$", re.M)
DRAFT_RE = re.compile(r"^draft:\s*(true|false)\s*$", re.M)


def frontmatter(text: str) -> str:
    m = FRONTMATTER_RE.match(text)
    return m.group(1) if m else ""


def is_flagged(fm: str) -> bool:
    m = FLAG_RE.search(fm)
    return bool(m) and m.group(1) == "true"


def is_draft(fm: str) -> bool:
    m = DRAFT_RE.search(fm)
    return bool(m) and m.group(1) == "true"


def series_globs() -> list[str]:
    """Every `latest:` glob in the gallery — the site's own definition of a series.

    Parsed with a regex rather than PyYAML so the gate has no third-party
    dependency and cannot fail on a machine without it; the file's structure is
    flat enough that the shape is unambiguous.
    """
    if not GALLERY.is_file():
        return []
    text = GALLERY.read_text(encoding="utf-8")
    return [m.group(1).strip().strip("'\"")
            for m in re.finditer(r"^\s*latest:\s*(\S+)\s*$", text, re.M)]


def glob_to_content(glob: str) -> str:
    """`/posts/essays/senate-race-report-*` -> `posts/essays/senate-race-report-*`.

    The glob is a URL path under `/posts/`; the same shape resolves under
    `content/posts/` with the extension attached by the search.
    """
    return glob.lstrip("/")


def installments(glob: str) -> list[Path]:
    rel = glob_to_content(glob)
    # The glob carries no extension, so match the directory and filter by prefix.
    parent, _, tail = rel.rpartition("/")
    directory = CONTENT / parent
    if not directory.is_dir():
        return []
    prefix = tail.rstrip("*")
    return sorted(p for p in directory.glob("*.md") if p.name.startswith(prefix))


def check(verbose: bool = False) -> tuple[list[str], list[str]]:
    """Returns (problems, notes)."""
    problems: list[str] = []
    notes: list[str] = []
    total = 0

    for glob in series_globs():
        posts = installments(glob)
        published = []
        for path in posts:
            fm = frontmatter(path.read_text(encoding="utf-8", errors="ignore"))
            if is_draft(fm):
                continue
            published.append((path, fm))

        if not published:
            notes.append(f"{glob}: no published installment yet")
            continue

        for path, fm in published:
            total += 1
            rel = path.relative_to(REPO).as_posix()
            if not is_flagged(fm):
                problems.append(
                    f"{rel}: part of the series declared by `latest: {glob}` in "
                    f"data/gallery.yml, but carries no `featuredOnHome: true` — "
                    f"the home page takes its five Recent Posts from flagged posts "
                    f"only, so this installment reaches no reader from the home page"
                )
            elif verbose:
                print(f"  ok  {rel}")

    print(f"series installments checked: {total} across {len(series_globs())} series")
    return problems, notes


def check_file(path: Path) -> list[str]:
    """Check one file that belongs to a series, **draft or not**.

    The corpus scan above skips drafts, which is right for the site but wrong for
    a report runner: the draft it just wrote is precisely the file whose flag has
    never been checked, and a corpus scan would report OK while that file is
    unflagged. This is the same blind spot `check-hero-paths.py --file` closes.

    A file that matches no declared series is not a problem — this gate has no
    opinion about standalone posts, which may legitimately go unflagged.
    """
    fm = frontmatter(path.read_text(encoding="utf-8", errors="ignore"))
    if not fm:
        return []
    rel = path.resolve().relative_to(REPO).as_posix() if path.resolve().is_relative_to(REPO) \
        else path.name
    for glob in series_globs():
        prefix = glob_to_content(glob).rpartition("/")[2].rstrip("*")
        parent = glob_to_content(glob).rpartition("/")[0]
        if rel == f"content/{parent}/{path.name}" and path.name.startswith(prefix):
            if is_flagged(fm):
                return []
            return [f"{rel}: series installment without `featuredOnHome: true` — "
                    f"declared by `latest: {glob}`; it would publish and never "
                    f"appear in the home page's Recent Posts"]
    return []


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("--file", help="check one file, draft or published")
    args = ap.parse_args()

    if args.file:
        problems = check_file(Path(args.file))
        if problems:
            for p in problems:
                print(f"  {p}")
            return 1
        print(f"series check: OK — {Path(args.file).name} is flagged for the home page")
        return 0

    problems, notes = check(args.verbose)
    for note in notes:
        print(f"  note: {note}")
    if problems:
        print(f"series posts missing the home flag: {len(problems)}")
        for p in problems:
            print(f"  {p}")
        return 1
    print("series check: OK — every published installment is flagged for the home page")
    return 0


if __name__ == "__main__":
    sys.exit(main())
