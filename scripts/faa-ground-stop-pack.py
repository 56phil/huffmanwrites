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
import dataclasses
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
# These three are the days before the daily pass started; every later day's
# index is captured by that day's own pass.
EVENT_INDEX_DAYS = ("2026-11-13", "2026-11-14", "2026-11-15")

ARCHIVE_CAP = 30          # watch items checked per pass
SAVE_BUDGET = 6           # save requests per pass: a courtesy, and a bound
SAVE_TIMEOUT = 100        # a save answered in 18.4 s when measured; 45 s was not enough
VERIFY_TIMEOUT = 45

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
    ok: bool                  # anything at all was read
    problems: dataclasses.field(default_factory=list)  # read, but did not parse

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


def watch_items(day: dt.date, all_rows: "list[dict]") -> "list[tuple[str, str, list[str]]]":
    """Every document worth a capture this pass: key, URL, wording to require."""
    items: "list[tuple[str, str, list[str]]]" = []
    seen = set()

    def add(key: str, url: str, needles: "list[str]") -> None:
        if url in seen:
            return
        seen.add(url)
        items.append((key, url, needles))

    for mdY_, n_ in ARCHIVE_WATCH:
        add(f"{mdY_}/{n_}",
            ADV_PAGE.format(mdY=mdY_, n=n_),
            [f"advzy {n_:03d}", f"advzy {n_}"])

    # Only documents that can carry the event: the six above, plus any row
    # whose own title is a ground stop or an operations plan. The index also
    # prints volcanic-activity bulletins and FCA notices, and a request on
    # those would spend a save to learn nothing.
    for row in all_rows:
        key = (row["adv_date"], int(row["n"]))
        if key in ARCHIVE_WATCH:
            continue
        title = row["title"].upper()
        if "GROUND STOP" in title or "OPERATIONS PLAN" in title:
            add(f"{row['adv_date']}/{row['n']}",
                ADV_PAGE.format(mdY=row["adv_date"], n=row["n"]),
                [f"advzy {int(row['n']):03d}", f"advzy {int(row['n'])}"])

    # The day indexes themselves: the days before the pass existed, then this
    # pass's own day.
    for iso in list(EVENT_INDEX_DAYS) + [day.isoformat()]:
        add(f"index {iso}", ADV_URL.format(date=iso), [index_needle(iso)])

    add("faa-qa", QA_URL, [QA_NEEDLE])
    return items


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
        mark = long_label(target)
        totals_rows.append([
            mark,
            _moved(canc.get("us", "—"), prior, mark, 0),
            _moved(dels.get("us", "—"), prior, mark, 1),
            _moved(canc.get("all", "—"), prior, mark, 2),
            _moved(dels.get("all", "—"), prior, mark, 3),
        ])
    if totals_rows:
        lines += [
            f"**FlightAware totals** — fetched {now.strftime('%H:%M')} CT. The date "
            "column is this pass's CT date for that page; the tracker words its own "
            "pages by weekday. A figure that moved since the previous pass of this "
            "date is printed with the earlier reading, because the day settles.",
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
    items = watch_items(day, all_rows)
    caps = []
    budget = SAVE_BUDGET
    verified = saved = 0
    for key, url, needles in items[:ARCHIVE_CAP]:
        note = ""
        stamp = link = ""
        held, why = False, "no capture"
        try:
            cap = wayback_capture(url)
        except Exception as exc:  # noqa: BLE001
            cap = None
            note = f"availability unavailable ({type(exc).__name__})"
        if cap:
            held, why = verify_capture(cap["url"], needles)
            if held:
                stamp, link = cap["timestamp"], cap["url"]
        if not held and budget > 0:
            budget -= 1
            try:
                new = save_capture(url)
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
        elif not held:
            note = f"{why}; save budget spent" if why else "save budget spent"
        if stamp:
            verified += 1
            caps.append([key, stamp, link, note])
        else:
            caps.append([key, "no capture", "", note or why])

    dropped = len(items) - min(len(items), ARCHIVE_CAP)
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
        f"{len(items)} watch items ({verified} verified, {saved} saved this pass)",
        "",
    ]
    return Pass("\n".join(lines).rstrip() + "\n", ok, problems)


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
    ap.add_argument("--now", help="ISO timestamp to treat as now (CT), for tests")
    ap.add_argument("--pack", default=str(PACK))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--offline", action="store_true")
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

    pack.write_text(upsert(text, label(day), result.block), encoding="utf-8")
    print(f"faa-ground-stop-pack: {label(day)} written to {pack}")
    return 4 if result.problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
