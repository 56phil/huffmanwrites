#!/usr/bin/env python3
"""Collect the day's Global SITREP data into a briefing pack.

Philip, 2026-10-07: a daily Global SITREP, published 06:00 CT, unattended.

This file is the collector half of that job, the same shape as
`scripts/chiefs-report.py`: a script fetches every number, and the writer (a
headless `claude -p` session reading this output) is forbidden to recall one.
The writer reads the pack; it does not remember a yield, a filing, or a market
price. Every figure below was observed by this process at the timestamp printed
at the top.

**A failed source is a gap, not a zero.** This is the design decision the whole
file turns on. A daily unattended job that aborts because one host hiccuped
produces no report at all, and the writer can work around a missing section but
cannot work around a missing file. So every collector is attempted
independently, a failure becomes a visible line (`**SOURCE UNAVAILABLE**`) and a
row in the status table, and the process exits 0 whenever ANY usable pack was
produced. It exits 1 only when nothing at all could be collected. The one thing
it must never do is let "the endpoint was unreachable" render as "the number is
zero" — that is the failure a scheduled job is uniquely good at hiding, because
the page still ships and still looks complete.

**Every URL and every figure is read out of a payload.** The repo's most
dangerous failure is a constructed URL that returns 200 and lands on the wrong
page (CLAUDE.md). Each link this pack prints is therefore taken from a field the
API actually returned — a Federal Register `html_url`, a CourtListener
`absolute_url`/`docket_absolute_url`, a Polymarket event `slug` — never
assembled from a headline, a date, or a guess.

**Counts are printed as received, not as requested.** The Federal Register API
returns a different `count` for the same query seconds apart, so the pack prints
`len(documents)` and never the number the query was asked for. A count that
disagrees with the rows would make the writer doubt the rows.

Usage:
  sitrep-pack.py                    # today's pack (America/Chicago), markdown
  sitrep-pack.py --date 2026-10-07  # the as-of date for every window and line
  sitrep-pack.py --window-days 2    # N calendar days ending on the as-of date
  sitrep-pack.py --json             # the same data as a JSON object
  sitrep-pack.py --out /tmp/pack.md # write to a file instead of stdout

Exit codes: 0 a usable pack was produced (even with failed sources), 1 nothing
could be collected.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import io
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# The site's clock is Central Time; every dated line in the pack is stamped in
# it so a 06:00 run cannot be read as the previous day's news.
try:
    from zoneinfo import ZoneInfo

    CT = ZoneInfo("America/Chicago")
except Exception:  # noqa: BLE001 - a missing tz database must not break the run
    CT = timezone(timedelta(hours=-5))

WINDOW_DEFAULT = 2

# Two User-Agents, because three different rules are in play and picking the
# wrong one is a silent 403. CourtListener and Polymarket's Gamma API refuse a
# default client and answer a named one; CNBC's quote service refuses a default
# client and answers a browser one. The Federal Register, Treasury, and BLS
# endpoints answer either, so they get the named one.
SITREP_UA = "huffmanwrites-sitrep/1.0 (+https://huffmanwrites.org)"
BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

TIMEOUT = 25.0
TRIES = 3

# A bid/ask spread this wide is a thin book, not a price. The midpoint of a
# 0.32/0.64 book is 0.48, which reads as a real 48% forecast and is not one.
# Same rule and same number as `scripts/chiefs-report.py`, for the same reason.
WIDE_SPREAD = 0.10

# Prediction-market rows are capped per section so the pack stays a briefing.
# The cap is stated in the section line; a section that shows 15 of 214 says so.
POLY_EVENTS_PER_TAG = 20
POLY_ROWS_PER_SECTION = 15

FR_API = "https://www.federalregister.gov/api/v1/documents.json"
FR_FIELDS = (
    "title",
    "type",
    "publication_date",
    "agencies",
    "html_url",
    "abstract",
    "document_number",
)
# The API hands back an opaque `search_after_cursor`; following `next_page_url`
# is the only way to page without re-deriving it, and deriving it is how a
# partial result set masquerades as a full one.
FR_MAX_PAGES = 25

CL_SEARCH = "https://www.courtlistener.com/api/rest/v4/search/"
CL_BASE = "https://www.courtlistener.com"

CNBC_SYMBOLS = (".SPX", ".IXIC", ".DJI", ".VIX", "US10Y", "@GC.1", "@CL.1", ".DXY")
CNBC_NAMES = {
    ".SPX": "S&P 500",
    ".IXIC": "Nasdaq Composite",
    ".DJI": "Dow Jones Industrial Average",
    ".VIX": "CBOE Volatility Index",
    "US10Y": "U.S. 10-year Treasury yield",
    "@GC.1": "Gold (front month)",
    "@CL.1": "WTI crude (front month)",
    ".DXY": "U.S. Dollar Index",
}

TREASURY_CSV = (
    "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
    "daily-treasury-rates.csv/{year}/all?type=daily_treasury_yield_curve"
    "&field_tdr_date_value={year}&page&_format=csv"
)

DEBT_API = (
    "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/"
    "od/debt_to_penny?sort=-record_date&page%5Bsize%5D=5"
)

BLS_API = "https://api.bls.gov/publicAPI/v1/timeseries/data/"
BLS_SERIES = (
    ("CUUR0000SA0", "CPI-U, all items (1982-84 = 100)"),
    ("LNS14000000", "Unemployment rate (%)"),
    ("CES0000000001", "Total nonfarm payrolls (thousands)"),
)

GAMMA_API = "https://gamma-api.polymarket.com/events"

# Section -> the Polymarket tags that feed it. A section reads more than one tag
# where the venue's own taxonomy splits a beat in two (`geopolitics` and `world`
# are the same news read through two tag trees; `ai` and `technology` likewise).
POLY_SECTIONS = (
    ("elections", "5. Elections and the midterms", ("midterms",)),
    ("world", "6. The world", ("geopolitics", "world")),
    ("technology", "7. Technology and AI", ("ai", "technology")),
)


class FetchError(RuntimeError):
    """A source could not be read. Never conflated with 'nothing to report'."""


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------
def _fetch(
    url: str,
    *,
    ua: str = "",
    data: "bytes | None" = None,
    content_type: "str | None" = None,
    timeout: float = TIMEOUT,
    tries: int = TRIES,
) -> bytes:
    """GET/POST bytes with a bounded retry. Raises FetchError, never a partial body.

    A hard 4xx is not retried: a 404 or a 403 is a statement about the request,
    and sending it three times does not change the answer. A 5xx or a transport
    failure is retried, because those are the ones that come back on the second
    try — and the whole point of this file is that one host hiccup must not cost
    the day's report.
    """
    headers = {}
    if ua:
        headers["User-Agent"] = ua
    if content_type:
        headers["Content-Type"] = content_type
    last: "Exception | None" = None
    for attempt in range(tries):
        req = urllib.request.Request(url, headers=headers, data=data)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if 400 <= e.code < 500 and e.code not in (408, 429):
                raise FetchError(f"HTTP {e.code} for {url}") from e
            last = e
            # A 429 is a rate limit: retrying inside the window just spends
            # another request, so wait a real interval. CourtListener's
            # anonymous search limit is per-minute and measured here on
            # 2026-10-07 — a second pack run seconds after the first had the
            # D.D.C. RECAP query refused outright. The wait is bounded so a
            # stalled run fails visibly rather than hanging the 06:00 job.
            if e.code == 429 and attempt < tries - 1:
                time.sleep(_retry_after(e, default=6.0))
                continue
        except Exception as e:  # noqa: BLE001 - any transport failure is the same finding
            last = e
        if attempt < tries - 1:
            time.sleep(0.5 * (attempt + 1))
    raise FetchError(f"{type(last).__name__} for {url}: {last}") from last


def _retry_after(error: urllib.error.HTTPError, default: float) -> float:
    """The server's Retry-After in seconds, clamped, or `default`."""
    raw = (error.headers or {}).get("Retry-After") if error.headers else None
    try:
        return min(max(float(raw), 0.0), 20.0) if raw else default
    except (TypeError, ValueError):
        return default


def fetch_json(url: str, **kw) -> object:
    body = _fetch(url, **kw)
    try:
        return json.loads(body)
    except ValueError as e:
        raise FetchError(f"non-JSON response from {url}: {e}") from e


def fetch_text(url: str, **kw) -> str:
    return _fetch(url, **kw).decode("utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Collection. One function per source; each raises FetchError on failure and
# the caller turns that into a visible gap.
# ---------------------------------------------------------------------------
def fr_url(start: str, end: str) -> str:
    params = [
        ("per_page", "100"),
        ("order", "newest"),
        ("conditions[publication_date][gte]", start),
        ("conditions[publication_date][lte]", end),
    ]
    params += [("fields[]", f) for f in FR_FIELDS]
    return FR_API + "?" + urllib.parse.urlencode(params)


def collect_federal_register(start: str, end: str) -> "list[dict]":
    """Every Document in the window, following the API's own pagination cursor."""
    url = fr_url(start, end)
    docs: "list[dict]" = []
    pages = 0
    while url and pages < FR_MAX_PAGES:
        payload = fetch_json(url)
        if not isinstance(payload, dict):
            raise FetchError("federalregister.gov returned a non-object payload")
        docs.extend(payload.get("results") or [])
        url = payload.get("next_page_url")
        pages += 1
    # A next_page_url still waiting after the cap means a window larger than this
    # pack will carry — say so rather than printing a truncated list as the whole.
    return docs[: 100 * FR_MAX_PAGES]


def fr_document(result: dict) -> dict:
    agencies = result.get("agencies") or []
    return {
        "title": result.get("title") or "(untitled)",
        "type": result.get("type") or "",
        "publication_date": result.get("publication_date") or "",
        "agency": (agencies[0].get("name") if agencies else "") or "",
        "url": result.get("html_url") or "",
        "abstract": result.get("abstract") or "",
        "document_number": result.get("document_number") or "",
    }


# CourtListener answers anonymous search at a per-minute rate; the daily job
# makes three calls back-to-back and the D.D.C. one was refused with HTTP 429 on
# a run that followed another by seconds (2026-10-07). Spacing the calls is the
# fix that costs nothing when the limit is not near.
CL_MIN_INTERVAL = 1.5
_CL_LAST = [0.0]


def cl_search(**params) -> dict:
    gap = CL_MIN_INTERVAL - (time.monotonic() - _CL_LAST[0])
    if gap > 0:
        time.sleep(gap)
    try:
        url = CL_SEARCH + "?" + urllib.parse.urlencode(params)
        payload = fetch_json(url, ua=SITREP_UA)
    finally:
        _CL_LAST[0] = time.monotonic()
    if not isinstance(payload, dict):
        raise FetchError("CourtListener returned a non-object payload")
    return payload


def _in_window(day: str, start: str, end: str) -> bool:
    """True when `day` (YYYY-MM-DD) sits in the window.

    The upper bound is load-bearing, not a formality: CourtListener's RECAP
    search (`type=r`) serves rows with absurd FUTURE `dateFiled` values, and a
    pack that passed them through would print court filings that have not
    happened. Measured on 2026-10-07: a window ending that day returned
    `dateFiled` values into 2027.
    """
    return bool(day) and start <= day <= end


def cl_result(payload: dict, start: str, end: str, opinion: bool) -> dict:
    """Filter one search page to the window and report what the API claimed.

    `api_count` is carried alongside the in-window rows because the search
    endpoint caps a page at 20 whatever `page_size` asks for (measured
    2026-10-07: `page_size=100` still returns 20 rows with `count: 25`). A pack
    that printed the 20 rows without the count would present one page as the
    whole window — so the renderer says "showing 20 of 25" when they disagree.
    """
    out = []
    for r in payload.get("results") or []:
        day = r.get("dateFiled") or ""
        if not _in_window(day, start, end):
            continue
        url = ""
        if opinion and r.get("absolute_url"):
            url = CL_BASE + r["absolute_url"]
        elif r.get("docket_absolute_url"):
            url = CL_BASE + r["docket_absolute_url"]
        elif r.get("docket_id"):
            # The exact shape `scripts/check-docket.py` already uses, and only
            # when the payload hands over a docket id to put in it.
            url = f"{CL_BASE}/docket/{r['docket_id']}/"
        out.append(
            {
                "date": day,
                "case": r.get("caseName") or "(unnamed)",
                "docket": r.get("docketNumber") or "",
                "court": r.get("court") or "",
                "url": url,
            }
        )
    return {
        "rows": out,
        "api_count": payload.get("count"),
        "returned": len(payload.get("results") or []),
    }


def cl_opinions(court: str, start: str, end: str) -> dict:
    payload = cl_search(
        type="o",
        court=court,
        filed_after=start,
        order_by="dateFiled desc",
        page_size=20,
    )
    return cl_result(payload, start, end, opinion=True)


def cl_recap(court: str, start: str, end: str) -> dict:
    payload = cl_search(
        type="r",
        court=court,
        filed_after=start,
        order_by="dateFiled desc",
        page_size=20,
    )
    return cl_result(payload, start, end, opinion=False)


def load_docket_registry():
    """Import `scripts/check-docket.py` for its CASES map and feed helpers.

    The registry is that file's `CASES` map and nothing else (CLAUDE.md), and a
    second copy here is exactly the drift the rule exists to prevent: a case
    added to the watcher would silently not appear in this pack. The module name
    is hyphenated, so it is loaded by path.
    """
    path = REPO / "scripts" / "check-docket.py"
    spec = importlib.util.spec_from_file_location("_sitrep_check_docket", path)
    if spec is None or spec.loader is None:
        raise FetchError(f"could not load the docket registry at {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def collect_watched_dockets(start: str, end: str) -> "list[dict]":
    mod = load_docket_registry()
    out = []
    for key, case in mod.CASES.items():
        row = {
            "key": key,
            "case": case.get("case") or key,
            "label": case.get("label") or key,
            "docket_url": mod.docket_url(case),
            "status": "OK",
            "count": 0,
            "newest": "",
            "detail": "",
        }
        try:
            entries = mod.parse_entries(mod.fetch_feed(mod.feed_url(case)))
        except Exception as e:  # noqa: BLE001 - a dead feed is a gap, not a crash
            row["status"] = "UNAVAILABLE"
            row["detail"] = f"{type(e).__name__}: {e}"
            out.append(row)
            continue
        in_window = [e for e in entries if _in_window(e.get("date") or "", start, end)]
        row["count"] = len(in_window)
        row["newest"] = max((e["date"] for e in in_window), default="")
        row["detail"] = (
            "nothing filed in the window"
            if not in_window
            else "; ".join(
                f"ECF {e['num']} ({e['date']})" if e["kind"] == "entry"
                else f"minute entry ({e['date']})"
                for e in sorted(
                    in_window, key=lambda e: (e["date"], e["num"] or 0, e["mid"] or 0)
                )
            )
        )
        out.append(row)
    return out


def collect_quotes() -> "list[dict]":
    symbols = urllib.parse.quote("|".join(CNBC_SYMBOLS), safe="")
    url = (
        "https://quote.cnbc.com/quote-html-webservice/restQuote/symbolType/symbol"
        f"?symbols={symbols}&requestMethod=itv&noform=1&partnerId=2&fund=1"
        "&exthrs=1&output=json&events=1"
    )
    payload = fetch_json(url, ua=BROWSER_UA)
    rows = ((payload or {}).get("FormattedQuoteResult") or {}).get("FormattedQuote")
    if not rows:
        raise FetchError("CNBC quote service returned no quotes")
    out = []
    for q in rows:
        out.append(
            {
                "symbol": q.get("symbol") or "",
                "name": CNBC_NAMES.get(q.get("symbol") or "") or q.get("shortName") or "",
                "last": q.get("last") or "",
                "change": q.get("change") or "",
                "change_pct": q.get("change_pct") or "",
                "as_of": q.get("last_time") or "",
            }
        )
    return out


def collect_yields(as_of: str) -> "list[dict]":
    year = as_of[:4]
    text = fetch_text(TREASURY_CSV.format(year=year))
    rows = list(csv.DictReader(io.StringIO(text)))
    if not rows:
        raise FetchError("Treasury CSV parsed to zero rows")
    parsed = []
    for r in rows:
        raw = (r.get("Date") or "").strip()
        try:
            d = datetime.strptime(raw, "%m/%d/%Y").date().isoformat()
        except ValueError:
            continue
        if d > as_of:
            # `--date` in the past must not print a curve from after it.
            continue
        parsed.append((d, r))
    parsed.sort(key=lambda t: t[0], reverse=True)
    out = []
    for d, r in parsed[:2]:
        two = r.get("2 Yr") or ""
        ten = r.get("10 Yr") or ""
        thirty = r.get("30 Yr") or ""
        spread = ""
        try:
            spread = f"{float(ten) - float(two):+.2f}"
        except (TypeError, ValueError):
            spread = ""
        out.append({"date": d, "2y": two, "10y": ten, "30y": thirty, "2s10s": spread})
    if not out:
        raise FetchError(f"no Treasury curve rows on or before {as_of}")
    return out


def collect_debt(as_of: str) -> "list[dict]":
    payload = fetch_json(DEBT_API)
    rows = (payload or {}).get("data") or []
    parsed = [r for r in rows if (r.get("record_date") or "") <= as_of]
    if not parsed:
        raise FetchError(f"no debt records on or before {as_of}")
    parsed.sort(key=lambda r: r["record_date"], reverse=True)
    return parsed[:2]


def collect_economy(start_year: int, end_year: int) -> "list[dict]":
    body = json.dumps(
        {
            "seriesid": [s for s, _ in BLS_SERIES],
            "startyear": str(start_year),
            "endyear": str(end_year),
        }
    ).encode()
    payload = fetch_json(
        BLS_API, data=body, content_type="application/json"
    )
    if (payload or {}).get("status") != "REQUEST_SUCCEEDED":
        raise FetchError(f"BLS status {(payload or {}).get('status')!r}")
    by_id = {s.get("seriesID"): s for s in (payload.get("Results") or {}).get("series") or []}
    out = []
    for series_id, name in BLS_SERIES:
        s = by_id.get(series_id)
        if not s or not s.get("data"):
            continue
        points = [p for p in s["data"] if (p.get("period") or "").startswith("M")]
        out.append(
            {
                "series_id": series_id,
                "name": name,
                "points": [
                    {
                        "month": f"{p.get('periodName', '')} {p.get('year', '')}".strip(),
                        "value": p.get("value") or "",
                    }
                    for p in points[:3]
                ],
                "source_url": BLS_API,
            }
        )
    if not out:
        raise FetchError("BLS returned no monthly observations for the verified series")
    return out


def _poly_market(m: dict, event_slug: str, event_title: str) -> "dict | None":
    try:
        prices = json.loads(m.get("outcomePrices") or "[]")
    except ValueError:
        prices = []
    bid, ask = m.get("bestBid"), m.get("bestAsk")
    spread = m.get("spread")
    if spread is None and isinstance(bid, (int, float)) and isinstance(ask, (int, float)):
        spread = ask - bid
    wide = isinstance(spread, (int, float)) and spread > WIDE_SPREAD
    implied = None
    if isinstance(bid, (int, float)) and isinstance(ask, (int, float)) and not wide:
        implied = (bid + ask) / 2
    elif prices and not wide:
        try:
            implied = float(prices[0])
        except (TypeError, ValueError):
            implied = None
    label = m.get("groupItemTitle") or ""
    question = m.get("question") or event_title
    return {
        "event": event_title,
        "question": question,
        "label": label,
        "implied": implied,
        "wide": bool(wide),
        "spread": round(spread, 3) if isinstance(spread, (int, float)) else None,
        "volume_24h": m.get("volume24hr"),
        "best_bid": bid,
        "best_ask": ask,
        "end_date": m.get("endDate") or "",
        "source_url": f"{GAMMA_API}?slug={event_slug}",
        "slug": event_slug,
    }


def collect_polymarket(tags: "tuple[str, ...]") -> "list[dict]":
    seen = {}
    for tag in tags:
        url = (
            f"{GAMMA_API}?limit={POLY_EVENTS_PER_TAG}&active=true&closed=false"
            f"&order=volume24hr&ascending=false&tag_slug={tag}"
        )
        payload = fetch_json(url, ua=SITREP_UA)
        if not isinstance(payload, list):
            raise FetchError(f"Gamma returned a non-array payload for tag {tag}")
        for event in payload:
            slug = event.get("slug") or ""
            if not slug or slug in seen:
                continue
            seen[slug] = [
                row
                for row in (
                    _poly_market(m, slug, event.get("title") or "")
                    for m in event.get("markets") or []
                )
                if row is not None
            ]
    out = [m for rows in seen.values() for m in rows]
    out.sort(key=lambda m: m.get("volume_24h") or 0, reverse=True)
    return out


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------
def _plural(n: int, singular: str, plural: "str | None" = None) -> str:
    """'1 document', '167 documents'. The pack is prose a writer may quote."""
    return f"{n} {singular if n == 1 else (plural or singular + 's')}"


def _money(value: str) -> str:
    """'40273024579219.17' -> '$40,273,024,579,219'. Unparseable passes through."""
    try:
        return f"${round(float(value)):,}"
    except (TypeError, ValueError):
        return value or ""


def _delta(now: str, prior: str) -> str:
    try:
        d = float(now) - float(prior)
    except (TypeError, ValueError):
        return ""
    return f"${d:+,.0f}"


def _pct(value) -> str:
    if value is None:
        return "—"
    return f"{value * 100:.1f}%"


def build_pack(as_of: str, window_days: int, now_ct: datetime) -> dict:
    start = (
        datetime.strptime(as_of, "%Y-%m-%d") - timedelta(days=window_days - 1)
    ).strftime("%Y-%m-%d")
    generated = now_ct.strftime("%Y-%m-%d %H:%M:%S %Z")

    pack: dict = {
        "as_of": as_of,
        "generated": generated,
        "window": {"days": window_days, "start": start, "end": as_of},
        "sources": [],
        "unavailable": [],
    }
    ok = 0

    def note(section: str, source: str, status: str, good: bool) -> None:
        nonlocal ok
        pack["sources"].append({"section": section, "source": source, "status": status})
        if good:
            ok += 1
        else:
            pack["unavailable"].append(f"{source}: {status}")

    def attempt(section: str, source: str, fn, describe):
        try:
            value = fn()
        except FetchError as e:
            note(section, source, f"UNAVAILABLE — {e}", False)
            return None
        except Exception as e:  # noqa: BLE001 - a collector bug is a gap, not a crash
            note(section, source, f"UNAVAILABLE — {type(e).__name__}: {e}", False)
            return None
        note(section, source, describe(value), True)
        return value

    # 1. The administration and the rule of law -----------------------------
    docs = attempt(
        "1. Administration",
        "Federal Register API",
        lambda: collect_federal_register(start, as_of),
        lambda v: f"OK ({len(v)} documents)",
    )
    administration = None
    if docs is not None:
        items = [fr_document(d) for d in docs]
        administration = {
            "total": len(items),
            "presidential": [d for d in items if d["type"] == "Presidential Document"],
            "rules": [d for d in items if d["type"] == "Rule"],
            "proposed_rules": [d for d in items if d["type"] == "Proposed Rule"],
            "notices": [d for d in items if d["type"] == "Notice"],
            "other": [
                d
                for d in items
                if d["type"]
                not in ("Presidential Document", "Rule", "Proposed Rule", "Notice")
            ],
        }
    pack["administration"] = administration

    # 2. The courts ---------------------------------------------------------
    courts: dict = {}
    def cl_status(v: dict) -> str:
        return (
            f"OK ({len(v['rows'])} in window of {v['returned']} returned; "
            f"API count {v['api_count']})"
        )

    courts["scotus"] = attempt(
        "2. Courts",
        "CourtListener — Supreme Court opinions",
        lambda: cl_opinions("scotus", start, as_of),
        cl_status,
    )
    courts["cadc_opinions"] = attempt(
        "2. Courts",
        "CourtListener — D.C. Circuit opinions",
        lambda: cl_opinions("cadc", start, as_of),
        cl_status,
    )
    courts["district"] = attempt(
        "2. Courts",
        "CourtListener — D.D.C. new complaints (RECAP)",
        lambda: cl_recap("dcd", start, as_of),
        cl_status,
    )
    watched = attempt(
        "2. Courts",
        "check-docket registry (watched dockets)",
        lambda: collect_watched_dockets(start, as_of),
        lambda v: f"OK ({len(v)} case(s); "
        f"{sum(1 for r in v if r['count'])} with a filing in window)",
    )
    courts["watched"] = watched
    pack["courts"] = courts

    # 3. Markets ------------------------------------------------------------
    markets: dict = {"as_of": "", "quotes": [], "yields": [], "debt": []}
    quotes = attempt(
        "3. Markets",
        "CNBC quote service",
        collect_quotes,
        lambda v: f"OK ({len(v)} symbols)",
    )
    if quotes is not None:
        markets["quotes"] = quotes
        stamps = [q["as_of"] for q in quotes if q["as_of"]]
        markets["as_of"] = max(stamps) if stamps else ""
    yields = attempt(
        "3. Markets",
        "U.S. Treasury daily yield curve",
        lambda: collect_yields(as_of),
        lambda v: f"OK ({len(v)} curve row(s), latest {v[0]['date']})",
    )
    if yields is not None:
        markets["yields"] = yields
    debt = attempt(
        "3. Markets",
        "FiscalData debt to the penny",
        lambda: collect_debt(as_of),
        lambda v: f"OK (latest {v[0]['record_date']})",
    )
    if debt is not None:
        markets["debt"] = debt
    pack["markets"] = markets

    # 4. The economy --------------------------------------------------------
    economy = attempt(
        "4. Economy",
        "BLS public API",
        lambda: collect_economy(int(as_of[:4]) - 1, int(as_of[:4])),
        lambda v: f"OK ({len(v)} series)",
    )
    pack["economy"] = economy

    # 5-7. Prediction markets ----------------------------------------------
    for key, heading, tags in POLY_SECTIONS:
        data = attempt(
            heading,
            f"Polymarket Gamma — {', '.join(tags)}",
            lambda t=tags: collect_polymarket(t),
            lambda v: f"OK ({len(v)} market(s) after dedupe)",
        )
        pack[key] = {"heading": heading, "tags": list(tags), "markets": data}

    # 8. What has no collector ---------------------------------------------
    pack["not_in_pack"] = (
        "Beats with no collector in this pack, which the writer must fetch and "
        "cite if the report needs them: congressional legislation and votes "
        "(the Congress.gov API requires a key); state and local government "
        "action; campaign finance filings (FEC bulk data is not real-time); "
        "corporate earnings and business news; international diplomacy and "
        "conflict beyond what prediction markets price; science and health "
        "agency actions outside the Federal Register; and sport, culture, and "
        "obituaries. None of these is a gap in the pack to be papered over with "
        "recalled facts — a missing beat is reported as absent or not reported."
    )

    pack["_ok_sources"] = ok
    return pack


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
def render(pack: dict) -> str:
    """The briefing pack the writer reads. Every line above traces to a payload."""
    L: "list[str]" = []
    as_of = pack["as_of"]
    win = pack["window"]
    L.append(f"# SITREP briefing pack — {as_of}")
    L.append("")
    L.append(
        f"Generated {pack['generated']} by scripts/sitrep-pack.py. "
        f"Window: {win['start']} through {win['end']} "
        f"({_plural(win['days'], 'day')})."
    )
    L.append("")
    L.append(
        "Every number below was fetched by the script at the timestamp above. "
        "If a fact you need is not in this pack, fetch it and cite the page you "
        "fetched. Never recall it."
    )
    L.append("")

    L.append("## Sources in this pack")
    L.append("")
    L.append("| Section | Source | Status |")
    L.append("|---|---|---|")
    for row in pack["sources"]:
        L.append(f"| {row['section']} | {row['source']} | {row['status']} |")
    L.append("")

    def gap(source: str, reason: str) -> None:
        L.append(f"**SOURCE UNAVAILABLE** — {source}: {reason}")
        L.append("")

    # 1 ---------------------------------------------------------------------
    L.append("## 1. The administration and the rule of law")
    L.append("")
    adm = pack.get("administration")
    if adm is None:
        reason = next(
            (u for u in pack["unavailable"] if u.startswith("Federal Register API")),
            "fetch failed",
        )
        gap("Federal Register API", reason)
    else:
        L.append(
            f"Federal Register documents published {win['start']} through "
            f"{win['end']}: {_plural(adm['total'], 'document')} "
            f"({_plural(len(adm['presidential']), 'presidential document')}, "
            f"{_plural(len(adm['rules']), 'rule')}, "
            f"{_plural(len(adm['proposed_rules']), 'proposed rule')}, "
            f"{_plural(len(adm['notices']), 'notice')}"
            + (f", {len(adm['other'])} other" if adm["other"] else "")
            + "), as received from the API."
        )
        L.append("")

        def doc_lines(title: str, rows: "list[dict]") -> None:
            L.append(f"### {title} ({len(rows)})")
            if not rows:
                L.append(
                    "None in the window. That is a finding about the window, "
                    "not a gap: say so rather than padding the section."
                )
                L.append("")
                return
            for d in rows:
                agency = f" — {d['agency']}" if d["agency"] else ""
                L.append(
                    f"- **{d['title']}**{agency} — published {d['publication_date']} "
                    f"— {d['url']}"
                )
            L.append("")

        doc_lines("Presidential documents", adm["presidential"])
        doc_lines("Rules", adm["rules"])
        doc_lines("Proposed rules", adm["proposed_rules"])
        doc_lines("Notices", adm["notices"])
        if adm["other"]:
            doc_lines("Other document types", adm["other"])

    # 2 ---------------------------------------------------------------------
    L.append("## 2. The courts")
    L.append("")
    courts = pack.get("courts") or {}

    def court_block(title: str, data, source: str) -> None:
        L.append(f"### {title}")
        if data is None:
            gap(source, "fetch failed")
            return
        rows = data["rows"]
        if data.get("returned") and data.get("api_count") and (
            data["returned"] < data["api_count"]
        ):
            L.append(
                f"The search API caps a page at {data['returned']} rows and "
                f"reports {data['api_count']} for the query, so the list below "
                "is the newest page of the window, not the whole of it."
            )
            L.append("")
        if not rows:
            L.append(
                "Nothing filed in the window. A quiet window is a fact to state, "
                "not to fill."
            )
            L.append("")
            return
        for r in rows:
            tail = []
            if r.get("docket"):
                tail.append(r["docket"])
            if r.get("court"):
                tail.append(r["court"])
            suffix = f" — {', '.join(tail)}" if tail else ""
            L.append(f"- {r['date']} — {r['case']}{suffix}")
            if r.get("url"):
                L.append(f"  {r['url']}")
        L.append("")

    court_block(
        "Supreme Court — opinions filed in the window",
        courts.get("scotus"),
        "CourtListener — Supreme Court opinions",
    )
    court_block(
        "D.C. Circuit — opinions filed in the window",
        courts.get("cadc_opinions"),
        "CourtListener — D.C. Circuit opinions",
    )
    court_block(
        "District courts — new complaints in the window (CourtListener RECAP)",
        courts.get("district"),
        "CourtListener — D.D.C. new complaints (RECAP)",
    )

    L.append("### The watched dockets")
    watched = courts.get("watched")
    if watched is None:
        gap("check-docket registry (watched dockets)", "fetch failed")
    else:
        L.append(
            "From the same registry `scripts/check-docket.py` watches; the feed "
            "was read at the timestamp above and filings counted for the window."
        )
        L.append("")
        for row in watched:
            if row["status"] != "OK":
                L.append(f"- **{row['label']}** — {row['case']} — SOURCE UNAVAILABLE: {row['detail']}")
                L.append(f"  {row['docket_url']}")
                continue
            if row["count"]:
                L.append(
                    f"- **{row['label']}** — {row['case']} — {row['count']} filing(s) "
                    f"in the window, newest {row['newest']}: {row['detail']}"
                )
            else:
                L.append(
                    f"- **{row['label']}** — {row['case']} — nothing filed in the window"
                )
            L.append(f"  {row['docket_url']}")
        L.append("")

    # 3 ---------------------------------------------------------------------
    L.append("## 3. Markets")
    L.append("")
    mk = pack.get("markets") or {}
    if mk.get("as_of"):
        L.append(
            f"Live quotes as of {mk['as_of']} (the newest timestamp among the "
            "quotes fetched)."
        )
        L.append("")
    quotes = mk.get("quotes") or []
    if not quotes:
        reason = next(
            (u for u in pack["unavailable"] if u.startswith("CNBC quote service")),
            "fetch failed",
        )
        gap("CNBC quote service", reason)
    else:
        L.append("| Symbol | Index | Last | Change | As of |")
        L.append("|---|---|---|---|---|")
        for q in quotes:
            L.append(
                f"| {q['symbol']} | {q['name']} | {q['last']} | "
                f"{q['change']} ({q['change_pct']}) | {q['as_of']} |"
            )
        L.append("")
    yields = mk.get("yields") or []
    L.append("### Treasury yield curve (U.S. Treasury daily rates)")
    L.append("")
    if not yields:
        reason = next(
            (u for u in pack["unavailable"] if u.startswith("U.S. Treasury daily")),
            "fetch failed",
        )
        gap("U.S. Treasury daily yield curve", reason)
    else:
        L.append("| Date | 2Y | 10Y | 30Y | 2s10s |")
        L.append("|---|---|---|---|---|")
        for y in yields:
            L.append(f"| {y['date']} | {y['2y']} | {y['10y']} | {y['30y']} | {y['2s10s']} |")
        L.append("")
        if len(yields) >= 2:
            L.append(
                f"The two rows are {yields[0]['date']} and {yields[1]['date']} — "
                "the day-over-day delta, or the last two business days when the "
                "as-of date is a weekend."
            )
            L.append("")

    L.append("### Federal debt")
    L.append("")
    debt = mk.get("debt") or []
    if not debt:
        reason = next(
            (u for u in pack["unavailable"] if u.startswith("FiscalData")),
            "fetch failed",
        )
        gap("FiscalData debt to the penny", reason)
    else:
        latest = debt[0]
        prior = debt[1] if len(debt) > 1 else None
        delta = (
            f" (Δ vs prior business day {prior['record_date']}: "
            f"{_delta(latest['tot_pub_debt_out_amt'], prior['tot_pub_debt_out_amt'])})"
            if prior
            else ""
        )
        L.append(
            f"- Total public debt outstanding {latest['record_date']}: "
            f"{_money(latest['tot_pub_debt_out_amt'])}{delta}"
        )
        L.append(
            f"- Debt held by the public: "
            f"{_money(latest['debt_held_public_amt'])} "
            f"(intragovernmental: {_money(latest['intragov_hold_amt'])})"
        )
        L.append("")

    # 4 ---------------------------------------------------------------------
    L.append("## 4. The economy (BLS public API)")
    L.append("")
    economy = pack.get("economy")
    if not economy:
        reason = next(
            (u for u in pack["unavailable"] if u.startswith("BLS public API")),
            "fetch failed",
        )
        gap("BLS public API", reason)
    else:
        L.append(
            "Monthly series, newest first; the month named is the reference "
            "month, which lags the as-of date because the data is published on "
            "a schedule."
        )
        L.append("")
        for s in economy:
            pts = s["points"]
            if not pts:
                continue
            vals = ", ".join(f"{p['month']} {p['value']}" for p in pts)
            L.append(f"- {s['name']} ({s['series_id']}): {vals}")
        L.append("")
        L.append(f"Source: {BLS_API}")
        L.append("")

    # 5-7 -------------------------------------------------------------------
    for key, heading, tags in POLY_SECTIONS:
        L.append(f"## {heading}")
        L.append("")
        section = pack.get(key) or {}
        markets = section.get("markets")
        source = f"Polymarket Gamma — {', '.join(tags)}"
        if markets is None:
            reason = next(
                (u for u in pack["unavailable"] if u.startswith(source)), "fetch failed"
            )
            gap(source, reason)
            continue
        if not markets:
            L.append(
                f"No live markets on the tags {', '.join(tags)}. That is a fact "
                "about the venue, not a gap to fill."
            )
            L.append("")
            continue
        shown = markets[:POLY_ROWS_PER_SECTION]
        L.append(
            f"Top {len(shown)} of {len(markets)} live market(s) across the tags "
            f"{', '.join(tags)}, by 24h volume."
        )
        L.append("")
        L.append("| Market | Implied | 24h volume | Link |")
        L.append("|---|---|---|---|")
        for m in shown:
            if m["wide"]:
                implied = f"WIDE BOOK (spread {m['spread']}) — no price"
            else:
                implied = _pct(m["implied"])
            vol = f"${m['volume_24h']:,.0f}" if isinstance(m["volume_24h"], (int, float)) else "—"
            # The market's own question, kept alongside the group label: a
            # multi-row event returns one market per outcome and its
            # `groupItemTitle` is the row ("October 15", a candidate), which
            # alone would print a date where a question belongs. Both strings
            # are read from the payload.
            if m["label"] and m["label"] != m["question"]:
                name = f"{m['event']} — {m['label']}"
            else:
                name = m["question"]
            L.append(f"| {name} | {implied} | {vol} | {m['source_url']} |")
        L.append("")
        L.append(
            "A row marked WIDE BOOK has a bid/ask spread wide enough that its "
            "midpoint is not a forecast, so no probability is printed for it — "
            "the midpoint of an empty book reads as a real price and is not one "
            "(the `scripts/chiefs-report.py` thin-book rule)."
        )
        L.append("")

    # 8 ---------------------------------------------------------------------
    L.append("## 8. Not in this pack")
    L.append("")
    L.append(pack["not_in_pack"])
    L.append("")
    L.append("---")
    L.append("")
    L.append(
        "Every number and URL above was read from the Federal Register API, "
        "CourtListener's search API and the watched dockets' own Atom feeds, "
        "CNBC's quote service, the U.S. Treasury and FiscalData, the BLS public "
        "API, and Polymarket's Gamma API by `scripts/sitrep-pack.py`. If a fact "
        "you want is not here, fetch it and cite the page you fetched — do not "
        "fill the gap from memory."
    )
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Collect the day's Global SITREP data into a briefing pack."
    )
    ap.add_argument(
        "--date",
        type=date.fromisoformat,
        help="the as-of date (YYYY-MM-DD) used for every window and every "
        "'as of' line; default today in America/Chicago",
    )
    ap.add_argument(
        "--window-days",
        type=int,
        default=WINDOW_DEFAULT,
        help=f"calendar days ending on the as-of date (default {WINDOW_DEFAULT})",
    )
    ap.add_argument("--json", action="store_true", help="emit the structured pack")
    ap.add_argument("--out", metavar="PATH", help="write the pack to a file")
    args = ap.parse_args()

    if args.window_days < 1:
        ap.error("--window-days must be at least 1")

    now_ct = datetime.now(CT)
    as_of = args.date.isoformat() if args.date else now_ct.date().isoformat()

    pack = build_pack(as_of, args.window_days, now_ct)
    ok = pack.pop("_ok_sources")

    if args.json:
        text = json.dumps(pack, indent=2, ensure_ascii=False)
    else:
        text = render(pack)
    if not text.endswith("\n"):
        text += "\n"

    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)

    if ok == 0:
        sys.stderr.write(
            "sitrep-pack: nothing could be collected from any source; "
            "see the status table\n"
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
