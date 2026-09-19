#!/usr/bin/env python3
"""Watch the Beatty v. Trump docket and report anything new.

Philip, 2026-09-19: "I must keep an eye on this story."

The Kennedy Center litigation (No. 1:25-cv-04480 (CRC), D.D.C.) moves in
day-scale bursts, and the coverage of it is unreliable — outlets routinely
conflate the two-year renovation closure with the seven-day safety closure, and
several have overstated what Judge Cooper's minute order actually froze. What
can be trusted is the docket. So watch the docket.

This reads the CourtListener Atom feed for the case, compares the highest ECF
entry number against a stored watermark, and reports new filings. The feed is
the right primitive: it is structured, it carries entry numbers, and it needs no
HTML scraping that would break when the site is restyled.

Exit codes:
  0 — no new filings (the common case; a no-op)
  0 — new filings found AND the report was delivered
  2 — could not read the feed (network, or CourtListener changed shape)
  3 — new filings found but delivery failed

A non-zero exit routes to scripts/alert-failure.sh via the runner, so a silent
failure to reach the docket does not look like "nothing happened" — which is the
failure mode that matters for a watch job.

Usage:
  check-docket.py                 # watch, update watermark, report
  check-docket.py --dry-run       # report what WOULD change; touch nothing
  check-docket.py --no-update     # report but do not move the watermark
  check-docket.py --quiet         # only report on change
  check-docket.py --status        # print current watermark and newest entry
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STATE = REPO / "scripts" / "docket-watch-state.json"

DOCKET_ID = "72069932"
CASE = "BEATTY v. TRUMP, 1:25-cv-04480"
FEED = f"https://www.courtlistener.com/docket/{DOCKET_ID}/feed/"
DOCKET_URL = f"https://www.courtlistener.com/docket/{DOCKET_ID}/beatty-v-trump/"

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) huffmanwrites-docket-watch"

# One-line summaries of what each recent entry was, so a report says what
# changed rather than just "entry 90 appeared". Kept short on purpose: this is a
# pointer to go read the document, not a substitute for reading it.
KNOWN: "dict[int, str]" = {
    48: "Preliminary injunction — bars effectuating the Mar 16 closure decision until the Board approves a conforming closure AND the court dissolves/modifies. STILL IN FORCE.",
    49: "Permanent injunction — the renaming is void; no signage on the building or grounds naming anyone but JFK. STILL IN FORCE.",
    50: "Memorandum opinion, Beatty v. Trump, 834 F. Supp. 3d 41 (D.D.C. 2026).",
    77: "Memo opinion & order — enjoins the renovation inscription and the Trump Plaza renaming; denies the $100M endowment plaque as unripe (60-day notice instead).",
    78: "Notice of board closure vote + Trump Truth Social statement.",
    79: "Notice of appeal -> D.C. Cir. No. 26-5322.",
    82: "Scheduling order (the Oct 16 / 23 / 27 briefing dates).",
    84: "Beatty emergency motion (staffer barred at 10:12 a.m.).",
    85: "Notice of supplemental authority (Trump 'ripped down' quote; Air Force One placard photo).",
    86: "DOJ response ('seven days, unless extended').",
    87: "Beatty reply (pretext).",
    88: "Motion to dissolve the PI (Rule 60(b)(5)) + 50-page memo.",
    89: "Renewed motion for partial summary judgment (+ Sep 18 Floca declaration, Delta Consulting report, Sep 15 board exhibits).",
}

# Dates that force a fresh look regardless of whether anything is filed. The
# docket and the case calendar are different instruments and both matter.
CALENDAR: "list[tuple[str, str]]" = [
    ("2026-09-23", "STATUS REPORT + sworn declaration due (Sept 17 minute order); discovery requests and deposition notices due; the 'seven-day' closure window expires."),
    ("2026-09-26", "NSO's first concert of its exile season (six DMV venues)."),
    ("2026-09-30", "Discovery responses due."),
    ("2026-10-08", "Board's own prior deferral date for returning the name to the façade."),
    ("2026-10-09", "Discovery closes."),
    ("2026-10-16", "Plaintiff opposition + cross-motion for summary judgment due."),
    ("2026-10-23", "Defendants' reply due."),
    ("2026-10-27", "Plaintiff's reply due."),
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_feed() -> str:
    # --compressed: see scripts/check-quotes.py. A gzip-forcing host would make
    # this read mojibake, the "<entry" test below would fail, and a live docket
    # would be reported as unreadable — the false-negative that makes a watch
    # job useless.
    r = subprocess.run(
        ["curl", "-sL", "--compressed", "--max-time", "30", "-A", USER_AGENT, FEED],
        capture_output=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"curl exit {r.returncode}")
    body = r.stdout.decode("utf-8", "replace")
    if "<entry" not in body:
        raise RuntimeError("feed contained no <entry> elements — shape changed?")
    return body


def parse_entries(xml: str) -> "list[dict]":
    """Return [{num, title, date, summary}] newest-last."""
    out = []
    for block in re.findall(r"<entry>(.*?)</entry>", xml, re.S):
        m = re.search(r"Entry #(\d+)", block)
        if not m:
            continue
        num = int(m.group(1))
        date_m = re.search(r"<published>([^<]+)</published>", block)
        summ_m = re.search(r"<summary[^>]*>(.*?)</summary>", block, re.S)
        summary = summ_m.group(1) if summ_m else ""
        # Trim the defendant list off the front: it is the same 45 names every
        # time and drowns the actual description.
        summary = re.sub(r"\s+", " ", summary).strip()
        summary = re.sub(
            r"^(?:MOTION|ORDER|NOTICE|RESPONSE|REPLY|MEMORANDUM|DECLARATION)[^.]{0,80}?\bby\s+"
            r"(?:[A-Z][A-Z.\s,'-]+,\s*){4,}",
            lambda mm: mm.group(0).split(" by ")[0] + " by [45 defendants] ",
            summary,
        )
        out.append({"num": num, "date": (date_m.group(1) if date_m else "")[:10],
                    "summary": summary[:400]})
    out.sort(key=lambda e: e["num"])
    return out


def load_state() -> dict:
    if STATE.is_file():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_state(s: dict) -> None:
    STATE.write_text(json.dumps(s, indent=2) + "\n", encoding="utf-8")


def due_calendar(today: str, horizon_days: int = 3) -> "list[tuple[str, str]]":
    """Calendar items due within the horizon, or already past but unreported."""
    out = []
    t0 = datetime.strptime(today, "%Y-%m-%d")
    for date, what in CALENDAR:
        d = datetime.strptime(date, "%Y-%m-%d")
        delta = (d - t0).days
        if 0 <= delta <= horizon_days:
            tag = "TODAY" if delta == 0 else f"in {delta}d"
            out.append((f"{date} ({tag})", what))
    return out


def deliver(title: str, body: str, quiet: bool) -> bool:
    """Two channels, matching alert-failure.sh: durable log + notification."""
    log = Path.home() / "Library" / "Logs" / "huffmanwrites-docket.log"
    try:
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a", encoding="utf-8") as f:
            f.write(f"\n=== {_now()} ===\n{title}\n{body}\n")
    except Exception:
        pass
    if quiet:
        return True
    r = subprocess.run(
        ["/usr/bin/osascript",
         "-e", "on run argv",
         "-e", 'display notification (item 1 of argv) with title "Kennedy Center docket" '
               'subtitle (item 2 of argv) sound name "Glass"',
         "-e", "end run",
         body[:300], title],
        capture_output=True,
    )
    return r.returncode == 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Watch the Beatty v. Trump docket.")
    ap.add_argument("--dry-run", action="store_true", help="report but change nothing")
    ap.add_argument("--no-update", action="store_true", help="report, keep watermark")
    ap.add_argument("--quiet", action="store_true", help="only report on change")
    ap.add_argument("--status", action="store_true", help="show watermark and newest entry")
    args = ap.parse_args()

    state = load_state()
    watermark = int(state.get("last_entry", 0))
    first_run = "last_entry" not in state

    try:
        entries = parse_entries(fetch_feed())
    except Exception as exc:
        print(f"docket-watch: ERROR: could not read feed: {exc}", file=sys.stderr)
        return 2

    if not entries:
        print("docket-watch: ERROR: feed parsed to zero entries", file=sys.stderr)
        return 2

    newest = entries[-1]["num"]

    if args.status:
        print(f"docket-watch: {CASE}")
        print(f"  watermark : {watermark or '(unset)'}")
        print(f"  newest    : {newest}")
        print(f"  feed      : {FEED}")
        print(f"  docket    : {DOCKET_URL}")
        return 0

    today = datetime.now().strftime("%Y-%m-%d")
    cal = due_calendar(today)

    # First run: record the watermark, do not alert on the entire history.
    if first_run:
        if not args.dry_run:
            state["last_entry"] = newest
            state["updated"] = _now()
            state["case"] = CASE
            save_state(state)
        print(f"docket-watch: first run — watermark set to {newest}; "
              f"{len(cal)} calendar item(s) within 3 days")
        for when, what in cal:
            print(f"  {when}: {what}")
        return 0

    new = [e for e in entries if e["num"] > watermark]

    if not new and not cal:
        if not args.quiet:
            print(f"docket-watch: no new filings (watermark {watermark}, newest {newest})")
        return 0

    lines = []
    if new:
        lines.append(f"{len(new)} new filing(s) since ECF {watermark}:")
        for e in new:
            note = KNOWN.get(e["num"], "")
            line = f"  ECF {e['num']} ({e['date']}): {note or e['summary'][:200]}"
            lines.append(line)
    if cal:
        lines.append("Calendar due:")
        for when, what in cal:
            lines.append(f"  {when}: {what}")
    body = "\n".join(lines)

    title = (f"ECF {new[-1]['num']}: {KNOWN.get(new[-1]['num'], new[-1]['summary'][:80])[:80]}"
             if new else "Kennedy Center: deadline approaching")

    print(f"docket-watch: {'CHANGE' if new else 'DEADLINE'}\n{body}")

    if args.dry_run:
        print("\ndocket-watch: --dry-run, watermark unchanged")
        return 0

    ok = deliver(title, body, args.quiet)
    if not ok:
        print("docket-watch: ERROR: delivery failed", file=sys.stderr)
        return 3

    if not args.no_update:
        state["last_entry"] = newest
        state["updated"] = _now()
        state["case"] = CASE
        save_state(state)

    return 0


if __name__ == "__main__":
    sys.exit(main())
