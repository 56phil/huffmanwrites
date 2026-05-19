# Skill: Hero Image Workflow

This skill manages the end-to-end process of generating and wiring "Hero" images for posts, ensuring visual consistency across the huffmanwrites site.

## Visual Identity (The Aesthetic)
All hero images must adhere to a strict conceptual aesthetic:
- **Textures**: Parian marble, weathered stone, translucent materials.
- **Palette**: Deep midnight navy backgrounds, glowing gold accents/lighting.
- **Lighting**: Dramatic cinematic lighting (chiaroscuro), gold filigree details.
- **Concept**: Metaphorical and conceptual rather than literal representations of the text.

## Generation Requirements
Every post requires a pair of images:
1. **Desktop Version**: 16:9 aspect ratio.
2. **Mobile Version**: 4:5 aspect ratio.
3. **Format**: WebP (`.webp`).

## Naming Convention
Files must be saved to `static/img/articles/` using the following format:
- `[id]-[slug]_[ratio].webp`
- *Example*: `11-pause_16x9.webp` and `11-pause_4x5.webp`.

## Implementation (Wiring) Workflow
After images are generated and placed in the assets folder, the post's frontmatter must be updated as follows:

| Frontmatter Field | Value/Requirement |
| :--- | :--- |
| `hero_desktop` | Path to 16:9 image (e.g., `"img/articles/11-pause_16x9.webp"`) |
| `hero_mobile` | Path to 4:5 image (e.g., `"img/articles/11-pause_4x5.webp"`) |
| `hero_alt` | Descriptive text for accessibility, matching the visual content. |
| `hero_caption` | A poetic or philosophical caption reflecting the post's theme. |

## Operational Steps
1. **Identify**: Select target post from `image-assignments.md`.
2. **Prompt**: Utilize the specific prompt designated for that post, ensuring visual identity keywords are present.
3. **Generate**: Produce both 16:9 and 4:5 variants.
4. **Verify**: Ensure files are renamed correctly and placed in `static/img/articles/`.
5. **Wire**: Update the Hugo post's frontmatter to link these assets.