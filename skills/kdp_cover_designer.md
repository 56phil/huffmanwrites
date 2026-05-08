# Skill: KDP Cover Designer

This skill manages the iterative design of book covers for KDP (6x9), specifically focusing on the "Unstuck" wraparound design.

## Capability
The agent can perform precise visual adjustments to the cover by manipulating the `BookCoverGenerator` class in `scripts/cover_generator.py`.

## Key Control Parameters
- **Author Positioning**: 
  - `author_bottom_margin`: Distance in inches from the bottom trim edge.
  - `author_font_size`: Pixel size of the author's name.
- **The "Crack" (Artistic Stroke)**:
  - Controlled via `crack_points`. Each point is `(section, x_offset, y_inches, width)`.
  - `section`: 'back', 'spine', or 'front'.
  - `y_inches`: Height from the top edge (increase to move lower).
  - `width`: Thickness of the stroke at that point.
- **Colors**:
  - Found in `self.colors` (e.g., `ACCENT` for the orange, `SUBTITLE` for the cyan).

## Workflow
1. **Modify**: Edit the attributes in `scripts/cover_generator.py`.
2. **Render**: Execute `python3 scripts/cover_generator.py`.
3. **Crop**: Use `magick` to extract the front cover for preview:
   `magick unstuck_cover_v2.png -crop 1750x2775+1980+0 unstuck_front_cover.jpg`

## Common Requests
- "Move the orange stroke down by 0.5 inches" $\rightarrow$ Add 0.5 to all `y_inches` in `crack_points`.
- "Make the author's name larger" $\rightarrow$ Increase `author_font_size`.
- "Change the subtitle color to gold" $\rightarrow$ Update `self.colors['SUBTITLE']`.
