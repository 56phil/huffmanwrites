#!/usr/bin/env python3
"""Fetch current 2026 Senate race ratings from every forecaster.

Philip, 2026-09-19: "Add ratings to the content."

The weekly Senate report needs a ratings table every week, not only when a
forecaster moves a race. But the three forecasters the site actually cites are
all closed to automated fetch — cookpolitical.com, centerforpolitics.org and
insideelections.com each return **HTTP 403** to curl even with a full browser
User-Agent and Accept headers. So they cannot be read directly by the research
agent, and a ratings table sourced "from Cook" would be uncitable.

Wikipedia's "2026 United States Senate elections" article carries the standard
aggregate ratings table, with every forecaster in its own column and an as-of
date on each. That page IS fetchable, and it cites each forecaster. It is the
practical route to the ratings, and it is what this script reads.

The extraction is not obvious and has two traps, both hit while writing this:
  1. Cells leak Parsoid/`mw:Nowiki` fragments — `"]}' id="mwB9Y">Tossup` — with
     no leading '<', so stripping tags leaves the attribute tail glued to the
     rating and a strict regex misses it. Fix: take the text after the LAST '>'
     in the cell.
  2. That bug silently dropped exactly the rows it mattered most to keep —
     Maine, North Carolina, Ohio and Texas, the four most competitive races —
     because those use the leaked-fragment markup. A table that loses the
     toss-ups is worse than no table.

Exit codes: 0 ok, 2 could not fetch or parse the page.

Usage:
  fetch-senate-ratings.py                # competitive races, markdown table
  fetch-senate-ratings.py --all          # all 35 races
  fetch-senate-ratings.py --changes      # diff against the stored baseline
  fetch-senate-ratings.py --update-baseline
  fetch-senate-ratings.py --json         # machine-readable
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STATE = REPO / "scripts" / "senate-ratings-state.json"

PAGE = "2026_United_States_Senate_elections"
API = f"https://en.wikipedia.org/api/rest_v1/page/html/{PAGE}"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")

# The forecasters the site cites in its own essays, plus the two model-based
# ones the reports lean on. Order is presentation order.
CITED = ["Cook", "IE", "Sabato", "RCP", "DDHQ", "Silver"]

# A rating that carries information about a competitive race.
COMPETITIVE = re.compile(r"^(toss-?up|tilt|lean)", re.I)

RATING = re.compile(
    r"^(Toss-?up|Tilt [DR]|Lean [DR]|Likely [DR]|Solid [DR]|Safe [DR])\s*(\(flip\))?$",
    re.I,
)

# State names needing parentheses in the display table.
SPECIALS = {"Florida(special)": "Florida (special)", "Ohio(special)": "Ohio (special)"}


def _die(msg: str, code: int = 2) -> "None":
    print(f"senate-ratings: ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def fetch() -> str:
    r = subprocess.run(
        ["curl", "-sL", "--max-time", "40", "-A", UA, API],
        capture_output=True,
    )
    if r.returncode != 0:
        _die(f"curl exit {r.returncode}")
    body = r.stdout.decode("utf-8", "replace")
    if "Cook" not in body or "Toss" not in body:
        _die("page fetched but the ratings table is absent — shape changed?")
    return body


def cell_text(raw: str) -> str:
    """Text of a table cell, robust to Wikipedia's leaked markup.

    Wikipedia's REST HTML emits fragments such as `"]}' id="mwB9Y">Tossup`
    where the leading '<' was consumed by the template. Stripping tags leaves
    the attribute tail attached to the value, so take the text after the last
    '>' to discard it.
    """
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", raw, flags=re.S | re.I)
    raw = re.sub(r"<[^>]*>", "", raw)
    raw = html.unescape(raw)
    if ">" in raw:
        raw = raw[raw.rindex(">") + 1:]
    return re.sub(r"\s+", " ", raw).strip()


def parse(page: str) -> "tuple[list[str], list[dict], dict[str, str]]":
    """Return (forecaster_names, races, as_of_dates)."""
    tables = []
    for m in re.finditer(r"<table[^>]*>", page):
        end = page.find("</table>", m.start())
        if end < 0:
            continue
        tbl = page[m.start():end]
        if "Cook" in tbl and re.search(r"Toss-?up|Lean [DR]|Solid [DR]", tbl):
            tables.append(tbl)
    if not tables:
        _die("no ratings table found")
    table = max(tables, key=len)

    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table, re.S)
    if len(rows) < 5:
        _die(f"ratings table has only {len(rows)} rows")

    # Header: forecaster names are the link texts, skipping the label columns.
    # Each column also carries its own as-of date, inside a `data-mw` template
    # param (`"1":{"wt":"Sep. 15,&lt;br />2026"}`), NOT as visible text. Those
    # dates differ per forecaster — Cook updates weekly, Sabato less often — so
    # a table stamped with today's date for every column would be a factual
    # error in a fact-checked publication.
    names: "list[str]" = []
    as_of: "dict[str, str]" = {}
    for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", rows[1], re.S):
        lm = re.search(r"<a[^>]*>([^<]+)</a>", c)
        if not lm or lm.group(1) in ("State", "PVI", "Senator"):
            continue
        name = lm.group(1).strip()
        names.append(name)
        raw_date = re.search(r'"1":\{"wt":"([^"]+)"\}', c)
        if raw_date:
            cleaned = html.unescape(raw_date.group(1))
            cleaned = re.sub(r"<br\s*/?>", " ", cleaned)
            cleaned = re.sub(r"\s+", " ", cleaned).strip().rstrip(",")
            as_of[name] = cleaned
    if not names:
        _die("could not read the forecaster column headers")

    out = []
    for row in rows[2:]:
        cells = [cell_text(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, re.S)]
        if len(cells) < 4:
            continue
        state = cells[0]
        if not state or state.startswith("Overall") or state in ("State", "]"):
            continue
        ratings = [RATING.match(c).group(0) for c in cells if RATING.match(c)]
        out.append({"state": state, "pvi": cells[1],
                    "by": dict(zip(names, ratings))})

    if len(out) < 30:
        _die(f"parsed only {len(out)} states; expected ~35 — refusing to emit a partial table")
    return names, out, as_of


def is_competitive(d: dict) -> bool:
    return any(COMPETITIVE.match(d["by"].get(k, "") or "") for k in ("Cook", "IE", "Sabato"))


def display(state: str) -> str:
    return SPECIALS.get(state, state)


def load_state() -> dict:
    if STATE.is_file():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_state(names, data) -> None:
    STATE.write_text(json.dumps({
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "as_of": names,
        "ratings": {d["state"]: d["by"] for d in data},
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def changes(data: "list[dict]") -> "list[tuple[str, str, str, str]]":
    prior = load_state().get("ratings") or {}
    if not prior:
        return []
    out = []
    for d in data:
        old = prior.get(d["state"]) or {}
        for name, rating in d["by"].items():
            was = old.get(name, "")
            if was and rating and was != rating:
                out.append((d["state"], name, was, rating))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch 2026 Senate race ratings.")
    ap.add_argument("--all", action="store_true", help="every race, not just competitive")
    ap.add_argument("--changes", action="store_true", help="diff against the stored baseline")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--update-baseline", action="store_true", help="store current ratings")
    args = ap.parse_args()

    names, data, as_of = parse(fetch())
    print(f"senate-ratings: read {len(data)} races; forecasters: {', '.join(names)}",
          file=sys.stderr)

    if args.update_baseline:
        save_state(names, data)
        print(f"senate-ratings: baseline updated ({len(data)} races)", file=sys.stderr)
        return 0

    if args.json:
        print(json.dumps({"forecasters": names, "as_of": as_of, "races": data}, indent=2))
        return 0

    if args.changes:
        ch = changes(data)
        if not ch:
            print("No rating changes since the stored baseline.", file=sys.stderr)
            print("(no changes)")
            return 0
        for state, name, was, now in ch:
            print(f"  {display(state):18} {name:8} {was:14} -> {now}")
        return 0

    subset = data if args.all else [d for d in data if is_competitive(d)]
    cols = [c for c in CITED if c in names]
    print(f"| Race | PVI | {' | '.join(cols)} |")
    print(f"|---|---|{'---|' * len(cols)}")
    for d in subset:
        vals = " | ".join(d["by"].get(c, "") or "—" for c in cols)
        print(f"| {display(d['state'])} | {d['pvi']} | {vals} |")
    # Each forecaster updates on its own schedule, so stamp each column with its
    # own as-of date rather than implying they are all current as of today.
    stamp = "; ".join(f"{c} {as_of.get(c, 'date unknown')}" for c in cols)
    print(f"\nRatings as of — {stamp}.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
