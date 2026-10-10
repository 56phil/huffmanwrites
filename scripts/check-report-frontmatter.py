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

# A link whose visible text is a placeholder rather than the thing cited.
#
# Two defects in one, and both matter on a publishing job. A reader sees the
# literal word "text" where a title should be. And `check-links.py --titles` has
# nothing to compare, so the only check that catches a link resolving to the
# WRONG page goes blind on that citation — which is what happened to the Senate
# report: `... ([text](url))` gave it zero comparable anchors, so the wrong-page
# check could not see the piece at all. The citation prose already names the
# source, so the fix is to make that name the link.
TEXT_ANCHOR = re.compile(
    r"\[(text|link|here|source|pdf|article|this)\]\(\s*https?://", re.I
)

# A work title doubled by a botched anchor rewrite: `*Meditations[*Meditations*
# 10.16](url)`, which renders as literal `*MeditationsMeditations 10.16` with a
# stray asterisk (the inner `*` does not italicise once it follows a `*` with no
# space). Introduced on 2026-09-27 by the batch that converted `[text]` anchors
# to work titles: the author's original was `*Meditations* 10.16 … , [text](url)`
# and the rewrite kept the italic span and prefixed a link, producing the doubled
# form in 27 published lines. The reader-visible damage is the doubled title; the
# gate exists so the NEXT such batch cannot ship it, and so these are found by a
# rule rather than by eye. Two groups that must match is the tell — a real
# citation never names the same work twice in a row.
DOUBLED_WORK_TITLE = re.compile(r"\*([^*\[\]]+?)\[\*\1")


def malformed_citation_problems(body: str) -> "list[str]":
    """Citations a rewrite mangled, independent of frontmatter validity."""
    hit = DOUBLED_WORK_TITLE.search(body)
    if not hit:
        return []
    return [
        f"a doubled work title in a citation: {hit.group(0)!r} — the anchor "
        f"rewrite left the title twice, and it renders as "
        f"“{hit.group(1)}{hit.group(1)}” with a stray asterisk. The correct "
        f"form is [*{hit.group(1)}* <rest>](url)."
    ]


def split_frontmatter(text: str) -> "tuple[str, str] | None":
    """Return (frontmatter, body), or None if the file has no usable block.

    The opening fence is matched as a LINE, not by splitting on the literal
    `---\\n`. One file in this corpus opens with `--- ` (a trailing space) and
    Hugo renders it correctly, but `split("---\\n", 2)` skipped that fence and
    landed on the CLOSING one, so the splitter handed back the frontmatter block
    as if it were the body and the gate reported "no title in frontmatter" for a
    file that has one. Measured 2026-09-27: exactly one file
    (`digests/stoic-saturday-rule-of-law.md`), but the failure is silent and
    would have applied to any future file with the same whitespace.
    """
    if not text.startswith("---"):
        return None
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1:])
    return None


def field(front: str, name: str) -> "str | None":
    """Read one frontmatter scalar. Quoted or bare; first occurrence wins."""
    m = re.search(rf"^{re.escape(name)}\s*:\s*(.*)$", front, re.M)
    return m.group(1).strip().strip("\"'") if m else None


def validate(path: "Path | str", hero_plate: "str | None" = None,
             now: "datetime | None" = None, slack_seconds: int = 300,
             future_ok: bool = False) -> "list[str]":
    """Every reason this file must not be published. Empty list means publish.

    `hero_plate` pins the series plate when a series uses one fixed pair of
    images across every installment (`105-senate-race-report`, and the same for
    the docket and Chiefs report). The skill says to copy those four fields
    verbatim; this is what makes "verbatim" checkable rather than trusted, and a
    series that quietly drifts to a different plate loses the visual identity
    the plate exists to hold.

    `future_ok` is the scheduling mode: it drops the "date ahead of the clock"
    rule for a file that is *deliberately* dated to an hour that has not arrived,
    whose page the deploy publishes at the stroke of that hour (the 12:00 UTC
    build in `.github/workflows/hugo.yml`, or a later push). The rule exists
    because a future date normally means a mistake — a `date`/`lastmod` typo, or
    a report dated tomorrow — and Hugo skips such a page silently, so the run
    reports success and the reader gets nothing. Corpus mode is the one place
    that cannot tell an appointment from a typo by the clock alone, because it
    runs on every other day and the same file is future today and past on its
    date. The publishing runners and the `--file` mode stay strict: a job that
    has just written "today" must never be permitted a future date. Do NOT
    default this on.
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

    problems.extend(malformed_citation_problems(body))

    placeholders = TEXT_ANCHOR.findall(body)
    if placeholders:
        problems.append(
            f"{len(placeholders)} link(s) whose visible text is a placeholder "
            f"({', '.join(sorted({p for p in placeholders}))}) — the reader sees "
            f"that word instead of the title, and check-links.py --titles has "
            f"nothing to compare, so the wrong-page check is blind on it. Make "
            f"the citation's own title the link text."
        )

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
            if not future_ok and stamp > reference + timedelta(seconds=slack_seconds):
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


def published_posts() -> "list[Path]":
    """Every published post in content/, for the rules that are not series-specific.

    `series_installments()` above answers "what carries the report contract" —
    `draft: false`, `featuredOnHome`, the hero fields. This answers a different
    question: "what does a reader actually see", which is every non-draft page
    under `content/posts/`. The anchor rule is the latter kind. It applies to all
    of them because a placeholder anchor is a reader-facing defect wherever it
    appears, and because `check-links.py --titles` goes blind on it wherever it
    appears — a `[text]` link in a book summary hides a wrong-page link just as
    effectively as one in a report, and nothing else watches those files.
    """
    out: "list[Path]" = []
    for path in sorted((REPO / "content" / "posts").rglob("*.md")):
        if path.name == "_index.md":
            continue
        split = split_frontmatter(path.read_text(encoding="utf-8", errors="ignore"))
        if split is None:
            continue
        if field(split[0], "draft") == "true":
            continue
        out.append(path)
    return out


def anchor_problems(path: "Path | str") -> "list[str]":
    """The citation-anchor rules alone, for one file: no placeholder anchor, and
    no work title doubled by a botched rewrite."""
    p = Path(path)
    if not p.is_file():
        return []
    split = split_frontmatter(p.read_text(encoding="utf-8", errors="ignore"))
    if split is None:
        return []
    problems = malformed_citation_problems(split[1])
    placeholders = TEXT_ANCHOR.findall(split[1])
    if placeholders:
        problems.append(
            f"{len(placeholders)} link(s) whose visible text is a placeholder "
            f"({', '.join(sorted({x for x in placeholders}))}) — the reader sees that "
            f"word instead of the title, and check-links.py --titles has nothing to "
            f"compare, so the wrong-page check is blind on it. Make the citation's "
            f"own title the link text."
        )
    return problems


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
    ap.add_argument("--anchors-corpus", action="store_true",
                    help="check the placeholder-anchor rule on EVERY published "
                         "post, not only series installments")
    args = ap.parse_args()

    if args.anchors_corpus:
        targets = published_posts()
        bad = []
        for path in targets:
            for problem in anchor_problems(path):
                bad.append((path, problem))
        for path, problem in bad:
            print(f"  {path.relative_to(REPO)}:", file=sys.stderr)
            print(f"    - {problem}", file=sys.stderr)
        if bad:
            print(f"report frontmatter: NOT PUBLISHABLE — {len(bad)} of "
                  f"{len(targets)} published posts use a placeholder anchor",
                  file=sys.stderr)
            print(f"coverage: {len(targets)} posts")
            return 1
        print(f"anchor check: OK — all {len(targets)} published posts name their links")
        print(f"coverage: {len(targets)} posts")
        return 0

    if args.corpus:
        targets = series_installments()
        failures = 0
        for path in targets:
            # Corpus mode is a scheduling scan, and a deliberately future-dated
            # appointment is exactly what a publishing series can legitimately
            # carry between its commit and its hour (the Weekly Satire's Monday
            # 07:00 embargo). The date rule stays live in --file mode and in the
            # runners, where "today" is the only date a just-written report may
            # carry. See validate()'s `future_ok` note.
            problems = validate(path, future_ok=True)
            if problems:
                failures += 1
                print(f"  {path.relative_to(REPO)}:", file=sys.stderr)
                for p in problems:
                    print(f"    - {p}", file=sys.stderr)
        if failures:
            print(f"report frontmatter: NOT PUBLISHABLE — {failures} of "
                  f"{len(targets)} series installments", file=sys.stderr)
            print(f"coverage: {len(targets)} posts")
            return 1
        print(f"report frontmatter: OK — all {len(targets)} series installments "
              f"are publishable")
        print(f"coverage: {len(targets)} posts")
        return 0

    if not args.file:
        ap.error("one of --file or --corpus is required")

    problems = validate(args.file, hero_plate=args.hero_plate)
    if problems:
        print(f"report frontmatter: NOT PUBLISHABLE — {len(problems)} problem(s) "
              f"in {args.file}", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        print(f"coverage: 1 posts")
        return 1
    print(f"report frontmatter: OK — {Path(args.file).name} is publishable")
    print(f"coverage: 1 posts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
