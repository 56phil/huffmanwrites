#!/usr/bin/env python3
"""Grade a generated hero image onto the house navy.

Why this exists: FLUX reads "deep midnight navy" as near-black. Measured on
NN 139 (`139-seneca-project_*`), the darkest 8% of pixels came back at mean
RGB (4, 4, 5) where the house ground is `#131E39` = (19, 30, 57). The prompt
cannot fix it; the grade does.

The grade is two moves, both applied in linear 8-bit RGB with no tone curve:

1. **Shadow lift.** Compute luminance, take the mean RGB of the darkest
   `--floor-pct` of pixels, and add the vector `navy - measured` to every pixel
   with a weight that is 1 at black and falls linearly to 0 at `--threshold`
   luminance. Detail inside the shadows is preserved because the offset is
   additive rather than a multiplier.
2. **Amber lift.** Above `--amber-from` luminance, add a small warm vector so a
   lit marble surface reads gold rather than cream.

Everything above `--threshold` is untouched, which is why the marble keeps the
model's own grain and the light keeps its falloff.

Usage:
    python3 scripts/grade-hero-navy.py in.png out.webp
    python3 scripts/grade-hero-navy.py in.webp out.webp --quality 92
"""

from __future__ import annotations

import argparse
import sys

import numpy as np
from PIL import Image

LUMA = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
NAVY = (0x13, 0x1E, 0x39)
AMBER = (6.0, 2.0, -6.0)


def grade(
    src: Image.Image,
    navy: tuple[int, int, int] = NAVY,
    floor_pct: float = 8.0,
    threshold: float = 45.0,
    amber_from: float = 120.0,
    amber: tuple[float, float, float] = AMBER,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (graded uint8 array, measured shadow mean, graded shadow mean)."""
    a = np.asarray(src.convert("RGB")).astype(np.float32)
    lum = a @ LUMA
    before = a[lum < np.percentile(lum, floor_pct)].mean(axis=0)

    w = np.clip((threshold - lum) / threshold, 0.0, 1.0)[..., None]
    a = a + w * (np.array(navy, dtype=np.float32) - before)

    hi = np.clip((lum - amber_from) / 120.0, 0.0, 1.0)[..., None]
    a = a + hi * np.array(amber, dtype=np.float32)

    a = np.clip(a, 0, 255)
    out_lum = a @ LUMA
    after = a[out_lum < np.percentile(out_lum, floor_pct)].mean(axis=0)
    return a.astype(np.uint8), before, after


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("source", help="generated image (PNG or WebP)")
    p.add_argument("target", help="WebP to write")
    p.add_argument("--floor-pct", type=float, default=8.0,
                   help="percentile used to measure the existing ground (default 8)")
    p.add_argument("--threshold", type=float, default=45.0,
                   help="luminance below which the navy lift is fully applied (default 45)")
    p.add_argument("--amber-from", type=float, default=120.0,
                   help="luminance above which the amber lift begins (default 120)")
    p.add_argument("--quality", type=int, default=88, help="WebP quality (default 88)")
    args = p.parse_args(argv)

    src = Image.open(args.source)
    graded, before, after = grade(src, floor_pct=args.floor_pct, threshold=args.threshold,
                                  amber_from=args.amber_from)
    Image.fromarray(graded).save(args.target, "WEBP", quality=args.quality, method=6)

    print(f"source: {args.source} {src.size[0]}x{src.size[1]}")
    print(f"target: {args.target}")
    print(f"shadow mean before: ({before[0]:.1f}, {before[1]:.1f}, {before[2]:.1f}); "
          f"after: ({after[0]:.1f}, {after[1]:.1f}, {after[2]:.1f})")
    print(f"navy target:        ({NAVY[0]:.0f}, {NAVY[1]:.0f}, {NAVY[2]:.0f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
