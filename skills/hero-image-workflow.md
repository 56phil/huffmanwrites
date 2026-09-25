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

## Credentials (single source of truth)
The fal.ai key has exactly one home: the **login keychain** as the generic password `huffmanwrites-fal`, with `~/.secrets` (chmod 600) as the fallback every launchd runner already reads. Never keep a third copy — a stale duplicate beside the live key is what silently 401s, and the difference is invisible until a generation fails.

```bash
# What the runners do, and what you should do too:
FAL_KEY="$(security find-generic-password -a "$USER" -s huffmanwrites-fal -w)"
[ -z "$FAL_KEY" ] && FAL_KEY="$(grep -oE 'FAL_KEY="[^"]+"' "$HOME/.secrets" | head -1 | cut -d'"' -f2)"
```

In an interactive shell, `.zshrc` already exports `FAL_KEY` from that keychain entry, so `$FAL_KEY` is set. Do not read a token out of a dotfile in the repo; a repo-local copy drifts from the keychain and nothing tells you.

## Operational Steps
1. **Identify**: Select target post from `image-assignments.md`.
2. **Prompt**: Utilize the specific prompt designated for that post, ensuring visual identity keywords are present.
3. **Generate**: Produce both 16:9 and 4:5 variants.
   - **Timeout note (learned 2026-09-05):** the 4:5 call (`1024x1280`) consistently takes longer than the 16:9 (`1536x1024`) and routinely exceeds a 120-second cell/tool ceiling — it has timed out on every recent pair at least once, and three times in a row on the 69-the-obstacle-is-the-way pair. Do NOT gamble on retries: run the 4:5 generation with the cell timeout disabled (`timeout: 0` in the eval call) so the request runs to completion (~2.5 min typical). The kernel stays alive across a timeout, but an interrupted cell aborts the in-flight HTTP request, so a "retry" is a fresh generation, not a resume.
4. **Verify**: Ensure files are renamed correctly and placed in `static/img/articles/`.
5. **Wire**: Update the Hugo post's frontmatter to link these assets.
6. **Add to gallery**: Add a matching entry to `data/gallery.yml` (image, title, caption, link to the post). The gallery does not auto-populate from post frontmatter — a hero image doesn't appear there until it's added by hand.