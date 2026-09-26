#!/usr/bin/env python3
"""Every hero path in frontmatter must point at a file that exists.

Why this exists, and why it is not redundant with `check-render-integrity.py`:

`check-render-integrity.py` catches a broken hero too, but it needs a full
`hugo` build and it runs once a week from the site-audit job. The reports that
carry heroes are written by **scheduled jobs** that publish or draft with no
human review, and their runners do not build the `public/` tree. A hero path
with a typo in it is invisible to all of them:

  - `hugo` does **not** fail on a missing image. The build succeeds.
  - The page returns 200 and renders an empty box where the hero should be.
  - The runner's own gates (quotes, links, dashes, prepositions) do not read
    frontmatter image paths.

So the defect ships and the first person to see it is a reader. This gate costs
nothing and closes it: read every content file, collect `hero_desktop` and
`hero_mobile`, and assert each names a file under `static/`.

Exit codes:
  0  every hero path resolves
  1  at least one does not
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONTENT = REPO / "content"
HERO_FIELDS = ("hero_desktop", "hero_mobile", "hero")
FIELD_RE = re.compile(r'^(hero_desktop|hero_mobile|hero):\s*"?([^"\n]+?)"?\s*$', re.M)


def frontmatter(text: str) -> str:
    """The leading `---` block, or "" when the file has none."""
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[:end] if end != -1 else ""


def check(verbose: bool = False) -> list[str]:
    problems = []
    checked = 0
    for path in sorted(CONTENT.rglob("*.md")):
        fm = frontmatter(path.read_text(encoding="utf-8", errors="ignore"))
        for field, value in FIELD_RE.findall(fm):
            value = value.strip().strip("'\"")
            if not value:
                continue
            checked += 1
            target = REPO / "static" / value.lstrip("/")
            if not target.is_file():
                rel = path.relative_to(REPO).as_posix()
                problems.append(f"{rel}: {field} -> static/{value} (no such file)")
            elif verbose:
                print(f"  ok  {path.relative_to(REPO).as_posix()}: {field} -> {value}")
    print(f"hero paths checked: {checked}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", action="append", default=[],
                    help="check only this content file (repeatable)")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    global CONTENT
    if args.file:
        problems = []
        for f in args.file:
            p = Path(f)
            fm = frontmatter(p.read_text(encoding="utf-8", errors="ignore"))
            for field, value in FIELD_RE.findall(fm):
                value = value.strip().strip("'\"")
                if value and not (REPO / "static" / value.lstrip("/")).is_file():
                    problems.append(f"{p.name}: {field} -> static/{value} (no such file)")
        if problems:
            print("hero paths do not resolve:")
            for p in problems:
                print("  " + p)
            return 1
        print(f"{len(args.file)} file(s): hero paths OK")
        return 0

    problems = check(args.verbose)
    if problems:
        print("hero paths do not resolve:")
        for p in problems:
            print("  " + p)
        return 1
    print("hero-path check: OK — every hero path names a file that exists")
    return 0


if __name__ == "__main__":
    sys.exit(main())
