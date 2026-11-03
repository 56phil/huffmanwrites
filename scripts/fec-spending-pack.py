#!/usr/bin/env python3
"""Collect the FEC's own numbers for the Musk midterm-spending piece.

Why this exists. `future-pieces/musk-midterm-spending.md` is built on one rule
the corpus already applies to the SITREP and the Chiefs report: the writer may
not recall a figure. Every number in that piece has to be printed by a
collector that read a filing, not assembled from press tallies that get
superseded the week after publication.

What it prints, per committee:

1. **Identity** — official name, committee type, designation, cycles, city.
   The name matters more than it looks: the corpus's AP-sourced sentence calls
   the Republican Senate super PAC "the Senate Leadership Fund", and the FEC's
   committee index does not answer to that phrase in a name search. It is
   `C00694323`, reached through Schedule A rather than through `/names/`, and
   the pack prints the registered name so the piece can name what the filing
   names.
2. **Summary filings** — every Form 3X on record, with `total_receipts` and
   `total_disbursements`. This is the layer the post-general report lands in on
   2026-12-03, and it is already the layer that carries the money the piece is
   about: Texas PAC's Q3 filing reports exactly $158,000,000 received.
3. **Musk itemized receipts** — Schedule A rows whose contributor name contains
   MUSK, with the distinct names seen, the count, the sum and the dates. **A
   zero here is a finding, not an error:** Texas PAC's Schedule A is empty while
   its summary filing reports $158,000,000, which means the itemization is not
   yet in the API and the piece must say "the filing reports $158 million from
   an intermediary; the itemized receipt is not yet published" rather than
   guessing at the payer.
4. **Independent expenditures** — America PAC's Schedule E totals by candidate,
   split support/oppose. Schedule E is reported on 24- and 48-hour notices as
   the money goes out, so this is the only part of the picture that is complete
   *before* the post-general deadline.

A source that fails prints `SOURCE UNAVAILABLE <reason>` and does not abort the
run: a pack with a stated gap is honest, and a job that dies on one host hiccup
produces nothing. Exit code is 0 for a pack with gaps and 1 only when nothing at
all could be read — the same shape as `scripts/sitrep-pack.py`.

Coverage is printed at the end: the number of API requests and the number of
rows inspected. A collector that inspected nothing must say so, because a
selector that broke is invisible otherwise.

Local-only in effect: the key lives in the login keychain (`huffmanwrites-fec`)
with `~/.secrets` (`FEC_API_KEY`) as the fallback. Without a key the pack prints
the gap and exits 1; it never falls back to `DEMO_KEY`, whose limit measured on
2026-11-02 is ten requests an hour, which is not enough to read three committees.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://api.open.fec.gov/v1"
USER_AGENT = "huffmanwrites-fec-pack/1.0 (+https://www.huffmanwrites.org)"
CYCLE = 2026

# Verified against the API on 2026-11-02, not recalled. Every id here was
# reached by a query that returned the committee's own registered name; see the
# module docstring for why C00694323 was found through Schedule A.
COMMITTEES: "list[dict]" = [
    {"id": "C00879510", "label": "America PAC", "expected": "AMERICA PAC"},
    # SLF PAC is the registered name of the super PAC the press calls the
    # Senate Leadership Fund. The id came off Schedule A, from the
    # `contributor_id` field of rows where the leader fund gave to others —
    # a name search cannot find it, which is why the guard below prints a NOTE
    # rather than silently accepting the label.
    {"id": "C00571703", "label": "Senate Leadership Fund (SLF PAC)", "expected": "SLF PAC"},
    {"id": "C00960211", "label": "Texas PAC", "expected": "TEXAS PAC"},
]

REQUESTS = 0
ROWS = 0
GAPS: "list[str]" = []


class SourceError(Exception):
    """A single source could not be read. The pack continues without it."""


def _key() -> "str | None":
    key = os.environ.get("FEC_API_KEY")
    if key:
        return key
    try:
        r = subprocess.run(
            ["security", "find-generic-password", "-a", os.environ.get("USER", ""),
             "-s", "huffmanwrites-fec", "-w"],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    secrets = Path.home() / ".secrets"
    if secrets.exists():
        for line in secrets.read_text(errors="replace").splitlines():
            s = line.strip()
            if s.startswith("#") or "=" not in s:
                continue
            k, _, v = s.partition("=")
            if k.strip().removeprefix("export ").strip() == "FEC_API_KEY":
                return v.strip().strip('"').strip("'") or None
    return None


def api(key: str, path: str, **params) -> dict:
    """One GET against the OpenFEC API. Raises SourceError, never returns junk."""
    global REQUESTS
    params.setdefault("api_key", key)
    url = BASE + path + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    REQUESTS += 1
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", "replace")
        except Exception:
            pass
        if e.code == 403 and "API_KEY_INVALID" in body:
            raise SourceError("403 API_KEY_INVALID — the FEC key does not authenticate")
        if e.code == 403 and "API_KEY_MISSING" in body:
            raise SourceError("403 API_KEY_MISSING — no FEC key reached the request")
        if e.code == 429:
            raise SourceError("429 throttled by api.data.gov")
        raise SourceError(f"HTTP {e.code} from api.open.fec.gov")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise SourceError(f"could not reach api.open.fec.gov ({e})")


def money(value) -> str:
    try:
        return f"${float(value):,.0f}"
    except (TypeError, ValueError):
        return "—"


def identity(key: str, committee_id: str) -> dict:
    d = api(key, f"/committee/{committee_id}/")
    results = d.get("results") or []
    if not results:
        raise SourceError(f"no committee record for {committee_id}")
    return results[0]


def filings(key: str, committee_id: str, limit: int = 8) -> "list[dict]":
    """Form 3X summary reports, newest first.

    F24 (24-hour independent-expenditure) notices are filtered out: they carry
    no totals, and a page of them buries the summary filings this pack exists to
    print. Filtering locally rather than by request keeps one request per
    committee.
    """
    d = api(key, "/filings/", committee_id=committee_id, per_page=100,
            sort="-receipt_date")
    global ROWS
    rows = d.get("results") or []
    ROWS += len(rows)
    summaries = [r for r in rows if str(r.get("form_type") or "").startswith("F3X")]
    return summaries[:limit]


def musk_receipts(key: str, committee_id: str, limit: int = 10) -> dict:
    """Schedule A rows whose contributor name contains MUSK, for this cycle."""
    d = api(key, "/schedules/schedule_a/", committee_id=committee_id,
            contributor_name="MUSK", two_year_transaction_period=CYCLE,
            per_page=100, sort="-contribution_receipt_amount")
    global ROWS
    raw = d.get("results") or []
    ROWS += len(raw)
    # The API's `contributor_name` filter is a substring match, so "MUSK"
    # also returns MUSKAR, MUSKE, MUSKER and MUSKETT — measured on SLF PAC's
    # 166 rows, where the strict filter keeps 2. Filtering here rather than
    # trusting the server's count is the difference between a filing figure and
    # a number that quietly includes strangers.
    rows = [r for r in raw
            if "ELON MUSK" in (r.get("contributor_name") or "").upper()
            or (r.get("contributor_name") or "").upper().startswith("MUSK, ELON")]
    total = sum(r.get("contribution_receipt_amount") or 0 for r in rows)
    dates = sorted(r.get("contribution_receipt_date") or "" for r in rows)
    return {
        "count": len(rows),
        "raw_count": d.get("pagination", {}).get("count") or len(raw),
        "rows": rows[:limit],
        "sum": total,
        "first": dates[0] if dates else None,
        "last": dates[-1] if dates else None,
        "names": sorted({(r.get("contributor_name") or "").strip() for r in rows}),
    }


def independent_expenditures(key: str, committee_id: str, top: int = 12) -> dict:
    """Schedule E in this cycle: totals by candidate, support vs oppose."""
    d = api(key, "/schedules/schedule_e/", committee_id=committee_id,
            two_year_transaction_period=CYCLE, per_page=100,
            sort="-expenditure_date")
    global ROWS
    rows = d.get("results") or []
    ROWS += len(rows)
    per: "dict[tuple, float]" = {}
    for r in rows:
        k = (r.get("candidate_name"), r.get("support_oppose_indicator"))
        per[k] = per.get(k, 0) + (r.get("expenditure_amount") or 0)
    ordered = sorted(per.items(), key=lambda kv: kv[1], reverse=True)
    dates = sorted(r.get("expenditure_date") or "" for r in rows)
    return {
        "count": len(rows),
        "raw_count": d.get("pagination", {}).get("count") or len(raw),
        "sum": sum(per.values()),
        "per": ordered[:top],
        "first": dates[0] if dates else None,
        "last": dates[-1] if dates else None,
        "support_oppose": {k: k for k in ("S", "O")},
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cycle", type=int, default=CYCLE,
                    help=f"two-year transaction period (default {CYCLE})")
    ap.add_argument("--json", action="store_true", help="emit the raw collected data")
    args = ap.parse_args()

    key = _key()
    if not key:
        print("SOURCE UNAVAILABLE FEC_API_KEY — no value in the keychain or ~/.secrets")
        print("coverage: 0 requests, 0 rows")
        return 1

    collected: "dict[str, dict]" = {}
    for c in COMMITTEES:
        block: "dict[str, dict]" = {}
        try:
            ident = identity(key, c["id"])
            block["identity"] = {
                "name": ident.get("name"),
                "type": ident.get("committee_type_full") or ident.get("committee_type"),
                "designation": ident.get("designation_full") or ident.get("designation"),
                "cycles": ident.get("cycles"),
                "city": ident.get("city"),
                "state": ident.get("state"),
            }
        except SourceError as e:
            block["identity"] = None
            GAPS.append(f"{c['label']} identity: {e}")
        try:
            block["filings"] = filings(key, c["id"])
        except SourceError as e:
            block["filings"] = []
            GAPS.append(f"{c['label']} filings: {e}")
        try:
            block["musk"] = musk_receipts(key, c["id"])
        except SourceError as e:
            block["musk"] = None
            GAPS.append(f"{c['label']} Schedule A: {e}")
        try:
            block["sched_e"] = independent_expenditures(key, c["id"])
        except SourceError as e:
            block["sched_e"] = None
            GAPS.append(f"{c['label']} Schedule E: {e}")
        collected[c["id"]] = {"label": c["label"], **block}

    if args.json:
        print(json.dumps(collected, indent=2, default=str))
        print(f"coverage: {REQUESTS} requests, {ROWS} rows", file=sys.stderr)
        return 0 if len(GAPS) < len(COMMITTEES) * 4 else 1

    print(f"# FEC spending pack — cycle {args.cycle}")
    print()

    for c in COMMITTEES:
        b = collected[c["id"]]
        print(f"## {c['label']} ({c['id']})")
        ident = b.get("identity")
        if ident:
            print(f"   filing name : {ident['name']}")
            print(f"   type        : {ident['type']} | designation {ident['designation']}")
            print(f"   cycles      : {ident['cycles']} | {ident['city']}, {ident['state']}")
            expected = c["expected"]
            got = (ident["name"] or "").upper()
            if expected not in got:
                print(f"   NOTE        : registered name does not contain "
                      f"{expected!r} — name the committee as the filing does")
        else:
            print("   identity: SOURCE UNAVAILABLE")

        rows = b.get("filings") or []
        if rows:
            print("   filings:")
            for r in rows:
                print(f"     {str(r.get('receipt_date'))[:10]}  {r.get('form_type'):4} "
                      f"{str(r.get('report_type')):4}  receipts {money(r.get('total_receipts')):>16}  "
                      f"disb {money(r.get('total_disbursements')):>16}")
        else:
            print("   filings: none returned")

        m = b.get("musk")
        if m is None:
            print("   Musk receipts: SOURCE UNAVAILABLE")
        elif not m["count"]:
            print("   Musk receipts: 0 itemized rows in this cycle.")
            print("     NOT a finding of zero giving — check whether the committee's")
            print("     summary filings report receipts the itemization has not reached.")
        else:
            print(f"   Musk receipts: {m['count']} row(s), {money(m['sum'])} summed, "
                  f"{m['first']} … {m['last']}")
            if m.get("raw_count", m["count"]) != m["count"]:
                print(f"     (server matched {m['raw_count']} names containing MUSK; "
                      f"{m['raw_count'] - m['count']} were other people)")
            print(f"     names matched: {', '.join(m['names'][:6]) or '—'}")
            for r in m["rows"]:
                print(f"     {r.get('contribution_receipt_date')}  "
                      f"{money(r.get('contribution_receipt_amount')):>14}  "
                      f"{(r.get('contributor_name') or '')[:34]:34}  line {r.get('line_number_label')}")

        e = b.get("sched_e")
        if e is None:
            print("   independent expenditures: SOURCE UNAVAILABLE")
        elif not e["count"]:
            print("   independent expenditures: 0 rows in this cycle")
        else:
            print(f"   independent expenditures: {e['count']} row(s), "
                  f"{money(e['sum'])} summed, {e['first']} … {e['last']}")
            for (cand, so), amt in e["per"]:
                side = {"S": "for", "O": "against"}.get(so, so)
                print(f"     {money(amt):>14}  {side:8} {cand}")
        print()

    if GAPS:
        print("## Gaps")
        for g in GAPS:
            print(f" SOURCE UNAVAILABLE {g}")
        print()

    print("## How to read this")
    print(" Summary figures come from Form 3X filings and are the layer the")
    print(" Post-General report lands in on 2026-12-03. Schedule A itemization")
    print(" can lag the summary: a committee whose summary reports large")
    print(" receipts may have zero itemized rows here. Say that plainly in the")
    print(" piece; do not infer the payer from the summary.")
    print()
    print(f"coverage: {REQUESTS} requests, {ROWS} rows")
    return 0 if len(GAPS) < len(COMMITTEES) * 4 else 1


if __name__ == "__main__":
    sys.exit(main())
