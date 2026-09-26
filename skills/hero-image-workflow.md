# Skill: Hero Image Workflow

This skill manages the end-to-end process of generating and wiring "Hero" images for posts, ensuring visual consistency across the huffmanwrites site.

## Visual Identity (The Aesthetic)
All hero images must adhere to a strict conceptual aesthetic:
- **Textures**: Parian marble, weathered stone, translucent materials.
- **Palette**: Deep midnight navy backgrounds, glowing gold accents/lighting.
- **Lighting**: Dramatic cinematic lighting (chiaroscuro), gold filigree details.
- **Concept**: Metaphorical and conceptual rather than literal representations of the text.

**One documented exception, and it is deliberate.** The **weekly Chiefs report**
carries a *series plate* — one pair of images reused all season — whose ground is
the team's own red (`#E31837`, gold `#FFB81C`) rather than midnight navy, with a
wordmark composited in. Philip, 2026-09-26: "I want a hero image dedicated to the
weekly Chiefs report. This will be used for the rest of the season. Text is
acceptable. The background will be the red used by the Chiefs instead of the
routine dark navy blue." The plate is `static/img/articles/103-chiefs-report_*`,
it is wired into `skills/chiefs-weekly-report.md` as a fixed frontmatter contract,
and `scripts/chiefs-report.py --validate` fails the publish if it is missing. **Do
not regenerate it navy, and do not give an individual Chiefs report its own
hero** — the plate belongs to the series, and two reports sharing one image is the
intended result.

Two mechanics from that build that generalize. **Text that must be readable is
composited, never generated:** FLUX garbles letterforms whenever a prompt invites
them, so ask the model for a clean field with a reserved blank area and explicitly
forbid text, then draw the wordmark in ImageMagick with the site's own heading face
(instanced from the upstream variable font with `fontTools`). **A brand color is
graded, not described:** the model reads "crimson" about 14° warm of the target, so
rotate only the red-family pixels onto the exact hex (`/tmp/chiefs-grade.py` is the
scratch tool) and leave the stone and the light alone.

**Two more series plates joined it on 2026-09-26**, on the same contract, and both
keep the house navy rather than a team color:
- **`104-docket-report_*`** — the weekly Docket Report (Saturdays from 2026-10-03).
  A stack of carved marble ledgers with gold light spilling from one opened volume.
  Wired into `skills/docket-weekly-report.md`.
- **`105-senate-race-report_*`** — the weekly Senate Race Report (Sundays through
  2026-11-01). A marble bench of seats, one struck by a gold blade. Wired into
  `skills/senate-race-report.md`, and into the three reports published before the
  plate existed.

Three mechanics those two builds added. **A reserved panel has to be described as a
prohibition, not as negative space:** "the subject occupies the right third" was
ignored across two passes, because FLUX centres a hero object by default, and the
only thing that worked was naming what must *not* be in the panel (no floor, no
horizon, no reflection, no vignette) and then reshaping the composition to a wide
horizontal band low in the frame, which is a shape the model produces happily.
**Match the existing plate's geometry by measuring it, not by eye:** the Chiefs
plate's cap heights, rule width and insets were read off the file with NumPy and
reused, so the family shares one treatment (Crimson Pro cap height is 0.5732 em,
which converts a desired pixel cap height into a pointsize). **`check-hero-paths.py`
is the cheap gate for this:** a hero path that names no file does not fail the Hugo
build and renders an empty box, so `scripts/check-hero-paths.py` asserts every
`hero_desktop` / `hero_mobile` in `content/` resolves under `static/`, and the
scheduled runners run it.

**A recurring series gets ONE gallery card, and the card resolves to the newest
installment.** A gallery entry holds a fixed `link`, so a series card would keep
pointing at whichever installment happened to be current when it was written, and
would go stale with every new one. Those entries carry `latest` instead:

```yaml
- image: /img/articles/105-senate-race-report_16x9.webp
  title: Senate Race Report
  caption: Fifty seats in the arc. The light reaches one.
  latest: /posts/essays/senate-race-report-*
```

`layouts/_default/gallery.html` resolves the glob at build time, takes the newest
match by `Date`, and pulls the card's image from that post's own `hero_desktop` —
which for a series plate is the same picture every week, so nothing visibly
moves. Do **not** add a gallery entry per installment: the plate is one image, so
a card per week would render the same picture N times. `scripts/check-gallery-pages.py`
guards the globs: a glob pointing at a directory that does not exist fails, and a
glob matching nothing yet is a note rather than a failure (a series that has not
started has no installments, and that is legitimate).

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