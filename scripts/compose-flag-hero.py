#!/usr/bin/env python3
"""Composite a correctly drawn United States flag onto a blank generated cloth.

Why this exists: FLUX.1 dev will not fly a flag upside down. Six prompts across five
phrasings ("canton at the bottom of the cloth", "the union sits in the lower corner",
"turn the flag 180 degrees", "draped with the blue canton at the bottom") all returned
the canton at the top left. For hero NN 140 (`140-the-credibility-ledger_*`) the cloth is
therefore generated blank and the flag is drawn and warped onto it here: fifty stars in
nine rows of six and five, thirteen stripes beginning and ending red, the union covering
the hoist-side 40 per cent and 7/13 of the height, flipped vertically so it hangs upside
down with the union along the bottom edge, as a distress signal.

The composite keeps the cloth's folds by multiplying the texture by a high-pass of the
cloth's own luminance, and its exposure is tied to the cloth's median luminance so a
lamp-lit flag does not read as a sticker pasted onto a night scene.

Usage:
    python3 scripts/compose-flag-hero.py in.png out.png x0,y0,x1,y1
    python3 scripts/compose-flag-hero.py in.png out.png tx0,ty0 tx1,ty1 bx1,by1 bx0,by0

Four numbers are a bounding box; the cloth quad is found inside it by luminance and
neutrality (a bright flagpole inside the box will fool it, which is why eight numbers
exist). Eight numbers are the cloth's own corners, clockwise from the pole-side top:
the reliable form, measured off the source.

The source must be a generated scene with a plain unmarked white cloth hanging from the
pole. Regenerate one with:

    a wide rectangular flag of plain unmarked white cloth, twice as wide as it is tall,
    streaming out to the right in a light breeze with soft vertical folds and a slight
    curl at the free end, no design and no pattern and no emblem on it at all

Then grade the result onto the house navy with `scripts/grade-hero-navy.py`, which this
script deliberately does not do: the grade belongs after the composite, not before.
"""

import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OLD_GLORY = (191, 10, 48)
WHITE = (255, 255, 255)
UNION = (0, 40, 104)
LUMA = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)


def flag_texture(w=2200):
    h = int(round(w / 1.9))
    img = Image.new("RGB", (w, h), WHITE)
    d = ImageDraw.Draw(img)
    stripe = h / 13.0
    for i in range(13):
        if i % 2 == 0:
            d.rectangle([0, i * stripe, w, (i + 1) * stripe], fill=OLD_GLORY)
    cw, ch = h * 0.76, h * 7 / 13
    d.rectangle([0, 0, cw, ch], fill=UNION)
    dy, dx = ch / 10.0, cw / 12.0
    r = ch * 0.0308

    def star(cx, cy, rad):
        pts = []
        for k in range(10):
            ang = -np.pi / 2 + k * np.pi / 5
            rr = rad if k % 2 == 0 else rad * 0.382
            pts.append((cx + rr * np.cos(ang), cy + rr * np.sin(ang)))
        d.polygon(pts, fill=WHITE)

    for row in range(9):
        count = 6 if row % 2 == 0 else 5
        for c in range(count):
            star(dx * (2 * c + (1 if row % 2 == 0 else 2)), dy * (row + 1), r)
    tex = np.asarray(img).astype(np.float32) / 255.0
    return np.flipud(tex)          # flown upside down: canton along the bottom


def homography(quad):
    src = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=np.float64)
    dst = np.array(quad, dtype=np.float64)
    A, b = [], []
    for (u, v), (x, y) in zip(src, dst):
        A.append([u, v, 1, 0, 0, 0, -u * x, -v * x]); b.append(x)
        A.append([0, 0, 0, u, v, 1, -u * y, -v * y]); b.append(y)
    return np.append(np.linalg.solve(np.array(A), np.array(b)), 1.0).reshape(3, 3)


def find_quad(lum, bbox, thresh=0.34):
    x0, y0, x1, y1 = bbox
    sub = lum[y0:y1, x0:x1]
    m = sub > thresh
    ys, xs = np.nonzero(m)
    if xs.size < 50:
        raise SystemExit("no cloth found in bbox")
    P = np.stack([xs + x0, ys + y0], axis=1).astype(np.float64)
    s = P[:, 0] + P[:, 1]; d = P[:, 0] - P[:, 1]
    quad = [P[np.argmin(s)], P[np.argmax(d)], P[np.argmax(s)], P[np.argmin(d)]]
    return [tuple(q) for q in quad]


def neutral_mask(arr, bbox, thresh=0.34, sat=0.22):
    x0, y0, x1, y1 = bbox
    sub = arr[y0:y1, x0:x1]
    lum = sub @ LUMA
    mx = sub.max(axis=2); mn = sub.min(axis=2)
    neutral = (mx - mn) < sat
    m = (lum > thresh) & neutral
    ys, xs = np.nonzero(m)
    P = np.stack([xs + x0, ys + y0], axis=1).astype(np.float64)
    s = P[:, 0] + P[:, 1]; d = P[:, 0] - P[:, 1]
    return [P[np.argmin(s)], P[np.argmax(d)], P[np.argmax(s)], P[np.argmin(d)]]


def main():
    src, out = sys.argv[1], sys.argv[2]
    arg = sys.argv[3]
    nums = [float(v) for v in arg.split(",")]
    bbox = tuple(int(v) for v in arg.split(",")) if len(nums) == 4 else (0, 0, 1, 1)
    fixed = [tuple(nums[i:i + 2]) for i in range(0, 8, 2)] if len(nums) == 8 else None
    gain = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
    im = Image.open(src).convert("RGB")
    W, H = im.size
    arr = np.asarray(im).astype(np.float32) / 255.0
    lum = arr @ LUMA
    quad = find_quad(lum, bbox) if fixed is None else fixed
    if fixed is not None:
        quad = fixed
    else:
        q2 = neutral_mask(arr, bbox)
        quad = [tuple(map(float, q)) for q in (q2 if np.all(np.isfinite(q2)) else quad)]

    xs = [p[0] for p in quad]; ys = [p[1] for p in quad]
    pad = 6
    x0, x1 = max(int(min(xs)) - pad, 0), min(int(max(xs)) + pad + 1, W)
    y0, y1 = max(int(min(ys)) - pad, 0), min(int(max(ys)) + pad + 1, H)

    gx, gy = np.meshgrid(np.arange(x0, x1), np.arange(y0, y1))
    pts = np.stack([gx.ravel(), gy.ravel(), np.ones(gx.size)])
    uv = np.linalg.inv(homography(quad)) @ pts
    u = uv[0] / uv[2] + 0.009 * np.sin(3.1 * np.pi * (uv[1] / uv[2]))
    v = uv[1] / uv[2]

    tex = flag_texture()
    th, tw = tex.shape[:2]
    inside = (u >= 0) & (u <= 1) & (v >= 0) & (v <= 1)
    sx = np.clip(u, 0, 1) * (tw - 1); sy = np.clip(v, 0, 1) * (th - 1)
    ix, iy = np.floor(sx).astype(int), np.floor(sy).astype(int)
    fx, fy = (sx - ix)[..., None], (sy - iy)[..., None]
    ix1 = np.clip(ix + 1, 0, tw - 1); iy1 = np.clip(iy + 1, 0, th - 1)
    samp = (tex[iy, ix] * (1 - fx) * (1 - fy) + tex[iy, ix1] * fx * (1 - fy)
            + tex[iy1, ix] * (1 - fx) * fy + tex[iy1, ix1] * fx * fy)
    samp = samp.reshape(y1 - y0, x1 - x0, 3)

    patch_lum = lum[y0:y1, x0:x1]
    sil = ((patch_lum > 0.28) & inside.reshape(y1 - y0, x1 - x0)).astype(np.float32)
    sil = np.asarray(Image.fromarray((sil * 255).astype(np.uint8)).filter(
        ImageFilter.MedianFilter(3))).astype(np.float32) / 255.0
    sil = np.asarray(Image.fromarray((sil * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(1.6))).astype(np.float32) / 255.0

    low = np.asarray(Image.fromarray((np.clip(patch_lum, 0, 1) * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(15))).astype(np.float32) / 255.0
    detail = np.clip(patch_lum / np.maximum(low, 1e-3), 0.68, 1.32)
    mean_lit = float(np.median(patch_lum[sil > 0.5]))
    exposure = (mean_lit / 0.78) * gain
    TINT = np.array([1.04, 0.97, 0.89], dtype=np.float32)
    layer = np.clip(samp * TINT * detail[..., None] * np.clip(exposure, 0.25, 1.0), 0, 1)

    a = sil[..., None]
    base = arr[y0:y1, x0:x1]
    arr[y0:y1, x0:x1] = base * (1 - a) + layer * a
    Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).save(out)
    print("wrote", out, "quad", [(round(a_, 1), round(b_, 1)) for a_, b_ in quad],
          "exposure", round(exposure, 3), "mean_lit", round(mean_lit, 3))


main()
