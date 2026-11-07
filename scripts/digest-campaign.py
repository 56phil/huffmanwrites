#!/usr/bin/env python3
"""Guard the newsletter send: is the letter actually scheduled?

Why this exists. 2026-11-07: the page released on time at 05:53 CT, the letter
was written and reviewed, and no email arrived, because **nothing was ever
scheduled**. The release job owns the page; no job, script or plist owns the
campaign. Preparing a letter by hand therefore ended with "the send waits on
Philip", which is a dependency on someone being awake at 06:00 on a Saturday,
and on the one morning nobody was, the letter reached the site and no inbox.

The fix is two verbs and one of them runs at prep time:

    python3 scripts/digest-campaign.py --schedule --file pending/<draft>.md \
        --slug stoic-saturday-<phrase>
    python3 scripts/digest-campaign.py --check --date <Saturday>

`--schedule` renders the email body with `scripts/digest-email.py`, creates the
campaign and sets its `scheduled_at`, so SendFox's own scheduler sends it at
06:00 CT whether or not anyone is at the machine. It is idempotent: a campaign
that already exists for that subject is reported, not duplicated. `--check`
asks SendFox whether a campaign exists for a letter dated that day, and exits 3
when none does, which is the state that produced this file.

Exit codes: 0 for a scheduled or already-sent campaign (and for `--schedule`
succeeding); 2 when no letter exists for the date asked about, which is not a
failure; 3 when a letter exists and nothing will send it.

The SendFox API sits behind Cloudflare, which answers a plain urllib client
with **HTTP 403 error code 1010**. Every request here sends a browser
User-Agent, the same lesson `check-secrets.py` carries for `/lists`.

The token is read through `check-secrets.py`'s registry so this file cannot
acquire a second idea of where the SendFox key lives. It is never printed.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SECTION = REPO / "content" / "posts" / "digests"
API = "https://api.sendfox.com"
CREDENTIAL = "SENDFOX_CLIENT_SECRET"
LIST_PRIMARY = 639865
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128 Safari/537.36")
FRONTMATTER_FIELD = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$")


class SendFoxError(RuntimeError):
    """The API answered with something other than the object asked for."""


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def resolve_token() -> "str | None":
    """The SendFox key, from the keychain first and ~/.secrets second."""
    cs = _load("check_secrets", REPO / "scripts" / "check-secrets.py")
    cred = next((c for c in cs.CREDENTIALS if c["name"] == CREDENTIAL), None)
    if cred is None:
        return None
    homes = cs.resolve_homes(cred)
    for value in homes.values():
        if value:
            return value
    return None


def api(token: str, method: str, path: str, payload: "dict | None" = None,
        timeout: float = 60.0) -> dict:
    body = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        API + path, data=body, method=method,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json",
                 "Content-Type": "application/json", "User-Agent": UA})
    try:
        raw = urllib.request.urlopen(request, timeout=timeout).read()
    except urllib.error.HTTPError as e:
        raise SendFoxError(f"{method} {path} answered HTTP {e.code}: "
                           f"{e.read()[:300].decode(errors='replace')}") from None
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise SendFoxError(f"{method} {path} could not be reached ({e})") from None
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except ValueError:
        raise SendFoxError(f"{method} {path} answered something that is not JSON") from None


def campaigns(token: str, limit: int = 100) -> "list[dict]":
    payload = api(token, "GET", f"/campaigns?limit={limit}")
    rows = payload.get("data", payload)
    return rows if isinstance(rows, list) else []


def campaign_for(rows: "list[dict]", subject: str) -> "dict | None":
    """The campaign whose subject is this one, matched exactly.

    Exact rather than fuzzy on purpose: a near match is how a letter gets
    reported as scheduled because last week's did.
    """
    wanted = subject.strip()
    for row in rows:
        if (row.get("subject") or "").strip() == wanted:
            return row
    return None


def will_send(row: "dict | None") -> bool:
    """Whether this campaign has already gone or is going, on SendFox's clock."""
    if not row:
        return False
    return bool(row.get("sent_at") or row.get("scheduled_at")) and not row.get("cancelled_at")


def read_frontmatter(path: Path) -> dict:
    text = path.read_text(errors="replace")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    block = text[3:end if end != -1 else len(text)]
    fields: "dict[str, str]" = {}
    for line in block.splitlines():
        m = FRONTMATTER_FIELD.match(line.strip())
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if value[:1] in ("'", '"') and value[-1:] == value[:1] and len(value) >= 2:
            value = value[1:-1]
        fields[key] = value
    return fields


def letter_for(date: str, section: Path = SECTION) -> "Path | None":
    """The digest whose own frontmatter date falls on `date`."""
    for path in sorted(section.glob("*.md")):
        if path.name.startswith("_"):
            continue
        fields = read_frontmatter(path)
        if (fields.get("date") or "").startswith(date):
            return path
    return None


def subject_for(path: Path) -> str:
    fields = read_frontmatter(path)
    return (fields.get("sendfox_subject") or fields.get("title") or "").strip()


def schedule_moment(date_field: str, hour: int = 6) -> str:
    """06:00 CT on the letter's own day, as SendFox's UTC string.

    Taken from the letter's own offset rather than from today's clock, because
    the letter carries the offset that applies on its date: a hardcoded -05:00
    in November names 07:00 CT and sends an hour late.
    """
    stamp = datetime.fromisoformat(date_field)
    offset = stamp.utcoffset() or timedelta(0)
    local = datetime(stamp.year, stamp.month, stamp.day, hour, 0, 0, tzinfo=timezone(offset))
    return local.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def render_html(draft: Path, slug: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "letter.html"
        result = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "digest-email.py"), str(draft),
             "--slug", slug, "--out", str(out)],
            capture_output=True, text=True)
        if result.returncode != 0 or not out.exists():
            raise SendFoxError("digest-email.py failed: "
                               + (result.stderr.strip() or result.stdout.strip()))
        return out.read_text()


def check(date: str, section: Path = SECTION, token: "str | None" = None) -> int:
    path = letter_for(date, section)
    if path is None:
        print(f"digest-campaign: no letter dated {date} in {section}; nothing to check")
        return 2
    subject = subject_for(path)
    if not subject:
        print(f"digest-campaign: {path.name} carries no sendfox_subject; the inbox line is blank")
        return 3
    key = token or resolve_token()
    if not key:
        print("digest-campaign: no SendFox key in the keychain or ~/.secrets")
        return 3
    try:
        row = campaign_for(campaigns(key), subject)
    except SendFoxError as e:
        print(f"digest-campaign: could not read campaigns ({e})")
        return 3
    if will_send(row):
        state = "sent" if row.get("sent_at") else f"scheduled for {row.get('scheduled_at')}"
        print(f"digest-campaign: campaign {row.get('id')} is {state} — \"{subject}\"")
        return 0
    print(f"digest-campaign: NOTHING WILL SEND {path.name} — no campaign exists for "
          f"\"{subject}\"\n  remedy: python3 scripts/digest-campaign.py --schedule "
          f"--file {path} --slug {path.stem}")
    return 3


def schedule(file: Path, slug: str, at: "str | None" = None, dry_run: bool = False,
             token: "str | None" = None, list_id: int = LIST_PRIMARY) -> int:
    subject = subject_for(file)
    if not subject:
        print(f"digest-campaign: {file.name} carries no sendfox_subject; refusing")
        return 3
    fields = read_frontmatter(file)
    when = at or schedule_moment(fields.get("date") or "", hour=6)
    key = None if dry_run else (token or resolve_token())
    if not dry_run and not key:
        print("digest-campaign: no SendFox key in the keychain or ~/.secrets")
        return 3

    rows: "list[dict]" = []
    if not dry_run:
        try:
            rows = campaigns(key)
        except SendFoxError as e:
            print(f"digest-campaign: could not read campaigns ({e})")
            return 3
        existing = campaign_for(rows, subject)
        if will_send(existing):
            state = "sent" if existing.get("sent_at") else f"scheduled for {existing.get('scheduled_at')}"
            print(f"digest-campaign: campaign {existing.get('id')} already {state}; nothing to do")
            return 0

    html = render_html(file, slug)
    if dry_run:
        print(f"digest-campaign: would create \"{subject}\" for {when} UTC "
              f"to list {list_id} ({len(html)} characters of HTML)")
        return 0

    created = api(key, "POST", "/campaigns", {
        "title": subject, "subject": subject, "html": html,
        "from_name": "Philip Huffman", "from_email": "philip.r.huffman@gmail.com",
        "lists": [list_id],
    })
    campaign = created.get("data", created)
    cid = campaign.get("id")
    if not cid:
        print(f"digest-campaign: the create answer carried no id: {created}")
        return 3
    api(key, "PATCH", f"/campaigns/{cid}", {"scheduled_at": when})
    record = api(key, "GET", f"/campaigns/{cid}")
    record = record.get("data", record)
    if not will_send(record):
        print(f"digest-campaign: campaign {cid} was created but is not scheduled "
              f"(scheduled_at {record.get('scheduled_at')!r})")
        return 3
    print(f"digest-campaign: campaign {cid} scheduled for {record.get('scheduled_at')} UTC "
          f"— \"{subject}\"")
    return 0


def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="report whether a campaign exists for the letter dated --date")
    ap.add_argument("--date", help="YYYY-MM-DD of the letter to check")
    ap.add_argument("--schedule", action="store_true",
                    help="create and schedule the campaign for --file")
    ap.add_argument("--file", help="the draft to send (pending/<name>.md)")
    ap.add_argument("--slug", help="the published page's slug, used for the footer link")
    ap.add_argument("--at", help='SendFox scheduled_at, UTC, "YYYY-MM-DD HH:MM:SS"')
    ap.add_argument("--section", help="directory of published letters (tests use a fixture)")
    ap.add_argument("--dry-run", action="store_true",
                    help="render and report without touching the API")
    args = ap.parse_args(argv)

    if args.check:
        if not args.date:
            ap.error("--check needs --date")
        section = Path(args.section) if args.section else SECTION
        return check(args.date, section)
    if args.schedule:
        if not args.file:
            ap.error("--schedule needs --file")
        if not args.slug:
            ap.error("--schedule needs --slug")
        return schedule(Path(args.file), args.slug, args.at, args.dry_run)
    ap.error("choose --check or --schedule")


if __name__ == "__main__":
    raise SystemExit(main())
