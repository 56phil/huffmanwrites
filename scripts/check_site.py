#!/usr/bin/env python3
"""Validate Hugo content metadata and built internal links."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


SITE_HOSTS = {"huffmanwrites.org", "www.huffmanwrites.org"}
REQUIRED_FRONTMATTER = ("title", "description", "date")
ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST_PATH = ROOT / "scripts" / "linkcheck_allowlist.txt"


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in {"href", "src", "srcset"} and value:
                if name == "srcset":
                    for candidate in value.split(","):
                        link = candidate.strip().split(" ")[0]
                        if link:
                            self.links.append((name, link))
                else:
                    self.links.append((name, value))


def parse_frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    if text.startswith("+++\n"):
        end = text.find("\n+++", 4)
        if end == -1:
            return {}
        data: dict[str, object] = {}
        for raw_line in text[4:end].splitlines():
            line = raw_line.strip()
            if not line or "=" not in line:
                continue
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip().strip('"').strip("'")
        return data

    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}

    data: dict[str, object] = {}
    current_list_key: str | None = None
    for raw_line in text[4:end].splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        if current_list_key and line.startswith("  - "):
            value = line[4:].strip().strip('"').strip("'")
            current = data.setdefault(current_list_key, [])
            if isinstance(current, list):
                current.append(value)
            continue
        current_list_key = None
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value == "":
            data[key] = []
            current_list_key = key
        elif value.startswith("[") and value.endswith("]"):
            data[key] = [
                item.strip().strip('"').strip("'")
                for item in value[1:-1].split(",")
                if item.strip()
            ]
        else:
            data[key] = value.strip('"').strip("'")
    return data


def is_future_date(value: object, today: dt.date) -> bool:
    if not isinstance(value, str):
        return False
    match = re.match(r"(\d{4}-\d{2}-\d{2})", value)
    if not match:
        return False
    return dt.date.fromisoformat(match.group(1)) > today


def validate_frontmatter(today: dt.date) -> list[str]:
    errors: list[str] = []
    for path in sorted((ROOT / "content").rglob("*.md")):
        rel = path.relative_to(ROOT)
        data = parse_frontmatter(path)
        if not data:
            errors.append(f"{rel}: missing front matter")
            continue
        required = ("title",)
        if rel.parts[1:2] == ("posts",):
            required = REQUIRED_FRONTMATTER
        elif rel.parts[1:2] == ("books",):
            required = ("title", "description")
        for key in required:
            if key not in data or data[key] == "" or data[key] == []:
                errors.append(f"{rel}: missing required front matter field '{key}'")
        if data.get("hero_mobile") and not data.get("hero_desktop"):
            errors.append(f"{rel}: hero_mobile requires hero_desktop")
        if data.get("image_mobile") and not data.get("image_desktop"):
            errors.append(f"{rel}: image_mobile requires image_desktop")
        aliases = data.get("aliases", [])
        if isinstance(aliases, str):
            aliases = [aliases]
        if isinstance(aliases, list):
            for alias in aliases:
                if not isinstance(alias, str):
                    continue
                if not alias.startswith("/") or not alias.endswith("/"):
                    errors.append(f"{rel}: alias should start and end with '/': {alias}")
        if is_future_date(data.get("date"), today) and data.get("draft") == "true":
            errors.append(f"{rel}: draft content should not also rely on a future date")
    return errors


def public_target_exists(public_dir: Path, link: str) -> bool:
    parsed = urlparse(link)
    if parsed.scheme and parsed.scheme not in {"http", "https"}:
        return True
    if parsed.netloc and parsed.netloc not in SITE_HOSTS:
        return True

    path = unquote(parsed.path)
    if not path or path == "/":
        return True
    if path.startswith("//"):
        return True
    target = public_dir / path.lstrip("/")
    if target.is_dir():
        target = target / "index.html"
    elif target.suffix == "":
        target = target / "index.html"
    return target.exists()


def load_link_allowlist() -> set[str]:
    if not ALLOWLIST_PATH.exists():
        return set()
    allowed: set[str] = set()
    for line in ALLOWLIST_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            allowed.add(line)
    return allowed


def validate_links(public_dir: Path) -> list[str]:
    errors: list[str] = []
    allowlist = load_link_allowlist()
    if not public_dir.exists():
        return [f"{public_dir.relative_to(ROOT)}: missing; run hugo before checking links"]
    for path in sorted(public_dir.rglob("*.html")):
        parser = LinkParser()
        parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
        for attr, link in parser.links:
            if link.startswith("#") or link.startswith("data:"):
                continue
            if link in allowlist:
                continue
            if not public_target_exists(public_dir, link):
                rel = path.relative_to(ROOT)
                errors.append(f"{rel}: broken {attr} -> {link}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public-dir", default="public")
    args = parser.parse_args()

    today = dt.date.today()
    errors = validate_frontmatter(today)
    errors.extend(validate_links(ROOT / args.public_dir))

    if errors:
        for error in errors:
            print(error)
        return 1
    print("Site checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
