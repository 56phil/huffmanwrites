#!/usr/bin/env python3
"""Watch for a missing SITREP edition — the one failure nothing else can see.

The daily SITREP is the only job here that publishes every day, and only a
FAILING run alerts. A run that never happens is invisible: launchd writes
nothing, the shared alert is never called, and the section simply has no edition
for the day. That is reachable more ways than it looks, and each one is real:

  * the machine is off at 06:00 — launchd does not run a missed calendar event
    at boot, and StartCalendarInterval has no catch-up;
  * the plist is uninstalled, renamed, or left unparseable by an edit;
  * the runner dies before its first log line (no Ollama, no network, a full
    disk) so not even the `alert-failure.sh` calls are reached;
  * the push lands but the Pages deploy does not, so `origin/main` carries the
    edition and the site does not.

Philip asked for this watchdog on 2026-10-08, the day after the first edition
shipped, when that gap was stated plainly.

WHY TWO CHECKS, and why the pair rather than either half. The local file answers
"did the writer run"; the deployed page answers "can a reader see it". Together
they separate the two failures, which need different fixes: no file anywhere
means the run never happened, and a file with a 404 page means the push or the
deploy did not land. A single check cannot tell those apart and would report the
same sentence for both.

WHY `sitrep-watchdog.py` and not `check-sitrep-edition.py`. The `check-*.py`
namespace in this repo means a gate over the corpus that CI or a publishing tail
must run, and `test_gates.py` asserts every one of them is wired somewhere. This
is a job's own instrument, like `sitrep-pack.py` and `chiefs-report.py`, and it
runs from its own launchd job.

Exit codes: 0 present, or not due yet; 1 missing; 3 could not be verified.
Non-zero routes to `scripts/alert-failure.sh` through `sitrep-watchdog-runner.sh`.
One alert per day per kind: the first check that finds a problem raises it, and
later checks the same day log that they did and exit 0, so a machine that was off
all morning does not produce four banners for the same missing edition.

Usage:
    python3 scripts/sitrep-watchdog.py                      # today, CT
    python3 scripts/sitrep-watchdog.py --date 2026-10-09    # a specific date
    python3 scripts/sitrep-watchdog.py --deadline 08:30     # later deadline
    python3 scripts/sitrep-watchdog.py --date 2026-10-09 --no-state --no-fetch
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parent.parent
SECTION = REPO / "content" / "posts" / "sitrep"
STATE_FILE = Path.home() / "Library" / "Logs" / "sitrep-watchdog-state.json"

# The canonical host: hugo.toml's baseURL and static/CNAME. Not www — the site
# answers there too, but a URL this repo writes names huffmanwrites.org.
SITE = "https://huffmanwrites.org"

# The first edition, published by hand during installation at 19:45 on
# 2026-10-07. Before this date the absence of an edition is not a finding.
SERIES_START = date(2026, 10, 7)

# The edition is due by 07:00 CT. The run starts at 06:00 and finished at
# 06:05:58 on its first unattended morning, so this is roughly an hour of slack
# for a slow pack plus the deploy.
DEADLINE = time(7, 0)

# Every SITREP slug is a CT date (`sitrep-2026-10-08.md`), because both the run
# and the frontmatter are CT. The machine's own zone is CT today, but a check
# that silently follows the machine's clock is a check that reports the wrong day
# after a move, so the zone is named.
TZ = ZoneInfo("America/Chicago")

UA = "huffmanwrites-sitrep-watchdog/1.0 (+https://huffmanwrites.org)"
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)


@dataclass
class Page:
    """What the deployed page turned out to be.

    `checked` is separate from `status` on purpose: "we asked and the request
    failed" and "we never asked" produce different sentences, and the second one
    only happens when `--no-fetch` asks for it.
    """

    status: int | None = None
    error: str = ""
    title: str | None = None
    body: str = ""
    checked: bool = False

    def serves(self, text: str) -> bool:
        """Does this page serve the edition, by its own <title>?

        The title is what `check-links.py --titles` compares for the same
        reason: a 200 is not evidence that the page is the one asked for. When
        there is no <title> to read, the body is the fallback rather than a
        verdict of OK.
        """
        if self.status != 200:
            return False
        haystack = self.title if self.title is not None else self.body
        return text in (haystack or "")


@dataclass
class Verdict:
    status: str  # present | not-due | missing | unverified
    kind: str  # "" when there is nothing to alert; otherwise the dedup key
    line: str
    exit_code: int


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def edition_path(day: date) -> Path:
    return SECTION / f"sitrep-{day.isoformat()}.md"


def edition_url(day: date) -> str:
    return f"{SITE}/posts/sitrep/sitrep-{day.isoformat()}/"


def decide(
    day: date,
    now: datetime,
    local_exists: bool,
    page: Page,
    deadline: time = DEADLINE,
    series_start: date = SERIES_START,
) -> Verdict:
    """The whole policy, in one place and with no I/O.

    `decide` is pure so the rules can be tested directly rather than through a
    live site: the cases that matter (a file with a 404 page, a page that
    answers but is not this edition, a check before the deadline) are all hard
    to stage against the real one.
    """
    expected = f"{day:%B} {day.day}, {day.year}"  # "October 9, 2026"
    url = edition_url(day)
    path = rel(edition_path(day))

    if day < series_start:
        return Verdict(
            "not-due", "",
            f"{day} is before the first edition ({series_start}); nothing to watch",
            0,
        )

    # A check before the deadline is asking about an edition that may not be due
    # yet — this is what makes `RunAtLoad` safe, so a login at 05:00 cannot raise
    # a banner about a report whose writer has not started. But the deadline
    # excuses an ABSENCE, never a presence: an edition already in place is
    # reported as published however early it is read, which is why a check at
    # 06:30 (an hour into a run that finished at 06:06) reports the edition
    # rather than the clock.
    already_in_place = local_exists and (page.serves(expected) or not page.checked)
    if day == now.date() and now.time() < deadline and not already_in_place:
        return Verdict(
            "not-due", "",
            f"{day} is not due until {deadline:%H:%M} CT and it is {now:%H:%M} CT; "
            "nothing to check",
            0,
        )

    if local_exists and page.serves(expected):
        return Verdict("present", "", f"{day} is published: {path} and {url}", 0)

    # `--no-fetch`: the local half is the whole answer, and it is decisive about
    # whether the run happened. Said out loud so nobody reads a pass as a
    # confirmed deploy.
    if not page.checked:
        if local_exists:
            return Verdict(
                "present", "",
                f"edition for {day} is in the repo at {path}; the deployed page "
                "was not checked (--no-fetch)",
                0,
            )
        return Verdict(
            "missing", "missing",
            f"no edition for {day}: {path} is missing; the deployed page was not "
            "checked (--no-fetch)",
            1,
        )

    if not local_exists:
        if page.serves(expected):
            # The page serves today's edition and the file is gone locally.
            # Rare, and not a missing edition: the reader can read it.
            return Verdict(
                "present", "",
                f"{day} is live at {url}, though {path} is absent from the "
                "working tree",
                0,
            )
        if page.status == 404:
            return Verdict(
                "missing", "missing",
                f"no edition for {day}: neither {path} nor {url} exists, so the "
                "run never happened (or never got as far as a file)",
                1,
            )
        if page.status is not None:
            return Verdict(
                "unverified", "unverified",
                f"no edition for {day}: {path} is absent and {url} returned "
                f"HTTP {page.status} rather than the edition",
                3,
            )
        return Verdict(
            "missing", "missing",
            f"no edition for {day}: {path} is missing, and the site could not be "
            f"read to confirm ({page.error or 'no response'})",
            1,
        )

    # The file is there. Either the deploy landed or it did not, and that
    # distinction is the whole reason the page is fetched at all.
    if page.status == 404:
        return Verdict(
            "missing", "missing",
            f"no edition for {day} on the site: {path} is in the repo but {url} "
            "is 404 — the push or the deploy did not land",
            1,
        )
    if page.status == 200:
        return Verdict(
            "unverified", "unverified",
            f"{path} exists, but {url} serves a page whose own title is not "
            f"'{expected}' — the wrong page is at that address",
            3,
        )
    return Verdict(
        "unverified", "unverified",
        f"{path} exists, but {url} could not be read "
        f"({page.error or 'no response'}); the deploy is unconfirmed",
        3,
    )


def fetch(url: str, timeout: int = 20) -> Page:
    """Fetch the page. A failure is a Page with an error and no status.

    The User-Agent is sent because GitHub Pages serves a bot-ish client
    normally, unlike the ESPN endpoints CLAUDE.md records, which answer a
    browser and refuse a default client. Nothing here needs that treatment.
    """
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", "replace")
            m = TITLE_RE.search(body)
            return Page(
                status=resp.status,
                title=(re.sub(r"\s+", " ", m.group(1)).strip() if m else None),
                body=body,
                checked=True,
            )
    except urllib.error.HTTPError as exc:
        return Page(status=exc.code, error=f"HTTP {exc.code}", checked=True)
    except Exception as exc:  # noqa: BLE001 - any transport failure is "unverified"
        return Page(status=None, error=f"{exc.__class__.__name__}: {exc}", checked=True)


# ---------------------------------------------------------------------------
# Alert dedup state. Machine-local, in ~/Library/Logs, and deliberately NOT in
# the repo: the publishing tail commits the working tree (`git add -A`), so a
# state file written inside the checkout would be swept into whichever job
# publishes next, under that job's commit message. `docket-watch-state.json`
# lives in scripts/ because the docket watcher compares filings across runs and
# its state is worth versioning; a "last alerted date" is not.
# ---------------------------------------------------------------------------
def load_state(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:  # noqa: BLE001 - a missing or corrupt state file is not a failure
        return {}


def save_state(path: Path, day: date, alerted: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"date": day.isoformat(), "alerted": alerted}, indent=1) + "\n",
            encoding="utf-8",
        )
    except Exception as exc:  # noqa: BLE001 - never turn a bookkeeping failure into an alert
        print(f"sitrep-watchdog: could not write {path}: {exc}", file=sys.stderr)


def parse_deadline(text: str) -> time:
    try:
        hh, mm = text.split(":")
        return time(int(hh), int(mm))
    except Exception:  # noqa: BLE001
        raise SystemExit(f"sitrep-watchdog: --deadline wants HH:MM, got {text!r}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Watch for a missing SITREP edition for a given day (CT)."
    )
    ap.add_argument("--date", help="watch this date (YYYY-MM-DD) instead of today")
    ap.add_argument("--deadline", default=f"{DEADLINE:%H:%M}",
                    help="CT time the edition is due (default 07:00)")
    ap.add_argument("--state", help=f"alert-dedup state file (default {STATE_FILE})")
    ap.add_argument("--no-state", action="store_true",
                    help="do not read or write the dedup state (always alert)")
    ap.add_argument("--no-fetch", action="store_true",
                    help="check the local file only; do not fetch the deployed page")
    args = ap.parse_args()

    now = datetime.now(TZ)
    try:
        day = date.fromisoformat(args.date) if args.date else now.date()
    except ValueError:
        raise SystemExit(f"sitrep-watchdog: --date wants YYYY-MM-DD, got {args.date!r}")
    deadline = parse_deadline(args.deadline)

    local = edition_path(day).exists()
    # Skip the fetch when the deadline has not arrived: the verdict is decided
    # by the clock, and a request at 05:00 answers a question nobody asked.
    pre = decide(day, now, local, Page(), deadline=deadline)
    page = Page() if pre.status == "not-due" or args.no_fetch else fetch(edition_url(day))

    verdict = decide(day, now, local, page, deadline=deadline)
    print(f"sitrep-watchdog: {verdict.line}")

    state_path = Path(args.state) if args.state else STATE_FILE
    state = {} if args.no_state else load_state(state_path)
    alerted = dict(state.get("alerted") or {}) if state.get("date") == day.isoformat() else {}

    if verdict.kind:
        if verdict.kind in alerted:
            print(
                f"sitrep-watchdog: {verdict.kind} for {day} was already alerted at "
                f"{alerted[verdict.kind]}; not alerting again"
            )
            return 0
        if not args.no_state:
            alerted[verdict.kind] = f"{now:%Y-%m-%d %H:%M:%S %Z}"
            save_state(state_path, day, alerted)
        return verdict.exit_code

    # A clean check for today resets the day's record, so a late edition that
    # arrives after an alert is not reported as a problem tomorrow.
    if not args.no_state and day == now.date() and state.get("date") == day.isoformat():
        save_state(state_path, day, {})
    return 0


if __name__ == "__main__":
    sys.exit(main())
