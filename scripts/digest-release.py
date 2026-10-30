#!/usr/bin/env python3
"""Release an embargoed Stoic Saturday page, and prove it is served.

Why this exists. The letter's page is dated to its send hour, and Hugo builds
with `buildFuture: false`, so the page is in `main` and in `content/` and is
still not published: it appears only in a deploy that runs *after* that hour.
Until 2026-10-31 the deploy was whatever push happened next, and the only push
that lands between midnight and a 06:00 send is the daily SITREP — so the
newsletter's page was released by a different article's job, and a SITREP
failure took the letter's URL down with it. This is the letter's own trigger:
it dispatches the Pages workflow and then requires the page to answer.

    digest-release.py                        # today's letter, if any
    digest-release.py --date 2026-10-31
    digest-release.py --now 2026-10-31T06:05:00 --dry-run

Exit 0 when there is nothing to release (no letter dated today, or its hour has
not arrived), when the page is already served, and when the release verified.
Exit 1 when the dispatch fails or the page never answers.

A letter stamped later than `LIFT` is released at its own hour, and the run says
so: at that point the page cannot be live before a 06:00 send, and the note is
the only warning before the campaign fires. Silence about a
missing page would be the same failure the job exists to prevent, so the run is
verification, not a fire-and-forget trigger.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parent.parent
SITE = "https://www.huffmanwrites.org"
SECTION = REPO / "content" / "posts" / "digests"
CT = ZoneInfo("America/Chicago")
# The embargo lifts here and the plist fires here; the campaign is scheduled for
# 06:00 CT. The page cannot exist before this minute (Hugo skips a page dated to
# an hour the build has not reached), and it goes live ~2-3 minutes after the
# dispatch, so the lead over the send is what this hour buys.
LIFT = dt.time(5, 53)
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")


def frontmatter(path: Path) -> dict:
    """The handful of fields this job needs, read without a YAML dependency."""
    text = path.read_text()
    if not text.startswith("---"):
        return {}
    raw = text.split("---", 2)[1]
    fields = {}
    for line in raw.splitlines():
        m = re.match(r"^(\w+):\s*(.*?)\s*$", line)
        if m:
            fields[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return fields


def letters(section: Path = SECTION) -> "list[tuple[Path, dt.datetime, dict]]":
    """Every dated letter in the section, oldest first."""
    found = []
    for path in sorted(section.glob("*.md")):
        if path.name.startswith(("_", "TEMPLATE")):
            continue
        fields = frontmatter(path)
        stamp = fields.get("date")
        if not stamp:
            continue
        try:
            when = dt.datetime.fromisoformat(stamp)
        except ValueError:
            continue
        if when.tzinfo is None:
            when = when.replace(tzinfo=CT)
        found.append((path, when, fields))
    found.sort(key=lambda item: item[1])
    return found


def due(day: dt.date, section: Path = SECTION) -> "tuple[Path, dt.datetime, dict] | None":
    """The letter dated for this CT day, if one exists and is not a draft."""
    for path, when, fields in reversed(letters(section)):
        if fields.get("draft", "").lower() == "true":
            continue
        if when.astimezone(CT).date() == day:
            return path, when, fields
    return None


def url_for(path: Path) -> str:
    return f"{SITE}/posts/digests/{path.stem}/"


def served(url: str, timeout: int = 20) -> bool:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def dispatch(branch: str = "main") -> "tuple[int, str]":
    """Ask GitHub to build and deploy main now. workflow_dispatch is not a cron:
    it runs when asked, which is the whole point of this job."""
    done = subprocess.run(
        ["gh", "workflow", "run", "hugo.yml", "--ref", branch],
        capture_output=True, text=True,
    )
    return done.returncode, (done.stderr or done.stdout).strip()


def verify(article: Path) -> int:
    """The same check the publishing tail runs: the page answers, and its own
    `<title>` carries the article's title."""
    done = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "verify-published.py"),
         "--article", str(article)],
        text=True,
    )
    return done.returncode


def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(description="Release an embargoed Stoic Saturday page.")
    ap.add_argument("--date", help="CT date to release (YYYY-MM-DD; default today)")
    ap.add_argument("--now", help="ISO datetime to treat as the wall clock (default: now)")
    ap.add_argument("--section", help="content directory to read instead of the real one")
    ap.add_argument("--branch", default="main", help="branch to deploy (default main)")
    ap.add_argument("--dry-run", action="store_true",
                    help="print what would happen and change nothing")
    args = ap.parse_args(argv)

    now = dt.datetime.fromisoformat(args.now) if args.now else dt.datetime.now(CT)
    if now.tzinfo is None:
        now = now.replace(tzinfo=CT)
    day = dt.date.fromisoformat(args.date) if args.date else now.astimezone(CT).date()
    section = Path(args.section) if args.section else SECTION

    letter = due(day, section)
    if letter is None:
        print(f"digest-release: no letter dated {day} in {section}; nothing to release")
        return 0
    path, when, fields = letter

    stamped = when.astimezone(CT)
    if (stamped.hour, stamped.minute) != (LIFT.hour, LIFT.minute):
        print(f"digest-release: note: {path.name} is stamped "
              f"{stamped.strftime('%H:%M')} CT but the embargo lifts at "
              f"{LIFT.strftime('%H:%M')} and the send is at 06:00; a later stamp "
              f"leaves the page no time to land first")

    if when > now:
        print(f"digest-release: {path.name} is dated {when.isoformat()}, which is after "
              f"the clock ({now.isoformat()}); nothing to release")
        return 0

    url = url_for(path)
    if served(url):
        print(f"digest-release: {url} already answers 200; nothing to release")
        return 0

    if args.dry_run:
        print(f"digest-release: would dispatch hugo.yml on {args.branch} for {path.name}, "
              f"then verify {url}")
        return 0

    code, detail = dispatch(args.branch)
    if code != 0:
        print(f"digest-release: dispatching the deploy failed (exit {code}): {detail}")
        return 1
    print(f"digest-release: dispatched hugo.yml on {args.branch}; verifying {url}")

    rc = verify(path)
    if rc != 0:
        print(f"digest-release: {url} did not answer with {fields.get('title', path.stem)!r}")
        return 1
    print(f"digest-release: released {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
