#!/usr/bin/env python3
"""Append the day's fetched facts to the ground-stop source pack.

Why this exists. `future-pieces/faa-ground-stop-source-notes.md` is the record
behind a piece on the nationwide ground stop of 13NOV26. Two kinds of fact in
it rot on a clock:

  * the FAA advisory index keeps **15 days** and then drops the page, so the
    primary documents die around 29NOV26, before the piece can be published;
  * FlightAware's daily totals settle within 24 hours and never change again,
    so an intraday snapshot reads wrong forever once the day closes.

A daily pass that reads both and writes down what it read keeps the record
current and leaves a snapshot URL for every advisory before the index drops it.

**It writes FACTS ONLY.** Numbers with the page they came from, advisory rows
as the index prints them, and capture timestamps. No analysis, no cause, no
model. The prose delta is written by a human or an agent reading this log, and
`future-pieces/faa-ground-stop-source-notes.md` §18 is the shape that takes.

Idempotent: a block for a date is replaced, not appended twice. A source that
fails is named as unavailable; the run stops only when nothing at all was
collected, because a pack entry that says "unavailable" is honest and a run
that writes an empty block is not.

Usage:
    python3 scripts/faa-ground-stop-pack.py                 # today, append
    python3 scripts/faa-ground-stop-pack.py --dry-run       # print, write nothing
    python3 scripts/faa-ground-stop-pack.py --date 2026-11-14
    python3 scripts/faa-ground-stop-pack.py --offline --dry-run   # no network
"""

from __future__ import annotations

import argparse
import datetime as dt
import html as html_mod
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

REPO = pathlib.Path(__file__).resolve().parent.parent
PACK = REPO / "future-pieces" / "faa-ground-stop-source-notes.md"
LOG_HEADING = "## 19. Daily collection log"
CT = dt.timezone(dt.timedelta(hours=-6), "CT")

ADV_URL = (
    "https://www.fly.faa.gov/adv/adv_list"
    "?whichAdvisories=ATCSCC&advisoryCategory=All&date={date}"
    "&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true"
)
ADV_PAGE = "https://www.fly.faa.gov/adv/adv_otherdis?adv_date={mdY}&advn={n}"
FLIGHTAWARE = "https://www.flightaware.com/live/cancelled/{which}"
WAYBACK = "http://archive.org/wayback/available?url={url}"

# The event's own documents. Checked every pass so the capture recorded is the
# newest one, not the one this pack closed with on 14NOV26.
ARCHIVE_WATCH = [
    ("11132026", 111), ("11132026", 119), ("11132026", 120),
    ("11142026", 1), ("11142026", 5), ("11142026", 18),
]
ARCHIVE_CAP = 24

UA = "huffmanwrites-ground-stop-pack/1.0 (+https://www.huffmanwrites.org)"

ROW = re.compile(
    r'<tr>\s*<td>\s*<a\s+href="/adv/adv_otherdis\?adv_date=(\d{8})&advn=(\d+)"'
    r'\s*>\s*(\d+)\s*</a>\s*</td>(.*?)</tr>',
    re.S,
)
CELL = re.compile(r"<td>(.*?)</td>", re.S)
TAG = re.compile(r"<[^>]+>")
TOTALS = re.compile(
    r"Total (cancellations|delays)"
    r"( within, into, or out of the United States)?"
    r" (yesterday|today|[A-Z][a-z]+day):\s*([0-9,]+)"
)


def fetch(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, "replace")


def clean(fragment: str) -> str:
    text = re.sub(r"<br\s*/?>", " / ", fragment, flags=re.I)
    text = TAG.sub(" ", text)
    text = html_mod.unescape(text).replace("\xa0", " ")
    return " ".join(text.split())


def parse_advisories(page: str) -> "list[dict]":
    """Rows of the ATCSCC index, as printed. Never summarised, never inferred."""
    rows = []
    for mdY, n, num, rest in ROW.findall(page):
        cells = [clean(c) for c in CELL.findall(rest)]
        cells = [c for c in cells if c]
        rows.append({
            "adv_date": mdY,
            "n": int(n),
            "num": num,
            "control": cells[0] if len(cells) > 0 else "",
            "title": cells[2] if len(cells) > 2 else (cells[-2] if cells else ""),
            "sent": cells[-1] if cells else "",
        })
    return rows


def parse_totals(page: str) -> "dict[str, dict[str, str]]":
    """FlightAware's own four lines, keyed by metric and scope."""
    text = " ".join(clean(page).split())
    out: "dict[str, dict[str, str]]" = {}
    for metric, us, _day, value in TOTALS.findall(text):
        scope = "us" if us else "all"
        out.setdefault(metric, {})[scope] = value
    return out


def wayback_capture(url: str) -> "dict[str, str] | None":
    import json
    raw = fetch(WAYBACK.format(url=urllib.parse.quote(url, safe="")), timeout=20)
    data = json.loads(raw)
    closest = (data.get("archived_snapshots") or {}).get("closest") or {}
    if not closest.get("available"):
        return None
    return {"url": closest.get("url", ""), "timestamp": closest.get("timestamp", "")}


def mdY(date: dt.date) -> str:
    return date.strftime("%m%d%Y")


def label(date: dt.date) -> str:
    return date.strftime("%d%b%y").upper()


def long_label(date: dt.date) -> str:
    return f"{date.strftime('%a')} {label(date)}"


def _table(header: "list[str]", rows: "list[list[str]]") -> "list[str]":
    out = ["| " + " | ".join(header) + " |",
           "|" + "|".join("---" for _ in header) + "|"]
    for row in rows:
        out.append("| " + " | ".join(c.replace("|", "\\|") for c in row) + " |")
    return out


def collect(day: dt.date, offline: bool = False) -> "tuple[str, bool]":
    """Render the block for `day` and say whether anything was collected."""
    now = dt.datetime.now(CT)
    lines = [f"### {label(day)}", ""]
    lines.append(
        f"**Collected** {now.strftime('%d%b%y %H:%M').upper()} CT by "
        "`scripts/faa-ground-stop-pack.py`. Facts only: every line below was read "
        "off the page named, and nothing here is analysis."
    )
    lines.append("")
    any_ok = False
    all_rows: "list[dict]" = []

    if offline:
        lines += ["**Offline pass.** No source was read.", ""]
        return "\n".join(lines), False

    for adv_day in (day, day + dt.timedelta(days=1)):
        url = ADV_URL.format(date=adv_day.isoformat())
        try:
            rows = parse_advisories(fetch(url))
        except Exception as exc:  # noqa: BLE001 - reported, never swallowed
            lines += [f"**Advisories, {adv_day.isoformat()}** — SOURCE UNAVAILABLE "
                      f"({type(exc).__name__}: {exc}). `{url}`", ""]
            continue
        any_ok = True
        if not rows:
            lines += [f"**Advisories, {adv_day.isoformat()}** — the index returned "
                      f"no rows, fetched {now.strftime('%H:%M')} CT. `{url}`", ""]
            continue
        all_rows.extend(rows)
        lines += [f"**Advisories on the index, {adv_day.isoformat()}** — "
                  f"{len(rows)} rows, fetched {now.strftime('%H:%M')} CT. `{url}`", ""]
        lines += _table(
            ["No.", "Control", "Sent", "Title"],
            [[r["num"], r["control"], r["sent"], r["title"]] for r in rows],
        )
        stops = [r for r in rows if "GROUND STOP" in r["title"].upper()]
        if stops:
            lines += ["", "Ground-stop rows above, by number: "
                      + ", ".join(r["num"] for r in stops) + "."]
        else:
            lines += ["", "No row on this day's index is a ground-stop advisory."]
        lines.append("")

    # FlightAware: two days back, yesterday, today.
    totals_rows = []
    for offset, which in ((2, "minus2days"), (1, "yesterday"), (0, "today")):
        target = now.date() - dt.timedelta(days=offset)
        url = FLIGHTAWARE.format(which=which)
        try:
            totals = parse_totals(fetch(url))
        except Exception as exc:  # noqa: BLE001
            lines += [f"**FlightAware, {which}** — SOURCE UNAVAILABLE "
                      f"({type(exc).__name__}: {exc}). `{url}`", ""]
            continue
        any_ok = True
        canc = totals.get("cancellations", {})
        dels = totals.get("delays", {})
        totals_rows.append([
            long_label(target),
            canc.get("us", "—"),
            dels.get("us", "—"),
            canc.get("all", "—"),
            dels.get("all", "—"),
        ])
    if totals_rows:
        lines += [
            f"**FlightAware totals** — fetched {now.strftime('%H:%M')} CT. The date "
            "column is this pass's CT date for that page; the tracker words its own "
            "pages by weekday.",
            "",
        ]
        lines += _table(
            ["Day", "Cancels (US)", "Delays (US)", "Cancels (all)", "Delays (all)"],
            totals_rows,
        )
        lines.append("")

    # Snapshots, so an advisory can still be cited after the 15-day window.
    # Only documents that can carry the event: the six on the watch list, plus
    # any rows whose own title is a ground stop or an operations plan. The
    # index also prints volcanic-activity bulletins and FCA notices, and
    # checking those would spend a request each to learn nothing.
    watch = list(ARCHIVE_WATCH)
    for row in all_rows:
        key = (row["adv_date"], int(row["n"]))
        title = row["title"].upper()
        if key not in watch and ("GROUND STOP" in title or "OPERATIONS PLAN" in title):
            watch.append(key)
    caps = []
    for mdY_, n_ in watch[:ARCHIVE_CAP]:
        page = ADV_PAGE.format(mdY=mdY_, n=n_)
        try:
            cap = wayback_capture(page)
        except Exception as exc:  # noqa: BLE001
            caps.append([f"{mdY_}/{n_}", f"unavailable ({type(exc).__name__})", ""])
            continue
        any_ok = True
        caps.append([
            f"{mdY_}/{n_}",
            cap["timestamp"] if cap else "no capture",
            cap["url"] if cap else "",
        ])
    if caps:
        lines += ["**Wayback captures** — nearest snapshot the availability API "
                  "returned for each advisory, fetched "
                  f"{now.strftime('%H:%M')} CT. The advisory index keeps 15 days; "
                  "a row reading `no capture` is a document no archive holds yet.",
                  ""]
        lines += _table(["Advisory", "Captured (UTC)", "Snapshot"], caps)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n", any_ok


def upsert(text: str, day_label: str, block: str) -> str:
    """Replace this date's block if it exists; otherwise append it under the log."""
    if LOG_HEADING not in text:
        text = text.rstrip() + "\n\n---\n\n" + LOG_HEADING + "\n"
    head, _, log = text.partition(LOG_HEADING)
    marker = f"### {day_label}"
    # The block ends at the next date heading OR at a hand-written reading,
    # so a re-run replaces the machine-written part and leaves the prose. A
    # reading that a daily pass silently deleted would be the worst failure
    # this job could have: the record would look current and be shorter.
    pattern = re.compile(
        r"^" + re.escape(marker) + r"\s*$.*?(?=^### |^\*\*Reading — |\Z)", re.S | re.M
    )
    if pattern.search(log):
        log = pattern.sub(block.rstrip() + "\n\n", log, count=1)
    else:
        log = log.rstrip() + "\n\n" + block.rstrip() + "\n"
    return head + LOG_HEADING + log.rstrip() + "\n"


def main(argv: "list[str]") -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--date", help="CT date to collect (YYYY-MM-DD); default today")
    ap.add_argument("--pack", default=str(PACK))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args(argv)

    day = (dt.date.fromisoformat(args.date) if args.date
           else dt.datetime.now(CT).date())
    pack = pathlib.Path(args.pack)

    block, any_ok = collect(day, offline=args.offline)
    if not any_ok:
        print(f"faa-ground-stop-pack: nothing collected for {day}; no block written.")
        return 3
    if args.dry_run:
        print(block)
        return 0

    text = pack.read_text(encoding="utf-8") if pack.exists() else ""
    pack.write_text(upsert(text, label(day), block), encoding="utf-8")
    print(f"faa-ground-stop-pack: {label(day)} written to {pack}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
