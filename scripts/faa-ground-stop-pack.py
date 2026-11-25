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

**It creates captures, not just records them (16NOV26).** `recorded, not
created` was the first version, on the belief that `web.archive.org/save/`
timed out at 45 s. Measured 16NOV26, a save answered in **18.4 s** and closed
the gap the pack had reported for two days, so the timeout was the constraint
rather than the service. The pass now asks, verifies, and — when nothing holds
the document — requests the save itself, within a per-pass budget.

**It verifies what it records.** The availability endpoint answers with the
*closest* capture and echoes the requested URL back, so a near-miss is
invisible: on 15NOV26 the pack recorded `11142026/18` as captured at
`20261114032528`, and that snapshot served **404** with nothing in the CDX
index a day later. A capture is recorded only after the snapshot body is
fetched and carries the wording it should; otherwise the verdict is
`no capture` or `unverified`, which are claims about the checker.

Idempotent: a block for a date is replaced, not appended twice. A source that
fails is named as unavailable; the run stops only when nothing at all was
collected, because a pack entry that says "unavailable" is honest and a run
that writes an empty block is not.

Exit codes:
    0   a block was written (or printed, with --dry-run)
    3   nothing at all was collected; no block written
    4   a page was read but a required figure did not parse out of it; the
        block is still written, and the runner alerts, because a selector that
        broke is invisible in every other way

Usage:
    python3 scripts/faa-ground-stop-pack.py                 # today, append
    python3 scripts/faa-ground-stop-pack.py --dry-run       # print, write nothing
    python3 scripts/faa-ground-stop-pack.py --date 2026-11-14
    python3 scripts/faa-ground-stop-pack.py --offline --dry-run   # no network
"""

from __future__ import annotations

import argparse
import concurrent.futures as futures
import dataclasses
import datetime as dt
import html as html_mod
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

REPO = pathlib.Path(__file__).resolve().parent.parent
PACK = REPO / "future-pieces" / "faa-ground-stop-source-notes.md"
LOG_HEADING = "## 19. Daily collection log"
LEDGER_HEADING = "## 20. Settled totals — every date read, merged and kept"
CITATIONS_HEADING = "## 21. Verified citations — generated; do not edit by hand"
CT = dt.timezone(dt.timedelta(hours=-6), "CT")

ADV_URL = (
    "https://www.fly.faa.gov/adv/adv_list"
    "?whichAdvisories=ATCSCC&advisoryCategory=All&date={date}"
    "&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true"
)
ADV_PAGE = "https://www.fly.faa.gov/adv/adv_otherdis?adv_date={mdY}&advn={n}"
FLIGHTAWARE = "https://www.flightaware.com/live/cancelled/{which}"
WAYBACK = "https://archive.org/wayback/available?url={url}"
SAVE = "https://web.archive.org/save/{url}"

# A document the FAA can edit or retire, quoted verbatim in §18.14 and on no
# other watch list. The needle is a phrase from its body, not its title.
QA_URL = (
    "https://www.faa.gov/newsroom/"
    "nationwide-ground-stop-questions-and-answers"
)
QA_NEEDLE = "connection attempts every 4 to 5 seconds"

# The event's own documents. Checked every pass so the capture recorded is the
# newest one, not the one this pack closed with on 14NOV26.
ARCHIVE_WATCH = [
    ("11132026", 111), ("11132026", 119), ("11132026", 120),
    ("11142026", 1), ("11142026", 5), ("11142026", 18),
]

# The day indexes nobody archived. The strongest primary source for "the
# airspace carried no restriction on the 15th" is that day's 27-row index
# page, and when the 15-day window closes it is the only thing that says so.
# The window runs from the stop to the last day of the Thanksgiving travel
# period, so the piece can prove each day of it separately; a date that has
# not happened yet is never requested, because the index for tomorrow is empty
# and capturing an empty page would be a false record.
INDEX_WINDOW = ("2026-11-13", "2026-11-30")

ARCHIVE_CAP = 30          # watch items checked per pass
DISCOVERY_CAP = 6         # index rows added per pass, so one busy day cannot fill the list
SAVE_BUDGET = 6           # save requests per pass for the documents that matter
SAVE_BUDGET_TAIL = 2      # ...and for a day's own airport advisories, which its index also holds
SAVE_TIMEOUT = 45         # a save answered in 18.4 s when measured; one hung for 100 s
SAVE_TIMEOUT_TAIL = 25    # a low-value save is not worth a long wait on somebody else's queue
VERIFY_TIMEOUT = 45
WORKERS = 6               # independent capture checks in flight at once
AUDIT_WORKERS = 3         # fewer, because the audit hammers one host and gets throttled

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
FIGROW = re.compile(
    r"^\|\s*((?:Mon|Tue|Wed|Thu|Fri|Sat|Sun) \d{2}[A-Z]{3}\d{2})\s*"
    r"\|([^|\n]*)\|([^|\n]*)\|([^|\n]*)\|([^|\n]*)\|",
    re.M,
)


@dataclasses.dataclass
class Pass:
    """One pass's block, and what the pass is able to claim about it."""

    block: str
    ok: bool                                          # anything at all was read
    problems: "list[str]" = dataclasses.field(default_factory=list)
    totals: "list[dict]" = dataclasses.field(default_factory=list)
    citations: "list[tuple]" = dataclasses.field(default_factory=list)

    def __bool__(self) -> bool:  # `if not collect(...)` keeps meaning "nothing read"
        return self.ok


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


WEEKDAYS = {
    name: index for index, name in enumerate(
        ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
         "Saturday", "Sunday"))
}


def parse_day_word(page: str) -> str:
    """The day the page names on its own lines — "Sunday", "yesterday", "today"."""
    text = " ".join(clean(page).split())
    match = TOTALS.search(text)
    return match.group(3) if match else ""


def tracker_day(now: "dt.datetime") -> dt.date:
    """FlightAware's own day, which is UTC and not Central.

    Its pages roll at 00:00Z, so between 18:00 CT and midnight the tracker is
    already on tomorrow. Labelling its "minus2days" page from the CT date put
    a whole day's totals under the wrong date on the 23:30 pass of 16NOV26:
    Sunday's 2,336 US cancellations were recorded against Saturday. The offset
    was the assumption; UTC is the measurement.
    """
    return now.astimezone(dt.timezone.utc).date()


def resolve_page_day(word: str, target: dt.date,
                     today: dt.date) -> "tuple[dt.date, str]":
    """The date a page is about, read from the page's own word.

    Returns the date and a problem string (empty when the word is usable).
    """
    text = (word or "").strip()
    if text.lower() == "today":
        return today, ""
    if text.lower() == "yesterday":
        return today - dt.timedelta(days=1), ""
    if text in WEEKDAYS:
        back = (today.weekday() - WEEKDAYS[text]) % 7
        return today - dt.timedelta(days=back), ""
    return target, (f"totals: a page names `{text or 'no day'}` instead of a day, "
                    "so its rows cannot be dated")


def wayback_capture(url: str) -> "dict[str, str] | None":
    """The *closest* capture the availability API offers — which may be a miss."""
    import json
    raw = fetch(WAYBACK.format(url=urllib.parse.quote(url, safe="")), timeout=20)
    data = json.loads(raw)
    closest = (data.get("archived_snapshots") or {}).get("closest") or {}
    if not closest.get("available"):
        return None
    return {"url": closest.get("url", ""), "timestamp": closest.get("timestamp", "")}


def verify_capture(snapshot_url: str, needles: "list[str]") -> "tuple[bool, str]":
    """Fetch the snapshot itself and require it to carry the document's wording.

    This is the half the availability API cannot do. It answers with the
    nearest capture of *some* URL and echoes the requested URL back, so a
    near-miss looks exactly like a hit until somebody opens it.
    """
    if not snapshot_url:
        return False, "no snapshot URL"
    try:
        body = fetch(snapshot_url, timeout=VERIFY_TIMEOUT)
    except Exception as exc:  # noqa: BLE001 - reported as the verdict
        return False, f"snapshot did not serve ({type(exc).__name__})"
    text = clean(body).lower()
    if not needles:
        # No wording to require: the question is only whether something was
        # archived and it is not a stub.
        return (True, "") if len(text) > 200 else (False, "snapshot is empty")
    for needle in needles:
        if needle.lower() in text:
            return True, ""
    return False, "snapshot does not carry the wording"


def save_capture(url: str, timeout: int = SAVE_TIMEOUT) -> "dict[str, str] | None":
    """Ask the Wayback Machine to archive the page now, and return the capture.

    The save endpoint answers with a redirect to the new snapshot, so the
    final URL carries its timestamp. Measured 16NOV26: 18.4 s for the advisory
    the pack had reported as uncapturable for two days.
    """
    req = urllib.request.Request(
        SAVE.format(url=urllib.parse.quote(url, safe=":/?&=%")),
        headers={"User-Agent": UA},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        final = resp.geturl()
    m = re.search(r"/web/(\d{14})/", final)
    if not m:
        return None
    return {"url": final, "timestamp": m.group(1)}


def index_needle(iso: str) -> str:
    return f"ATCSCC ADVISORIES FOR {iso}"


def index_days(day: dt.date) -> "list[str]":
    """Every day index from the stop to `day`, never past the window or today."""
    start = dt.date.fromisoformat(INDEX_WINDOW[0])
    end = min(dt.date.fromisoformat(INDEX_WINDOW[1]), day)
    out, cursor = [], start
    while cursor <= end:
        out.append(cursor.isoformat())
        cursor += dt.timedelta(days=1)
    return out


def needles_for(key: str) -> "list[str]":
    """The wording a snapshot of this document must carry to be that document."""
    m = re.match(r"^(\d{8})/(\d+)$", key)
    if m:
        n = int(m.group(2))
        return [f"advzy {n:03d}", f"advzy {n}"]
    if key == "faa-qa":
        return [QA_NEEDLE]
    if key.startswith("index "):
        return [index_needle(key[len("index "):])]
    return []


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
        out.append("| " + " | ".join(row) + " |")
    return out


def block_of(text: str, day_label: str) -> str:
    """This date's machine-written block, up to its hand-written reading."""
    if not text:
        return ""
    pattern = re.compile(
        r"^### " + re.escape(day_label) + r"\s*$.*?(?=^### |^\*\*Reading — |\Z)",
        re.S | re.M,
    )
    m = pattern.search(text)
    return m.group(0) if m else ""


def prior_state(text: str, day_label: str) -> "dict":
    """What the previous pass of this date recorded, so a move is visible.

    `upsert` replaces the day's block, which is right — the record should show
    the settled figure, not a mid-day one. But a figure that moved between
    passes then vanishes, and the file reads as though the number were always
    that. Sunday's US cancellations were 1,446 at 08:00 on 15NOV26 and 2,336
    the next morning; only the second is true, and only the pair shows that a
    tracker settles.
    """
    block = block_of(text, day_label)
    if not block:
        return {}
    when = ""
    hm = re.search(r"\*\*Collected\*\*\s+\S+\s+(\d{2}:\d{2})\s+CT", block)
    if hm:
        when = hm.group(1)
    figures = {}
    for day_mark, *cells in FIGROW.findall(block):
        figures[day_mark.strip()] = [c.strip().split(" (")[0] for c in cells]
    return {"time": when, "figures": figures}


def _moved(value: str, prior: "dict", day_mark: str, index: int) -> str:
    old = (prior.get("figures") or {}).get(day_mark) or []
    was = old[index] if len(old) > index else ""
    if not was or was in ("—", value):
        return value
    when = prior.get("time") or ""
    return f"{value} (was {was}{' at ' + when if when else ''})"


def watch_items(day: dt.date, all_rows: "list[dict]") -> "tuple[list[tuple[str, str, list[str]]], int]":
    """Every document worth a capture this pass: key, URL, wording to require.

    The order is the save budget's order. Measured on 16NOV26's first live
    pass: today's own local ground stops — eight of them, each a CDM advisory
    about one airport — came before the four day index pages, spent the whole
    budget, and left every index page `no capture`. A transient airport
    advisory is also on an index that is captured anyway; the index is the
    better artifact and is what has no other home.

    Returns the items and the index at which the low-value tail begins. The
    tail is checked and can borrow two saves, because a body that says why an
    airport stopped is worth having; it is not worth the whole budget, and on
    16NOV26 two hung saves there cost the pass two minutes.
    """
    items: "list[tuple[str, str, list[str]]]" = []
    seen = set()

    def add(key: str, url: str, needles: "list[str]") -> None:
        if url in seen:
            return
        seen.add(url)
        items.append((key, url, needles))

    # 1. The event's own documents.
    for mdY_, n_ in ARCHIVE_WATCH:
        key = f"{mdY_}/{n_}"
        add(key, ADV_PAGE.format(mdY=mdY_, n=n_), needles_for(key))

    # 2. A ground stop or operations plan on an event day, discovered from the
    #    index. Later days are captured by their own pass, when the advisory is
    #    hours old rather than an hour old.
    event_days = {mdY_ for mdY_, _ in ARCHIVE_WATCH}
    discovered = 0
    for row in sorted(all_rows, key=lambda r: r["adv_date"]):
        key = (row["adv_date"], int(row["n"]))
        if key in ARCHIVE_WATCH or row["adv_date"] not in event_days:
            continue
        if not _carries_event(row["title"]):
            continue
        discovered += 1
        if discovered <= DISCOVERY_CAP:
            key = f"{row['adv_date']}/{row['n']}"
            add(key, ADV_PAGE.format(mdY=row["adv_date"], n=row["n"]), needles_for(key))

    # 3. The day indexes themselves, one per day of the window that has
    #    happened. A day's page is the proof of what that day's airspace did
    #    or did not do, and the index drops it after fifteen days.
    for iso in index_days(day):
        add(f"index {iso}", ADV_URL.format(date=iso), [index_needle(iso)])

    # 4. A page the FAA can edit and every other watch list misses.
    add("faa-qa", QA_URL, [QA_NEEDLE])

    # 5. Everything else that can carry the event, last because it can wait a
    #    pass: an airport's ground stop is on its day's index too.
    tail_start = len(items)
    for row in all_rows:
        key = (row["adv_date"], int(row["n"]))
        if key in ARCHIVE_WATCH or row["adv_date"] in event_days:
            continue
        if _carries_event(row["title"]):
            key = f"{row['adv_date']}/{row['n']}"
            add(key, ADV_PAGE.format(mdY=row["adv_date"], n=row["n"]), needles_for(key))
    return items, tail_start


def _resolve(item: "tuple[str, str, list[str]]") -> "tuple":
    """Ask what holds this document, and check that the answer is the document.

    Runs in a thread pool: each item is an independent read, and one slow
    snapshot must not hold up the rest.
    """
    key, url, needles = item
    try:
        cap = wayback_capture(url)
    except Exception as exc:  # noqa: BLE001 - reported as the verdict
        return key, url, needles, None, f"availability unavailable ({type(exc).__name__})"
    if not cap:
        return key, url, needles, None, "no capture"
    ok, why = verify_capture(cap["url"], needles)
    if ok:
        return key, url, needles, cap, ""
    return key, url, needles, None, why


def _carries_event(title: str) -> bool:
    """Only documents that can carry the event. The index also prints
    volcanic-activity bulletins and FCA notices, and a request on those would
    spend a save to learn nothing."""
    upper = title.upper()
    return "GROUND STOP" in upper or "OPERATIONS PLAN" in upper


def collect(
    day: dt.date,
    offline: bool = False,
    prior: "dict | None" = None,
    now: "dt.datetime | None" = None,
) -> Pass:
    """Render the block for `day` and say what the pass can claim about it."""
    now = now or dt.datetime.now(CT)
    prior = prior or {}
    lines = [f"### {label(day)}", ""]
    lines.append(
        f"**Collected** {now.strftime('%d%b%y %H:%M').upper()} CT by "
        "`scripts/faa-ground-stop-pack.py`. Facts only: every line below was read "
        "off the page named, and nothing here is analysis."
    )
    lines.append("")
    if offline:
        lines += ["**Offline pass.** No source was read.", ""]
        return Pass("\n".join(lines), False, [])

    ok = False
    problems: "list[str]" = []
    all_rows: "list[dict]" = []
    tables = 0

    for adv_day in (day, day + dt.timedelta(days=1)):
        url = ADV_URL.format(date=adv_day.isoformat())
        try:
            rows = parse_advisories(fetch(url))
        except Exception as exc:  # noqa: BLE001 - reported, never swallowed
            lines += [f"**Advisories, {adv_day.isoformat()}** — SOURCE UNAVAILABLE "
                      f"({type(exc).__name__}: {exc}). `{url}`", ""]
            continue
        ok = True
        if not rows:
            if adv_day <= now.date():
                # A day that has happened always carries operations plans and
                # volcanic bulletins. Zero rows is a selector break, and a
                # quiet day is the one thing it cannot be.
                problems.append(
                    f"advisories: the index returned no rows for {adv_day}, "
                    "a day already past — a parse break, not a quiet day")
                lines += [f"**Advisories, {adv_day.isoformat()}** — EMPTY, and that "
                          f"day is past: a parse or fetch break, not a quiet day. "
                          f"`{url}`", ""]
            else:
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

    # FlightAware: two days back, yesterday, today — counted on the tracker's
    # own clock, which is UTC, and dated from the word the page prints.
    totals_rows = []
    ledger_rows = []
    today_utc = tracker_day(now)
    for offset, which in ((2, "minus2days"), (1, "yesterday"), (0, "today")):
        target = today_utc - dt.timedelta(days=offset)
        url = FLIGHTAWARE.format(which=which)
        try:
            page = fetch(url)
            totals = parse_totals(page)
            word = parse_day_word(page)
        except Exception as exc:  # noqa: BLE001
            lines += [f"**FlightAware, {which}** — SOURCE UNAVAILABLE "
                      f"({type(exc).__name__}: {exc}). `{url}`", ""]
            continue
        ok = True
        canc = totals.get("cancellations", {})
        dels = totals.get("delays", {})
        if not canc.get("us"):
            # The page answered. A dash in this row would read as "no
            # cancellations", which is a claim the pass did not make.
            problems.append(
                f"totals: the {which} page was read and yielded no "
                "US cancellation figure")
            lines += [f"**FlightAware, {which}** — READ, NO FIGURE PARSED "
                      f"(the page answered and the selector matched nothing). "
                      f"`{url}`", ""]
            continue
        tables += 1
        resolved, problem = resolve_page_day(word, target, today_utc)
        if problem:
            problems.append(problem)
        elif resolved != target:
            problems.append(
                f"totals: the {which} page says {word or 'nothing'}, which is "
                f"{resolved} and not {target}: the offset assumption broke")
        mark = long_label(resolved)
        totals_rows.append([
            mark,
            _moved(canc.get("us", "—"), prior, mark, 0),
            _moved(dels.get("us", "—"), prior, mark, 1),
            _moved(canc.get("all", "—"), prior, mark, 2),
            _moved(dels.get("all", "—"), prior, mark, 3),
        ])
        # Kept separately from the block, because a block shows three days and
        # the report needs every day of the period.
        ledger_rows.append({
            "date": resolved.isoformat(),
            "c_us": canc.get("us", "—"),
            "d_us": dels.get("us", "—"),
            "c_all": canc.get("all", "—"),
            "d_all": dels.get("all", "—"),
            "read": f"{now.strftime('%d%b%y %H:%M').upper()}",
        })
    if totals_rows:
        lines += [
            f"**FlightAware totals** — fetched {now.strftime('%H:%M')} CT. The "
            f"tracker's own day is **{today_utc.isoformat()}**: its pages roll at "
            "00:00Z, so between 18:00 CT and midnight it is already on tomorrow, "
            "and the date column is read from the day word each page prints. A "
            "figure that moved since the previous pass of this date is printed "
            "with the earlier reading, because the day settles.",
            "",
        ]
        lines += _table(
            ["Day", "Cancels (US)", "Delays (US)", "Cancels (all)", "Delays (all)"],
            totals_rows,
        )
        lines.append("")

    # Snapshots, so an advisory can still be cited after the 15-day window.
    # Every recorded capture is opened and checked for the wording it should
    # carry, and a document no archive holds is captured on the spot.
    #
    # The checks run concurrently because they are independent reads against a
    # service that answers in anywhere from 0.5 s to 20 s: serially, twenty of
    # them outlived a two-minute window on 16NOV26 and the pass wrote nothing
    # at all. Saves stay serial, because the budget is a courtesy to somebody
    # else's machine.
    all_items, tail_start = watch_items(day, all_rows)
    items = all_items[:ARCHIVE_CAP]
    resolved = []
    if items:
        with futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
            resolved = list(pool.map(_resolve, items))

    caps = []
    citation_rows = []
    budget, tail_budget = SAVE_BUDGET, SAVE_BUDGET_TAIL
    verified = saved = 0
    for position, (key, url, needles, cap, why) in enumerate(resolved):
        note = ""
        stamp = link = ""
        tail = position >= tail_start
        may_save = (tail_budget > 0) if tail else (budget > 0)
        if cap:
            stamp, link = cap["timestamp"], cap["url"]
        elif may_save:
            if tail:
                tail_budget -= 1
                limit = SAVE_TIMEOUT_TAIL
            else:
                budget -= 1
                limit = SAVE_TIMEOUT
            try:
                new = save_capture(url, timeout=limit)
            except Exception as exc:  # noqa: BLE001
                new = None
                note = f"{why}; save failed ({type(exc).__name__})"
            if new:
                good, vwhy = verify_capture(new["url"], needles)
                if good:
                    stamp, link = new["timestamp"], new["url"]
                    note = "saved this pass"
                    saved += 1
                else:
                    note = f"saved this pass, {vwhy}"
        else:
            note = f"{why}; save budget spent" if why else "save budget spent"
        if stamp:
            verified += 1
            caps.append([key, stamp, link, note])
            citation_rows.append((key, link, stamp))
        else:
            # `no capture` is a claim about the archive; a snapshot that would
            # not open is a claim about the checker. The archive throttles a
            # client that has just asked it for nine saves, so the two are not
            # the same finding and must not read the same.
            verdict = "unverified" if "did not serve" in (note or why) else "no capture"
            caps.append([key, verdict, "", note or why])

    dropped = len(all_items) - len(items)
    if caps:
        lines += ["**Wayback captures** — every snapshot below was fetched and "
                  "checked for the wording it should carry; `no capture` means no "
                  "archive holds the document, and the note says whether a save "
                  f"was requested. Fetched {now.strftime('%H:%M')} CT. The advisory "
                  "index keeps 15 days. "
                  + (f"{dropped} watch item(s) fell outside this pass's cap of "
                     f"{ARCHIVE_CAP}. " if dropped > 0 else ""), ""]
        lines += _table(["Watch", "Captured (UTC)", "Snapshot", "Note"], caps)
        lines.append("")

    lines += [
        f"coverage: {len(all_rows)} advisory rows, {tables} totals tables, "
        f"{len(all_items)} watch items ({verified} verified, {saved} saved this pass)",
        "",
    ]
    return Pass("\n".join(lines).rstrip() + "\n", ok, problems,
                totals=ledger_rows, citations=citation_rows)


def upsert(text: str, day_label: str, block: str) -> str:
    """Replace this date's block; leave any section that follows the log alone."""
    if LOG_HEADING not in text:
        text = text.rstrip() + "\n\n---\n\n" + LOG_HEADING + "\n"
    head, _, rest = text.partition(LOG_HEADING)
    # The log ends at the next top-level section, not at the end of the file:
    # the ledger and the citation list follow it, and a block appended after
    # them would be outside the log and outside their reach.
    nxt = re.search(r"^## ", rest, re.M)
    log = rest[:nxt.start()] if nxt else rest
    tail = rest[nxt.start():] if nxt else ""
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
    body = head + LOG_HEADING + log.rstrip() + "\n"
    return body + ("\n" + tail if tail else "")


def section(text: str, heading: str) -> str:
    match = re.search(r"^" + re.escape(heading) + r"\s*$.*?(?=^## |\Z)", text, re.S | re.M)
    return match.group(0) if match else ""


def replace_section(text: str, heading: str, body: str) -> str:
    block = heading + "\n\n" + body.strip() + "\n"
    pattern = re.compile(r"^" + re.escape(heading) + r"\s*$.*?(?=^## |\Z)", re.S | re.M)
    if pattern.search(text):
        return pattern.sub(lambda _m: block + "\n", text, count=1).rstrip() + "\n"
    return text.rstrip() + "\n\n---\n\n" + block


MONTHS = {name: index for index, name in enumerate(
    ("JAN", "FEB", "MAR", "APR", "MAY", "JUN",
     "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"), start=1)}


def iso_from_mark(mark: str) -> "str | None":
    """`Sun 15NOV26` -> `2026-11-15`. The block's own day label, not a guess."""
    match = re.match(r"^[A-Z][a-z]{2} (\d{2})([A-Z]{3})(\d{2})$", mark.strip())
    month = MONTHS.get(match.group(2)) if match else None
    if not month:
        return None
    return f"20{match.group(3)}-{month:02d}-{int(match.group(1)):02d}"


def _read_stamp(stamp: str) -> dt.datetime:
    try:
        return dt.datetime.strptime(stamp.strip(), "%d%b%y %H:%M")
    except (ValueError, AttributeError):
        return dt.datetime.min


def harvest_ledger(text: str) -> "dict[str, dict]":
    """Every totals row the log already holds, keyed by the date it describes."""
    rows: "dict[str, dict]" = {}
    for body in re.findall(
            r"^### \d{2}[A-Z]{3}\d{2}\s*$.*?(?=^### |^\*\*Reading — |^## |\Z)",
            text, re.S | re.M):
        when = re.search(r"\*\*Collected\*\*\s+(\d{2}[A-Z]{3}\d{2} \d{2}:\d{2}) CT", body)
        stamp = when.group(1) if when else ""
        for mark, c_us, d_us, c_all, d_all in FIGROW.findall(body):
            iso = iso_from_mark(mark)
            if not iso:
                continue
            row = {
                "date": iso,
                "c_us": c_us.strip().split(" (")[0],
                "d_us": d_us.strip().split(" (")[0],
                "c_all": c_all.strip().split(" (")[0],
                "d_all": d_all.strip().split(" (")[0],
                "read": stamp,
            }
            current = rows.get(iso)
            if current is None or _read_stamp(stamp) >= _read_stamp(current["read"]):
                rows[iso] = row
    return rows


def merge_ledger(text: str, live: "list[dict]") -> "dict[str, dict]":
    rows = harvest_ledger(text)
    for row in live:
        current = rows.get(row["date"])
        if current is None or _read_stamp(row["read"]) >= _read_stamp(current["read"]):
            rows[row["date"]] = dict(row)
    return rows


def render_ledger(rows: "dict[str, dict]") -> str:
    lines = [
        "Every date this job has read, merged and kept. FlightAware shows three "
        "days at a time, so a settled figure leaves its pages for good; this "
        "table is where it stays. A later reading replaces an earlier one for "
        "the same date, and a date is never dropped.",
        "",
        "| Date | Cancels (US) | Delays (US) | Cancels (all) | Delays (all) | Last read (CT) |",
        "|---|---|---|---|---|---|",
    ]
    for iso in sorted(rows):
        row = rows[iso]
        lines.append(f"| {iso} | {row['c_us']} | {row['d_us']} | {row['c_all']} | "
                     f"{row['d_all']} | {row['read']} |")
    return "\n".join(lines)


def harvest_citations(text: str) -> "dict[str, tuple]":
    rows: "dict[str, tuple]" = {}
    for key, url, stamp in re.findall(
            r"^\|\s*([^|]+?)\s*\|\s*(https?://[^|\s]+)\s*\|\s*([^|]*)\|",
            section(text, CITATIONS_HEADING), re.M):
        rows[key] = (url.strip(), stamp.strip())
    return rows


def render_citations(rows: "dict[str, tuple]") -> str:
    lines = [
        "Generated from §19's verified captures — **cite these URLs, not the ones "
        "in §15 or §16, which were written by hand before the snapshots were "
        "checked.** Every row here was fetched and had its wording checked when "
        "it was recorded; `python3 scripts/faa-ground-stop-pack.py --audit` "
        "re-checks all of them and exits nonzero if any stops serving its "
        "document.",
        "",
        "| Document | Cite this URL | Captured (UTC) |",
        "|---|---|---|",
    ]
    for key in sorted(rows):
        url, stamp = rows[key]
        lines.append(f"| {key} | {url} | {stamp} |")
    return "\n".join(lines)


def audit(text: str) -> int:
    """Re-open every citation the pack hands a writer.

    Exit 4 when a snapshot serves and does not carry its document — that is a
    citation that would mislead a reader. Exit 3 when a snapshot could not be
    read at all: the archive throttles, so "did not serve" is a claim about the
    checker and not about the document, and the two must not read alike. One
    retry after a pause, because the first failure is usually the throttle.
    """
    rows = harvest_citations(text)
    if not rows:
        print("citation-audit: no citations recorded; nothing to check")
        return 0
    keys = sorted(rows)

    def check(key: str) -> "tuple[str, str, str, str]":
        url = rows[key][0]
        ok, why = verify_capture(url, needles_for(key))
        if not ok and "did not serve" in why:
            time.sleep(2)
            ok, why = verify_capture(url, needles_for(key))
        if ok:
            return key, url, "", "verified"
        verdict = "unverified" if "did not serve" in why else "failed"
        return key, url, why, verdict

    with futures.ThreadPoolExecutor(max_workers=AUDIT_WORKERS) as pool:
        results = list(pool.map(check, keys))
    failed = [r for r in results if r[3] == "failed"]
    unverified = [r for r in results if r[3] == "unverified"]
    print(f"citation-audit: {len(results)} citation(s), "
          f"{len(results) - len(failed) - len(unverified)} verified, "
          f"{len(unverified)} unverified, {len(failed)} failed")
    for key, url, why, _ in failed:
        print(f"citation-audit: FAIL {key}: {why} — {url}")
    for key, url, why, _ in unverified:
        print(f"citation-audit: UNVERIFIED {key}: {why} — {url}")
    if failed:
        return 4
    return 3 if unverified else 0


ADVISORY_KEY = re.compile(r"^(\d{8})/(\d+)$")


def _snapshot_gone(url: str, tries: int = 2, pause: float = 3.0) -> "tuple[bool, str]":
    """True only when the archive says the capture is not there, i.e. HTTP 404.

    A 429, a timeout or a dropped connection is a claim about the checker and is
    never a reason to remove a citation; that is the difference the audit's
    `unverified` verdict exists to keep. Two attempts, because the first 404 was
    once a flake.
    """
    why = ""
    for attempt in range(tries):
        try:
            fetch(url, timeout=VERIFY_TIMEOUT)
            return False, ""
        except urllib.error.HTTPError as exc:  # noqa: PERF203 - two attempts, by design
            why = f"HTTP {exc.code}"
            if exc.code != 404:
                return False, why
        except Exception as exc:  # noqa: BLE001 - reported as the reason it was kept
            return False, type(exc).__name__
        if attempt + 1 < tries:
            time.sleep(pause)
    return True, why


def prune_dead(text: str) -> "tuple[str, list[str], list[str]]":
    """Drop §21 rows whose snapshot the archive no longer holds (24NOV26).

    Why this exists. §21 is rebuilt as `existing rows ∪ this pass's verified
    rows`, so a row whose capture has died is never removed: the audit reports
    it `unverified`, and the release gate that runs `--audit` before the writer
    aborts for good. Measured 24NOV26, seven advisory rows returned 404 on
    repeated fetches, the CDX index held nothing for either day, and the live FAA
    database answered "no advisories match your selection criteria" for every
    date — a citation no reader and no checker could ever open again.

    Two safeguards, because deleting a citation is not a thing to do on a
    hunch. The drop happens only on a 404 (never a throttle or a timeout), and
    only when that advisory's own day index is in §21 and verifies: the index
    prints the advisory's number and title, so the fact that it was issued
    survives the row. An advisory whose index does not verify is kept and
    reported.

    Returns (new_text, dropped, kept), each line saying what and why.
    """
    rows = harvest_citations(text)
    dropped: "list[str]" = []
    kept: "list[str]" = []
    for key in sorted(rows):
        m = ADVISORY_KEY.match(key)
        if not m:
            continue
        url, _stamp = rows[key]
        gone, why = _snapshot_gone(url)
        if not gone:
            continue
        mdY = m.group(1)
        iso = f"{mdY[4:8]}-{mdY[0:2]}-{mdY[2:4]}"
        idx_key = f"index {iso}"
        idx = rows.get(idx_key)
        if not idx:
            kept.append(f"{key}: snapshot {why}, but there is no {idx_key} row "
                        "to cite instead")
            continue
        ok, vwhy = verify_capture(idx[0], needles_for(idx_key))
        if not ok:
            kept.append(f"{key}: snapshot {why} and {idx_key} does not verify "
                        f"({vwhy or 'empty'})")
            continue
        dropped.append(f"{key}: snapshot {why}; its day index {idx_key} verifies, "
                       f"so cite {idx[0]}")
        del rows[key]
    return replace_section(text, CITATIONS_HEADING, render_citations(rows)), dropped, kept


ARCHIVE_URL = re.compile(r"https?://web\.archive\.org/web/\d+/[^\s)\]\"'<>`]+")
ADVISORY_URL = re.compile(r"https?://www\.fly\.faa\.gov/adv/adv_otherdis\?[^\s)\]\"'<>`]+")


def _trim(url: str) -> str:
    return url.rstrip(".,;:)]")


def _advisory_key(url: str) -> str:
    """`adv_date=11132026&advn=111` -> `11132026/111`, from the URL itself."""
    m = re.search(r"adv_date=(\d{8})&advn=(\d+)", url)
    return f"{m.group(1)}/{int(m.group(2))}" if m else ""


def article_audit(pack_text: str, article: str, source: str) -> int:
    """Check a finished piece against §21 before it publishes.

    The rule is not "every URL must appear in §21", because a different capture
    that opens and carries the document is a good citation. The rule is that
    **every citation can be opened and is the document**, and that **every
    advisory cited has an archived copy somewhere in the piece** — the live
    `adv_otherdis` URL dies when the FAA's fifteen-day window closes, which is
    inside the drafting window for this series.

    Exit 4 for a citation that serves the wrong document, or an advisory with
    no archived copy; 3 for one that could not be read. Nothing else is a
    failure: a capture §21 does not list is reported as `unlisted`, because the
    check that matters has already been made.
    """
    cites = harvest_citations(pack_text)
    known = {url for url, _ in cites.values()}
    archive, live = [], []
    for url in (_trim(u) for u in ARCHIVE_URL.findall(article)):
        if url not in archive:
            archive.append(url)
    for url in (_trim(u) for u in ADVISORY_URL.findall(article)):
        if url not in live:
            live.append(url)

    if not archive and not live:
        print(f"citation-audit: {source} cites no archived or advisory URL")
        return 0

    archived_keys = {_advisory_key(u) for u in archive}
    uncovered = [u for u in live if _advisory_key(u) not in archived_keys]
    unlisted = [u for u in archive if u not in known]

    def check(url: str) -> "tuple[str, str, str]":
        # A loose needle on purpose: §21 already established WHICH document a
        # listed URL is, and this asks whether it still opens as one.
        needles = (["advzy"] if "adv_otherdis" in url
                   else ["atcscc advisories"] if "adv_list" in url else [])
        ok, why = verify_capture(url, needles)
        if not ok and "did not serve" in why:
            time.sleep(2)
            ok, why = verify_capture(url, needles)
        return url, ("verified" if ok else
                     ("unverified" if "did not serve" in why else "failed")), why

    results = []
    if archive:
        with futures.ThreadPoolExecutor(max_workers=AUDIT_WORKERS) as pool:
            results = list(pool.map(check, archive))
    failed = [r for r in results if r[1] == "failed"]
    unverified = [r for r in results if r[1] == "unverified"]
    verified = len(results) - len(failed) - len(unverified)

    print(f"citation-audit: {source}: {len(archive)} archive URL(s) "
          f"({verified} verified, {len(unverified)} unverified, {len(failed)} failed), "
          f"{len(live)} live advisory URL(s), {len(known)} row(s) in §21")
    for url in unlisted:
        print(f"citation-audit: UNLISTED (opens; not in §21) — {url}")
    for url, _, why in failed:
        print(f"citation-audit: FAIL {why} — {url}")
    for url, _, why in unverified:
        print(f"citation-audit: UNVERIFIED {why} — {url}")
    for url in uncovered:
        print(f"citation-audit: FAIL advisory cited with no archived copy — {url}")
    if live and not uncovered:
        print(f"citation-audit: {len(live)} live advisory URL(s) are backed by an "
              "archived copy in the piece; they will 404 after the 15-day window")

    if failed or uncovered:
        return 4
    return 3 if unverified else 0


def main(argv: "list[str]") -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--date", help="CT date to collect (YYYY-MM-DD); default today")
    ap.add_argument("--now", help="ISO timestamp to treat as now (CT), for tests")
    ap.add_argument("--pack", default=str(PACK))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--audit", action="store_true",
                    help="re-open every recorded citation and fail on a miss")
    ap.add_argument("--prune-dead", action="store_true",
                    help="drop a §21 row whose snapshot is gone (HTTP 404), "
                         "when that advisory's day index still verifies")
    ap.add_argument("--file", help="with --audit: check a finished piece against §21")
    args = ap.parse_args(argv)

    now = dt.datetime.now(CT)
    if args.now:
        # Injectable clock, the same shape sitrep-watchdog.py takes: a check
        # whose answer depends on today's date can be observed but not
        # asserted about, and a test that reads the real clock goes red the
        # day it happens to be right.
        now = dt.datetime.fromisoformat(args.now)
        if now.tzinfo is None:
            now = now.replace(tzinfo=CT)
    day = (dt.date.fromisoformat(args.date) if args.date else now.date())
    pack = pathlib.Path(args.pack)
    text = pack.read_text(encoding="utf-8") if pack.exists() else ""

    if args.prune_dead:
        new_text, dropped, kept = prune_dead(text)
        for line in dropped:
            print(f"prune-dead: DROPPED {line}")
        for line in kept:
            print(f"prune-dead: KEPT {line}")
        if not dropped:
            print("prune-dead: nothing to drop")
            return 0
        if args.dry_run:
            print(f"prune-dead: dry run — {len(dropped)} row(s) would be dropped")
            return 0
        pack.write_text(new_text, encoding="utf-8")
        print(f"prune-dead: {len(dropped)} row(s) dropped from §21")
        return 0

    if args.audit:
        if args.file:
            source = pathlib.Path(args.file)
            if not source.exists():
                print(f"citation-audit: no such file: {source}")
                return 3
            return article_audit(text, source.read_text(encoding="utf-8"),
                                 source.name)
        return audit(text)

    result = collect(day, offline=args.offline, prior=prior_state(text, label(day)),
                     now=now)
    if not result.ok:
        print(f"faa-ground-stop-pack: nothing collected for {day}; no block written.")
        return 3

    for problem in result.problems:
        print(f"faa-ground-stop-pack: {problem}")

    if args.dry_run:
        print(result.block)
        return 4 if result.problems else 0

    new_text = upsert(text, label(day), result.block)
    new_text = replace_section(new_text, LEDGER_HEADING,
                                render_ledger(merge_ledger(new_text, result.totals)))
    cites = harvest_citations(new_text)
    for key, url, stamp in result.citations:
        cites[key] = (url, stamp)
    new_text = replace_section(new_text, CITATIONS_HEADING, render_citations(cites))
    pack.write_text(new_text, encoding="utf-8")
    print(f"faa-ground-stop-pack: {label(day)} written to {pack}")
    return 4 if result.problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
