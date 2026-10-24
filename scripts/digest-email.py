#!/usr/bin/env python3
"""Render a Stoic Saturday draft as the newsletter email body.

The pending draft is Markdown with frontmatter; SendFox needs one HTML string.
This does the conversion and adds the masthead the letter carries in the inbox:
the PRH monogram, the series name, and the send date. Nothing else is styled —
the body stays Pandoc's output, because the letter has to be edited in the
draft, not in a template.

    python3 scripts/digest-email.py pending/<draft>.md --out /tmp/letter.html

The monogram is `static/img/prh-monogram.png`, served from `www.` because the
apex 301s and an email client will not follow it. Its source is the SVG beside
it; regenerate with `rsvg-convert -w 192 -h 192`.
"""

import argparse
import datetime as dt
import html
import re
import subprocess
import sys
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://www.huffmanwrites.org"
MONOGRAM = f"{SITE}/img/prh-monogram.png"


def frontmatter(text: str) -> "tuple[dict, str]":
    if not text.startswith("---\n"):
        raise SystemExit("digest-email: the draft has no frontmatter")
    _, raw, body = text.split("---\n", 2)
    fields = {}
    for line in raw.splitlines():
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if m:
            fields[m.group(1)] = m.group(2).strip().strip('"')
    return fields, body


def send_date(fields: dict) -> str:
    stamp = fields.get("date")
    if not stamp:
        raise SystemExit("digest-email: the draft has no `date`")
    return dt.datetime.fromisoformat(stamp).strftime("%B %-d, %Y")


def masthead(date_line: str) -> str:
    return (
        '<div style="text-align:center;padding:4px 0 16px;'
        'border-bottom:1px solid #D4820A;margin-bottom:26px;">'
        f'<img src="{MONOGRAM}" width="64" height="64" alt="PRH" '
        'style="display:block;margin:0 auto 12px;border:0;outline:none;text-decoration:none;">'
        '<div style="font-family:Georgia,\'Times New Roman\',serif;font-size:15px;'
        'letter-spacing:4px;text-transform:uppercase;color:#131E39;">Stoic Saturday</div>'
        '<div style="font-family:Georgia,\'Times New Roman\',serif;font-size:13px;'
        f'color:#6E6E6E;margin-top:6px;">{html.escape(date_line)}</div>'
        "</div>"
    )


def body_html(markdown: str) -> str:
    try:
        done = subprocess.run(
            ["pandoc", "-f", "markdown", "-t", "html", "-"],
            input=markdown, capture_output=True, text=True, check=True,
        )
    except FileNotFoundError:
        raise SystemExit("digest-email: pandoc is not installed")
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"digest-email: pandoc failed: {exc.stderr[:200]}")
    return done.stdout


def footer(slug: str) -> str:
    return (
        "\n<hr>\n"
        f'<p><a href="{SITE}/posts/digests/{slug}/">Read this letter on the site</a></p>\n'
        '<p><a href="{{unsubscribe_url}}">Unsubscribe</a></p>\n'
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Render a Stoic Saturday draft as email HTML.")
    ap.add_argument("draft", help="pending/<draft>.md")
    ap.add_argument("--out", help="write here instead of stdout")
    ap.add_argument("--slug", help="page slug (default: the draft's filename stem)")
    args = ap.parse_args()

    path = pathlib.Path(args.draft)
    if not path.is_file():
        raise SystemExit(f"digest-email: no such draft: {path}")
    fields, body = frontmatter(path.read_text())
    slug = args.slug or path.stem
    page = masthead(send_date(fields)) + body_html(body) + footer(slug)
    if args.out:
        pathlib.Path(args.out).write_text(page)
    else:
        sys.stdout.write(page)
    return 0


if __name__ == "__main__":
    sys.exit(main())
