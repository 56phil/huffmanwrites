#!/usr/bin/env python3
"""Gate a report's frontmatter for publication, not for drafting.

The scheduled report jobs used to file a `draft: true` page for review. They now
publish whatever passes every gate (Philip, 2026-09-27), which changes what a
missing field costs: a draft with `draft: true` left in it is a page awaiting
review, and the same page published is a push that deploys nothing while every
gate reports OK. This is the gate that reads the artifact as a publisher rather
than as an editor.

Every rule here is a failure this repo has actually shipped, and each one is
invisible to the build:

  draft: false            a draft flag left true deploys nothing and looks like
                          a successful publish in the log.
  featuredOnHome: true    more than five posts already carry the flag, so the
                          home feed takes the five newest flagged and an
                          unflagged post reaches no reader from the home page.
                          Five Senate reports shipped that way, 2026-09-06 to
                          2026-09-27, and nothing else could see it.
  title/description/date  a page with no description is a search-result snippet
  /lastmod/author         with nothing in it.
  the hero fields         a hero path naming no file does NOT fail the Hugo
                          build — it renders an empty box on a page that ships.
  the date not ahead of   Hugo's `buildFuture: false` skips a future-dated page
  the clock               WITHOUT failing the build, so the run reports success
                          and the report is simply absent. Recorded three times.
  the attribution line    the house signature, and its absence is the only
                          cheap signal that the body was not written to spec.

It lives here rather than in a runner because the date rule needs to parse the
frontmatter's own offset format (`-05:00`), which macOS `date -j -f` cannot
read: it accepts `-0500`, fails on `-05:00`, and reports the failure as usage
text on stderr, so a shell version would silently skip its most important check.
A check that is a function can also be tested, which `scripts/test_gates.py`
does.

Exit codes: 0 publishable, 1 a problem (each printed), 2 usage/no such file.

Usage:
  check-report-frontmatter.py --file content/posts/essays/x.md
  check-report-frontmatter.py --file x.md --hero-plate 105-senate-race-report
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

try:
    from zoneinfo import ZoneInfo

    CT = ZoneInfo("America/Chicago")
except Exception:  # noqa: BLE001 - a missing tz database must not break the run
    CT = timezone(timedelta(hours=-5))

# The fields every report must carry. `draft` and `featuredOnHome` are separate
# because their required VALUES are what matter, not their presence: a page with
# `draft: true` has the field and must still be rejected.
REQUIRED = ("title", "description", "date", "lastmod", "author")
HERO = ("hero_desktop", "hero_mobile", "hero_alt", "hero_caption")
ATTRIBUTION = re.compile(r"^\*PRH \|", re.M)


def split_frontmatter(text: str) -> "tuple[str, str] | None":
    """Return (frontmatter, body), or None if the file has no usable block."""
    if not text.startswith("---"):
        return None
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return None
    return parts[1], parts[2]


def field(front: str, name: str) -> "str | None":
    """Read one frontmatter scalar. Quoted or bare; first occurrence wins."""
    m = re.search(rf"^{re.escape(name)}\s*:\s*(.*)$", front, re.M)
    return m.group(1).strip().strip("\"'") if m else None


def validate(path: "Path | str", hero_plate: "str | None" = None,
             now: "datetime | None" = None, slack_seconds: int = 300) -> "list[str]":
    """Every reason this file must not be published. Empty list means publish.

    `hero_plate` pins the series plate when a series uses one fixed pair of
    images across every installment (`105-senate-race-report`, and the same for
    the docket and Chiefs report). The skill says to copy those four fields
    verbatim; this is what makes "verbatim" checkable rather than trusted, and a
    series that quietly drifts to a different plate loses the visual identity
    the plate exists to hold.
    """
    p = Path(path)
    if not p.is_file():
        return [f"no article at {p}"]
    text = p.read_text(encoding="utf-8")

    split = split_frontmatter(text)
    if split is None:
        return ["no frontmatter block" if not text.startswith("---")
                else "frontmatter block is not closed"]
    front, body = split
    problems: "list[str]" = []

    if field(front, "draft") != "false":
        problems.append(
            f"draft is {field(front, 'draft')!r}, not false — the commit would "
            f"deploy nothing while every gate reported success"
        )
    if field(front, "featuredOnHome") != "true":
        problems.append(
            "featuredOnHome is not true — with more than five flagged posts "
            "already on the site, an unflagged post never reaches the home feed"
        )
    for name in REQUIRED:
        if not field(front, name):
            problems.append(f"no {name} in frontmatter")
    if not ATTRIBUTION.search(body):
        problems.append("missing the closing attribution line (*PRH | …)")

    for name in HERO:
        if not field(front, name):
            problems.append(f"no {name} in frontmatter")
    for name in ("hero_desktop", "hero_mobile"):
        hero_path = field(front, name)
        if hero_path and not (REPO / "static" / hero_path).is_file():
            problems.append(
                f"{name} points at a file that does not exist: static/{hero_path}"
            )

    if hero_plate:
        for name, suffix in (("hero_desktop", "_16x9.webp"), ("hero_mobile", "_4x5.webp")):
            hero_path = field(front, name)
            if hero_path and Path(hero_path).name != f"{hero_plate}{suffix}":
                problems.append(
                    f"{name} is {Path(hero_path).name}, not the series plate "
                    f"{hero_plate}{suffix} — the plate is fixed for the series"
                )

    raw = field(front, "date")
    if raw:
        try:
            stamp = datetime.fromisoformat(raw)
        except ValueError:
            problems.append(f"date {raw!r} is not ISO 8601")
        else:
            if stamp.tzinfo is None:
                stamp = stamp.replace(tzinfo=CT)
            reference = now or datetime.now(CT)
            if reference.tzinfo is None:
                reference = reference.replace(tzinfo=CT)
            if stamp > reference + timedelta(seconds=slack_seconds):
                problems.append(
                    f"date {raw} is ahead of the clock "
                    f"({reference.isoformat(timespec='seconds')}); buildFuture "
                    f"would silently skip the page"
                )
    return problems


def series_installments() -> "list[Path]":
    """Published installments of every declared series, from data/gallery.yml.

    Imported from `check-series-posts.py` rather than re-derived, because the
    globs must not drift between the two gates: a series recognised by one and
    not the other is how the `featuredOnHome` rule came to live in one skill and
    not another. The filename has a hyphen, so it is loaded by path.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "check_series_posts", Path(__file__).with_name("check-series-posts.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out: "list[Path]" = []
    for glob in mod.series_globs():
        for path in mod.installments(glob):
            fm = mod.frontmatter(path.read_text(encoding="utf-8", errors="ignore"))
            if not mod.is_draft(fm):
                out.append(path)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", metavar="PATH",
                    help="the report to check")
    ap.add_argument("--hero-plate", metavar="BASENAME",
                    help="pin the series plate, e.g. 105-senate-race-report")
    ap.add_argument("--corpus", action="store_true",
                    help="check every published installment of every declared "
                         "series; the mode CI runs, where no single file is known")
    args = ap.parse_args()

    if args.corpus:
        targets = series_installments()
        failures = 0
        for path in targets:
            problems = validate(path)
            if problems:
                failures += 1
                print(f"  {path.relative_to(REPO)}:", file=sys.stderr)
                for p in problems:
                    print(f"    - {p}", file=sys.stderr)
        if failures:
            print(f"report frontmatter: NOT PUBLISHABLE — {failures} of "
                  f"{len(targets)} series installments", file=sys.stderr)
            return 1
        print(f"report frontmatter: OK — all {len(targets)} series installments "
              f"are publishable")
        return 0

    if not args.file:
        ap.error("one of --file or --corpus is required")

    problems = validate(args.file, hero_plate=args.hero_plate)
    if problems:
        print(f"report frontmatter: NOT PUBLISHABLE — {len(problems)} problem(s) "
              f"in {args.file}", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print(f"report frontmatter: OK — {Path(args.file).name} is publishable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
