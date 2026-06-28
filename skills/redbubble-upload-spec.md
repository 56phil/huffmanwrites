# Redbubble Upload Spec

Reference for uploading artwork to the huffmanwrites Redbubble account.

## Account

- Account: huffmanwrites (or philhuffman56@icloud.com — check at redbubble.com)

## Master File Requirements

| Property | Requirement |
|---|---|
| Format | PNG (preferred) or JPG |
| Color mode | RGB |
| Resolution | 300 DPI minimum |
| Recommended size | 7632 × 6480 px (Redbubble's "perfect" size) |
| Minimum size | 2048 × 2048 px (anything smaller gets a quality warning) |
| Max file size | 300 MB |

Redbubble scales one master file to all products. Upload the largest version you have — it can only scale down, not up without quality loss.

## Product-Specific Notes

### Apparel (T-shirts, hoodies, etc.)
- Print area is centered on the garment
- Redbubble auto-positions; you can adjust in the editor after upload
- Transparent PNG works best for apparel — the shirt color shows through any transparent areas

### Stickers
- Use PNG with transparency for die-cut stickers (Redbubble cuts along the image edge)
- Add a small white border inside the artwork if you want a classic sticker look

### Prints & Posters
- Full bleed: artwork should extend to the edges
- Safe zone: keep text and key elements at least 0.125 in from the edge

### Mugs
- Wrap-around design: ~3300 × 1300 px at 300 DPI works well
- The handle area is not printed

### Phone Cases
- Redbubble generates per-model crops from the master; verify the most popular models (iPhone 15, Samsung S24) in the editor

### Tote Bags
- Print area: ~14 × 14 in at 300 DPI = ~4200 × 4200 px

### Scarves / Tapestries / Throw Blankets
- These use the full master at high resolution; the 7632 × 6480 px master covers them well

## Credo Product Line

Current products in the huffmanwrites shop tied to Redbubble:

| Product | Content file |
|---|---|
| Credo Tee | `content/shop/credo-tee.md` |
| Credo Mug | `content/shop/credo-mug.md` |
| Credo Print | `content/shop/credo-print.md` |
| Credo Journal | `content/shop/credo-journal.md` |
| Credo Garden Flag | `content/shop/credo-garden-flag.md` |

## Workflow

1. Create artwork at 7632 × 6480 px, 300 DPI, RGB, PNG
2. Upload to Redbubble as a new "work"
3. Enable the desired product types and adjust positioning in the Redbubble editor
4. Copy the product URL and add/update `link:` frontmatter in the matching `content/shop/*.md` file
5. Run `hugo --gc --minify` and verify the shop page renders correctly

## Visual Identity Reminder

All artwork should follow the established aesthetic:
- Deep midnight navy backgrounds (`#131E39`)
- Glowing gold accents (amber `#D4820A`)
- Parian marble textures where appropriate
- Cinematic/conceptual imagery — not literal
- Credo: **"Think clearly. Live intentionally. Love deeply."**
