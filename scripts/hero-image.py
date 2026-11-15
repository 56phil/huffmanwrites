#!/usr/bin/env python3
"""Generate a hero image through fal.ai, reproducibly.

Why this exists: the harness's `generate_image` tool resolves its model through
an image-capable provider, and this machine has none — the only image credential
here is fal's. An extension used to substitute a fal-backed tool under the same
name; when that stopped loading (measured 15NOV26, `Image generation exhausted
the resolved image chain` on every call, while the module itself still imported
as a valid factory), hero generation fell back to ad-hoc scripts that took a
prompt on a command line and left nothing behind but the image.

The ad-hoc part is the defect. Six plates for `161-blank-reason-field` were
generated before one was kept, and only the survivor's prompt survived, in a
brief written afterwards. A generation whose seed, size and prompt are not
recorded cannot be reproduced or defended when a caption or an alt line has to
change.

So this script prints the whole request before it runs, takes `--seed`, and
writes nothing but the image. Everything it prints is safe to paste into a
brief: the key is read from the login keychain, held in memory, and never
echoed, not even in an error.

Usage:
    python3 scripts/hero-image.py --prompt-file /tmp/prompt.txt --aspect 16:9 \\
        --seed 2611 --out static/img/articles/161-slug_16x9.webp

    python3 scripts/hero-image.py --prompt "a marble ledger page" --width 1024 \\
        --height 1280 --out /tmp/mobile.png --dry-run

Exit codes: 0 wrote an image; 2 setup problem (no key, bad size, bad output
path); 3 fal refused, failed or timed out; 4 the download failed.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

QUEUE = "https://queue.fal.run"
DEFAULT_MODEL = "fal-ai/flux/dev"
KEYCHAIN_SERVICE = "huffmanwrites-fal"

# The two shapes the site uses. A hero is 16:9 on desktop and 4:5 on a phone,
# and the numbers below are what `static/img/articles/*` already carries.
ASPECTS = {"16:9": (1536, 1024), "4:5": (1024, 1280), "1:1": (1024, 1024)}

POLL_SECONDS = 2.5


def read_key(use_keychain: bool = True) -> str:
    """The key, from the environment first and the login keychain second.

    Environment first so a test can hand this a stub without touching the real
    credential; the keychain is the durable home per the repo's secrets rule.
    """
    from_env = os.environ.get("FAL_KEY", "").strip()
    if from_env:
        return from_env
    if not use_keychain:
        return ""
    user = os.environ.get("USER", "")
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-a", user, "-s", KEYCHAIN_SERVICE, "-w"],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def request_body(prompt: str, width: int, height: int, seed: int | None, model: str) -> dict:
    """The exact JSON posted to fal. Pure, so a test can read it without a network."""
    body = {
        "prompt": prompt,
        "num_images": 1,
        "enable_safety_checker": False,
        "image_size": {"width": width, "height": height},
    }
    if seed is not None:
        body["seed"] = seed
    return {"endpoint": f"{QUEUE}/{model}", "body": body}


def submit(endpoint: str, body: dict, key: str, timeout: float) -> dict:
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Key {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        queued = json.load(response)
    deadline = time.time() + timeout
    while True:
        if time.time() > deadline:
            raise TimeoutError(f"fal did not finish within {timeout:.0f}s")
        time.sleep(POLL_SECONDS)
        poll = urllib.request.Request(
            queued["status_url"], headers={"Authorization": f"Key {key}"}
        )
        with urllib.request.urlopen(poll, timeout=60) as response:
            state = json.load(response)
        status = state.get("status")
        if status == "COMPLETED":
            break
        if status == "FAILED" or state.get("error"):
            raise RuntimeError(f"fal failed: {state.get('error') or status}")
    result = urllib.request.Request(
        queued["response_url"], headers={"Authorization": f"Key {key}"}
    )
    with urllib.request.urlopen(result, timeout=60) as response:
        return json.load(response)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a hero image through fal.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--prompt", help="the prompt text")
    source.add_argument("--prompt-file", help="a file holding the prompt")
    size = parser.add_mutually_exclusive_group(required=True)
    size.add_argument("--aspect", choices=sorted(ASPECTS), help="a size the site uses")
    size.add_argument("--width", type=int, help="exact width, with --height")
    parser.add_argument("--height", type=int, help="exact height, with --width")
    parser.add_argument("--seed", type=int, help="fixed seed, so a plate can be re-run")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"fal endpoint (default {DEFAULT_MODEL})")
    parser.add_argument("--out", required=True, help="where to write the image")
    parser.add_argument("--timeout", type=float, default=300.0, help="seconds to wait (default 300)")
    parser.add_argument("--no-keychain", action="store_true", help="do not read the login keychain")
    parser.add_argument("--dry-run", action="store_true", help="print the request and stop")
    args = parser.parse_args(argv)

    if args.width is not None or args.height is not None:
        if args.width is None or args.height is None:
            print("hero-image: --width and --height must be given together", file=sys.stderr)
            return 2
        width, height = args.width, args.height
    else:
        width, height = ASPECTS[args.aspect]
    if width % 16 or height % 16:
        print(f"hero-image: {width}x{height} is not a multiple of 16", file=sys.stderr)
        return 2

    prompt = args.prompt if args.prompt is not None else ""
    if args.prompt_file:
        try:
            prompt = open(args.prompt_file, encoding="utf-8").read().strip()
        except OSError as exc:
            print(f"hero-image: cannot read {args.prompt_file}: {exc.strerror}", file=sys.stderr)
            return 2
    if not prompt.strip():
        print("hero-image: the prompt is empty", file=sys.stderr)
        return 2

    request = request_body(prompt, width, height, args.seed, args.model)
    # Printed before the call, so the log is the record even when the call fails.
    print(f"hero-image: model={args.model} size={width}x{height} seed={args.seed}")
    print("hero-image: prompt: " + " ".join(prompt.split()))
    if args.dry_run:
        print(json.dumps(request, indent=2))
        return 0

    key = read_key(use_keychain=not args.no_keychain)
    if not key:
        print(
            f"hero-image: no key. Install it with scripts/install-secret.sh fal "
            f"(keychain service {KEYCHAIN_SERVICE}) or set FAL_KEY.",
            file=sys.stderr,
        )
        return 2
    if not os.path.isdir(os.path.dirname(os.path.abspath(args.out))):
        print(f"hero-image: no directory at {os.path.dirname(os.path.abspath(args.out))}", file=sys.stderr)
        return 2

    try:
        payload = submit(request["endpoint"], request["body"], key, args.timeout)
    except TimeoutError as exc:
        print(f"hero-image: {exc}", file=sys.stderr)
        return 3
    except (RuntimeError, urllib.error.HTTPError, urllib.error.URLError) as exc:
        print(f"hero-image: {exc}", file=sys.stderr)
        return 3

    images = payload.get("images") or []
    if not images:
        print("hero-image: fal returned no image", file=sys.stderr)
        return 3
    url = images[0].get("url")
    try:
        with urllib.request.urlopen(url, timeout=120) as response:
            data = response.read()
    except (urllib.error.HTTPError, urllib.error.URLError) as exc:
        print(f"hero-image: download failed: {exc}", file=sys.stderr)
        return 4
    with open(args.out, "wb") as handle:
        handle.write(data)
    reported = images[0].get("width"), images[0].get("height")
    print(f"hero-image: wrote {args.out} ({len(data)} bytes, fal reports {reported[0]}x{reported[1]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
