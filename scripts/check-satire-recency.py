#!/usr/bin/env python3
"""The Weekly Satire's subject must be news from the seven days before publication.

Philip, 2026-10-27: "I want the subject of the satire piece to be a news item
from the preceding week." The skill says it, but a skill is an instruction to a
writer that publishes unreviewed, and the one thing a series that publishes
without review cannot rely on is an instruction with no check behind it. This is
the check, and it is deliberately the narrow, checkable half.

  A dated source line in `## Sources` is the only place a fetched page's date is
  recorded, so "the piece is about this week's news" is checkable as "at least
  MIN_IN_WINDOW source lines carry a date inside the window". A piece whose
  sources are all older than that is a piece written about old news, which is the
  defect this exits non-zero on.

What it does NOT check, on purpose: whether the *subject* is the item the sources
describe. That is a judgement about the prose, and a gate that guessed at it
would fail correct pieces — worse than showing a human the dates. The rule stands
in the skill; this is its floor.

The window is (publish date - 7 days, publish date], both taken from the
article's own `date:` frontmatter unless `--date` overrides it. Nothing here
reads the clock unless it has neither, which is why the tests can pin it.

Scope note: this gate runs from the runner on the piece that run wrote, and is
deliberately NOT in the corpus gate set. The four pre-written installments
(2026-10-12 through 11-02) predate the rule, and three of them are about news ten
to twenty-five days old on their own date; a corpus entry would turn CI red on
published, reviewed pages.

Usage:
  check-satire-recency.py --file <path>               # publish date from frontmatter
  check-satire-recency.py --file <path> --date 2026-11-09
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import sys

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
PUBLISH_DATE_RE = re.compile(r"^date:\s*(\d{4}-\d{2}-\d{2})", re.M)
SOURCES_HEADING_RE = re.compile(r"^##\s+Sources\s*$", re.M)
HEADING_RE = re.compile(r"^##\s+\S", re.M)

MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9, "oct": 10,
    "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}
_MONTH = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?"
_MONTH += r"|Aug(?:ust)?|Sept?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
ISO_DATE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
MONTH_FIRST = re.compile(rf"\b({_MONTH})\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?,?\s+(\d{{4}})\b", re.I)
DAY_FIRST = re.compile(rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+({_MONTH})\.?,?\s+(\d{{4}})\b", re.I)
# The site's own citation style is APA-ish — "Habeshian, S. (2026, October 10)." —
# so the year-first shape is the one the Sources list will actually use.
APA_STYLE = re.compile(rf"\(\s*(\d{{4}}),\s*({_MONTH})\.?\s+(\d{{1,2}})\s*\)", re.I)

WINDOW_DAYS = 7
MIN_IN_WINDOW = 2


def frontmatter(text: str) -> str:
    m = FRONTMATTER_RE.match(text)
    return m.group(1) if m else ""


def publish_date(text: str, override: str | None) -> dt.date | None:
    if override:
        return dt.date.fromisoformat(override)
    m = PUBLISH_DATE_RE.search(frontmatter(text))
    if m:
        return dt.date.fromisoformat(m.group(1))
    return None


def sources_block(text: str) -> str | None:
    """The `## Sources` section body, or None when the file has no such heading."""
    m = SOURCES_HEADING_RE.search(text)
    if not m:
        return None
    rest = text[m.end():]
    nxt = HEADING_RE.search(rest)
    return rest[: nxt.start()] if nxt else rest


def _safe(year: str, month: int, day: str) -> dt.date | None:
    try:
        return dt.date(int(year), month, int(day))
    except ValueError:
        return None


def dates_in(line: str) -> list[dt.date]:
    out: list[dt.date] = []
    for y, mo, d in ISO_DATE.findall(line):
        got = _safe(y, int(mo), d)
        if got:
            out.append(got)
    for mon, d, y in MONTH_FIRST.findall(line):
        m = MONTHS.get(mon.lower().rstrip("."))
        got = _safe(y, m, d) if m else None
        if got:
            out.append(got)
    for d, mon, y in DAY_FIRST.findall(line):
        m = MONTHS.get(mon.lower().rstrip("."))
        got = _safe(y, m, d) if m else None
        if got:
            out.append(got)
    for y, mon, d in APA_STYLE.findall(line):
        m = MONTHS.get(mon.lower().rstrip("."))
        got = _safe(y, m, d) if m else None
        if got:
            out.append(got)
    return out


def source_lines(block: str) -> list[str]:
    """One entry per source: bullet or numbered-item lines, else non-blank lines."""
    bullets = [ln for ln in block.splitlines() if re.match(r"^\s*(?:[-*+]|\d+\.)\s+\S", ln)]
    if bullets:
        return bullets
    return [ln for ln in block.splitlines() if ln.strip()]


def check(text: str, pub: dt.date) -> tuple[list[str], int, int, int]:
    """Returns (problems, entries, dated, in_window)."""
    block = sources_block(text)
    if block is None:
        return (["no `## Sources` section: the week's sources cannot be dated"], 0, 0, 0)

    entries = source_lines(block)
    dated = 0
    in_window = 0
    stale: list[str] = []
    window_start = pub - dt.timedelta(days=WINDOW_DAYS)

    for line in entries:
        ds = dates_in(line)
        if not ds:
            continue
        dated += 1
        if any(window_start <= d <= pub for d in ds):
            in_window += 1
        else:
            newest = max(ds)
            age = (pub - newest).days
            label = re.sub(r"\s+", " ", line.strip())[:110]
            stale.append(f"{newest.isoformat()} ({age}d old): {label}")

    problems: list[str] = []
    if in_window < MIN_IN_WINDOW:
        problems.append(
            f"only {in_window} source(s) dated inside {window_start.isoformat()}..{pub.isoformat()}; "
            f"{MIN_IN_WINDOW} are required, because the piece must be about the week before it publishes"
        )
        for s in stale:
            problems.append(f"outside the window: {s}")
        if dated == 0:
            problems.append("no source line carries a readable date (YYYY-MM-DD, Month D, YYYY, or D Month YYYY)")
    return problems, len(entries), dated, in_window


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", required=True, help="the article to check")
    ap.add_argument("--date", help="publish date (YYYY-MM-DD); defaults to the frontmatter `date:`")
    args = ap.parse_args()

    path = pathlib.Path(args.file)
    text = path.read_text(encoding="utf-8")
    pub = publish_date(text, args.date)
    if pub is None:
        print(f"  {path.name}: no publish date (no `date:` in frontmatter and no --date)")
        print("coverage: 0 sources")
        return 1

    problems, entries, dated, in_window = check(text, pub)
    if problems:
        print(f"recency: {path.name} is not about the week before {pub.isoformat()}")
        for p in problems:
            print(f"  {p}")
        print(f"coverage: {entries} sources")
        return 1

    print(f"recency: OK — {in_window} of {entries} source(s) dated within "
          f"{WINDOW_DAYS} days before {pub.isoformat()}")
    print(f"coverage: {entries} sources")
    return 0


if __name__ == "__main__":
    sys.exit(main())
