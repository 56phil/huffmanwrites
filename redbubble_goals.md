# Redbubble Design Project: Credo Collection

## Purpose
Expand the **huffmanwrites.org** brand into wearable/apparel designs that embody the credo:
> **"Think clearly. Live intentionally. Love deeply."**

Target audience:
- Readers of *The Stoic Citizen*, *Misaligned*, and *Unstuck*.
- Neurodivergent individuals seeking affirming, minimalist designs.
- Philosophy enthusiasts who value intentionality.

## Scope
### Designs
5 existing designs (located in `static/img/Redbutton-Credo-Designs/`):
1. `circle-5000x5000.png` — Circular motif (likely the credo in gold on navy).
2. `credo-5000x5000.png` — Primary credo typography.
3. `design-5000x5000.png` — Abstract/Stoic symbol (e.g., Parian marble texture).
4. `triangle-5000x5000.png` — Tripartite design ("Think/Live/Love").
5. `wreath-5000x5000.png` — Stoic wreath (symbol of resilience).

### Products
Initial launch:
- **Stickers** (all 5 designs).
- **T-shirts** (unisex, black/navy).
- **Mugs** (11oz, white/black).
- **Phone cases** (iPhone/Android).

### Platform
Redbubble only (for now).

## Constraints
### Technical
- **File format**: PNG (already compliant).
- **Resolution**: 5000x5000px (Redbubble max; no upscaling needed).
- **DPI**: 300 (assumed; verify with `file` command).
- **Bleed**: Safe zone ≥ 300px from edges (verify with `vision_analyze`).
- **Color profile**: sRGB (verify with `image_generate` preview).

### Brand
- **Colors**: Navy `#131E39` (background), gold `#D4820A` (text/accents).
  - Merch background sampled from actual design PNGs (Digital Color Meter, Display P3: R 0.109 / G 0.159 / B 0.281) → converted to sRGB hex `#18294A`. Lighter/more saturated than the site's `#131E39` due to P3→sRGB gamut conversion — use `#18294A` when matching Redbubble print colors, not the site navy.
- **Typography**: Small-caps for "Think/Live/Love" (match `custom.css`).
- **Tone**: Minimalist, conceptual, high-contrast.

### Metadata
- **Titles**: "[Design Name] — Stoic Credo [Product Type]"
  Example: `"Circle — Stoic Credo Sticker"`.
- **Descriptions**:
  > "A minimalist design embodying the Stoic credo: *Think clearly. Live intentionally. Love deeply.* © Philip Huffman | [huffmanwrites.org](https://huffmanwrites.org)"
- **Tags**:
  `stoic, philosophy, minimalist, navy gold, Parian marble, neurodivergence, intentional living, huffmanwrites, credo, resilience`

## Workflow
1. **Rename files** for SEO/clarity:
   - `circle.png` → `credo-circle-stoic-sticker.png`
   - `credo.png` → `think-live-love-credo-typography.png`
   - `design.png` → `parian-marble-stoic-texture.png`
   - `triangle.png` → `think-live-love-tripartite-credo.png`
   - `wreath.png` → `stoic-wreath-resilience-symbol.png`

2. **Verify designs** with `vision_analyze`:
   - Check bleed, DPI, color accuracy.
   - Confirm readability on dark/light products.

3. **Upload to Redbubble** using the metadata template.

4. **Launch** and monitor sales/traffic.

## Risks
- **Redbubble’s algorithm**: Low organic reach; mitigate with cross-promotion (huffmanwrites.org, newsletter).
- **Design theft**: Watermark previews with "© huffmanwrites.org".
- **Color shifts**: Test prints via Redbubble’s mockup tool.

## Success Metrics
- **Short-term**: 5 designs live, 10 sales in first 30 days.
- **Long-term**: Expand to 10+ designs (neurodivergence-affirming themes).