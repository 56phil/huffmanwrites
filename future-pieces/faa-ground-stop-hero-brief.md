# Hero brief — "The Blank Reason Field"

Target: `future-pieces/faa-ground-stop-the-blank-field.md` → `content/posts/essays/the-blank-reason-field.md` on publication.

Plate number: **161** (160 is `cheapest-boundary`). Files: `static/img/articles/161-blank-reason-field_16x9.webp` and `…_4x5.webp`, each duplicated byte-identically into `assets/img/articles/`.

## The concept, and why this one

The essay's spine is a document that states no cause and a cancellation that leaves the field empty, followed by a cause that turns out to be a schedule nobody had integrated. The image must carry *the blank where the reason goes*, not aviation.

**The subject is a single upright slab of white Parian marble, cut as a ledger page.** Its face is incised with fine horizontal grooves, the ruled rows of a record with nothing yet written in them. Low on the face, one rectangular recess is cut deeper than the rest: empty, uninscribed, and the only place the amber light gathers. A hairline seam of gold runs out of that recess across the stone and stops.

Nothing in the frame is a machine, an aircraft, or a screen. The blank is the subject; the light is what fills it.

**Hard prohibition on letterforms.** FLUX garbles glyphs, and this image asks for a page that has none. The prompt forbids text, letters, numerals, symbols, and "writing" as an object, and the ruled grooves are the only structure. Do not composite a wordmark: unlike the Chiefs plate, this one is a single essay and carries no type.

## Prompt — desktop (16:9)

> A single upright slab of white Parian marble, cut as the page of a ledger, photographed in deep midnight-navy darkness. Its face is ruled with very fine horizontal grooves, close and even, extending edge to edge across the stone. Low on the face and slightly left of centre, one shallow rectangular recess is cut deeper than the ruled surface; it is empty and uncarved, and warm amber-gold light pools inside it and spills a short distance across the grooves. A hairline seam of gold runs from the recess toward the right edge of the slab and stops before reaching it. Dramatic chiaroscuro, one light source, the stone's own veining and grain visible where the light strikes, the marble surface matte rather than glossy. The slab occupies the left two thirds of the frame and stands in an empty void. No text, no letters, no numerals, no symbols, no inscriptions, no writing of any kind, no paper, no screen, no machinery, no aircraft, no people, no horizon, no floor, no reflection, no vignette, no frame, no border.

## Prompt — mobile (4:5)

> A single upright slab of white Parian marble, cut as the page of a ledger, seen closer and from slightly below, filling the lower two thirds of a tall frame in deep midnight-navy darkness. Fine horizontal grooves are ruled across its face and continue past the edges of the image. One shallow rectangular recess, cut deeper than the grooves, sits just above the centre line; it is empty and uncarved, and warm amber-gold light rises out of it. A hairline seam of gold runs from the recess downward into the grooves and stops. Deep shadow above the slab, the stone's veining lit from one side, matte finish, strong contrast. No text, no letters, no numerals, no symbols, no inscriptions, no writing of any kind, no paper, no screen, no machinery, no aircraft, no people, no horizon, no reflection, no vignette, no border.

Both prompts keep the composition to a **wide horizontal band low in the frame**, because a reserved area described as negative space is ignored, and the only thing that reliably clears space is naming what must not enter it. Here the reserved area is the darkness above the slab, and the prohibitions name the things that would fill it.

## Generate

```bash
# 16:9 — 1536x1024, then 4:5 — 1024x1280 (the 4:5 routinely exceeds 120 s; re-run rather than shrink)
# tool: generate_image, prompt above, one call per ratio
```

Then grade the ground onto the house navy. FLUX returns "midnight navy" as near-black; the grade is a measurement, not an impression:

```bash
python3 scripts/grade-hero-navy.py /tmp/raw-16x9.png static/img/articles/161-blank-reason-field_16x9.webp
python3 scripts/grade-hero-navy.py /tmp/raw-4x5.png  static/img/articles/161-blank-reason-field_4x5.webp
```

The script prints the shadow mean before and after; expect roughly `(4, 4, 5)` → near `(19, 30, 57)`. Nothing above the luminance threshold is touched, so the marble keeps the light the model gave it.

Duplicate into `assets/` (both homes are read, and `check-hero-paths.py` fails a mismatch):

```bash
cp static/img/articles/161-blank-reason-field_*.webp assets/img/articles/
```

## Frontmatter to wire

```yaml
hero_desktop: "img/articles/161-blank-reason-field_16x9.webp"
hero_mobile: "img/articles/161-blank-reason-field_4x5.webp"
hero_alt: "An upright slab of white marble carved as a ruled ledger page, its rows empty, with one deep rectangular recess low on the face holding a pool of amber light and a hairline gold seam running from it across the stone, all against a near-black navy darkness."
hero_caption: "The order named no cause. The page kept the space for one, and the light found it first."
```

## Verify before publishing

1. `python3 scripts/check-hero-paths.py` — both paths resolve under `static/` and the copies in `assets/` match byte for byte.
2. Read the 16:9 in the browser at its rendered width: the recess must be visible without scrolling and the slab's top edge must not collide with the header.
3. Confirm no glyphs survived generation anywhere on the slab. If any appeared, regenerate rather than retouch; a plausible-looking half-letter on the marble is the same class of defect as a fabricated citation.
4. The caption says *space*, not *cause*, because the essay's claim is that the field was left for a reason and the reason arrived late. Do not let the caption promise the essay resolves what the record does not.

## Where it goes on the site

One essay, one hero, one gallery entry — not a series plate:

```yaml
- image: /img/articles/161-blank-reason-field_16x9.webp
  title: The Blank Reason Field
  caption: The light gathers where the reason was left out.
  link: /posts/essays/the-blank-reason-field/
```

## Shipped — 15NOV26

- **Both plates generated** through fal (`fal-ai/flux/dev`) after four compositional attempts. The model would not remove the ground plane: every prompt that forbade a floor produced a slab standing on a dark surface anyway, so the pair accepts the surface rather than fighting it, which is what plate 160 does as well ("stand on a polished marble floor"). The slab is lit as a museum object, not as an object in a room.
- **The hairline gold seam did not render** in either frame. The lit empty niche carries the meaning alone, and nothing was retouched to add what the model would not draw.
- **Graded as measured**, not as intended. Shadow mean before → after, against the `(19, 30, 57)` target: 16:9 `(2.7, 2.6, 1.3)` → `(18.1, 28.5, 53.9)`; 4:5 `(2.4, 2.3, 1.5)` → `(18.1, 28.6, 54.2)`. The stone keeps the light the model gave it, because the grade touches nothing above the luminance threshold.
- **Files:** `static/img/articles/161-blank-reason-field_16x9.webp` (1536×1024) and `…_4x5.webp` (1024×1280), each copied byte-identically into `assets/img/articles/`. Frontmatter wired in the draft; `draft: true` stands until the piece is published.
- **The gallery entry is deliberately not added yet.** A card pointing at `/posts/essays/the-blank-reason-field/` before that page exists would be a dead end dressed as a link. Add it in the same commit that publishes the essay.
