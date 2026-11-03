# The Musk Money: what $158 million bought

Philip, 2026-11-02: "Elon Musk spent a large amount of money on the midterm
election. After the dust settles, I want to publish a piece on that."

Status: brief, not a draft. Nothing here is publishable prose. It records the
subject, the material the corpus already holds, the one date on which the
money stops moving, and the shape the piece should take. Written before the
election because the sourcing decision has to be made before the numbers
arrive, not after.

---

## Wait for the filing, not for the dust

"Dust settles" has a date. Verified today at the FEC's own deadlines page:

| Report | Period covered | Due |
|---|---|---|
| Pre-General | 10/01/2026 – 10/14/2026 | 10/22/2026 (already filed) |
| **Post-General** | 10/15/2026 – **11/23/2026** | **12/03/2026** |

So the cycle total for any committee does not exist until **December 3, 2026**.
Before that date a piece about "how much he spent" rests on press tallies that
will be superseded within the week, and the corpus's own rule applies: a figure
that changes after publication is a figure the reader cannot check.

The window is therefore **December 4 through roughly December 12**. Publish
inside it. After mid-December the story is a month old and the numbers have
been re-reported everywhere, which is the point at which the piece stops being
worth writing.

Two things are visible earlier and do not need the post-general report:
**24- and 48-hour independent-expenditure notices**, which report spending as
it happens. Those give the shape of the last three weeks and are worth
collecting continuously from now, because they are the only evidence of what
the money did in the final stretch.

---

## What the corpus already says, with citations

Do not re-report these as new. Link them; the piece's job is the total and the
verdict, not the discovery of the contributions.

| Fact | Where it is already published |
|---|---|
| America PAC spent nearly $250,000 on September 4, its first spending of the cycle | `senate-race-report-2026-09-06.md`[^4], citing the Texas Tribune |
| Musk gave **$158 million** to the Senate Leadership Fund in September, and the fund transferred **$158 million** to Texas PAC, the super PAC supporting Paxton | `senate-race-report-2026-10-18.md`[^16], citing Jesse Bedayn, AP, via PBS NewsHour, October 16, 2026 |
| Republican Senate super PACs at roughly $323 million against $116 million Democratic, more than $440 million total across the battleground | same report, footnote 36 |

The $158 million in and $158 million out is the single most interesting fact
already on the record, and it is the one the piece should be built on: money
entered a committee and left it the same size, for one state.

## What the corpus does not have, and the piece must fetch

- The **cycle total** across every vehicle Musk is connected to: America PAC,
  the Senate Leadership Fund contribution, and anything else the filings
  disclose. Do not assume the press's "$X million" figure; read it off
  Schedule A of each committee.
- Whether the September contribution was the **largest single individual
  contribution** of the 2026 cycle, and if not, what was.
- The **cost per vote** in the races the money entered, against the 2022 and
  2024 midterm comparables.
- What the money **bought**: the called result in each race it entered. This is
  the piece's verdict and it cannot be written until the last race is called,
  which for Texas and Alaska may be well after December 3. If a race is still
  uncalled when the window opens, the piece reports the uncalled state and says
  so; it does not project.

---

## The collector this needs (prerequisite)

The repo's rule for a data-driven piece is a collector, not a writer's memory:
`scripts/sitrep-pack.py` and `scripts/chiefs-report.py` exist for exactly this
reason, and a November 2026 SITREP already ran with a number the writer could
not have recalled.

Proposed: `scripts/fec-spending-pack.py`, printing, for a named committee:

1. Committee identity and registration from the FEC's committee endpoint.
2. Schedule A itemized receipts over a threshold, with contributor name and
   date, so the $158 million is a filing line and not a press sentence.
3. Schedule B disbursements, which is where the Senate Leadership Fund's
   transfer to Texas PAC appears.
4. Schedule E independent expenditures by race and by support/oppose.
5. Coverage count, per the repo's gate rule: a pack that inspected nothing must
   say so.

**Blocker: there is no FEC credential.** `scripts/check-secrets.py` carries five
(fal, SendFox, Ollama, Firecrawl, CourtListener) and no FEC key. `api.open.fec.gov`
requires one, free, from api.data.gov, registered to an email address. This is
Philip's signup, not something a session can do. When it exists:

- store it as keychain `huffmanwrites-fec`, variable `FEC_API_KEY`, with
  `~/.secrets` as the fallback home;
- add it to `check-secrets.py`'s list, with a probe that distinguishes live from
  stale (the FEC API answers `403` with `API_KEY_MISSING`/`API_KEY_INVALID` for
  a bad key and `200` for a good one, so the probe is cheap and definitive);
- then the pack, then the piece.

Until that key exists, the piece cannot be written to the corpus's standard, and
the honest fallback is to cite the AP/PBS reporting already in the corpus and
say the total is not yet knowable. Do not aggregate from press tallies and
present the sum as a filing figure.

---

## Three angles; pick one before drafting

**1. The coat check.** $158 million enters the Senate Leadership Fund and $158
million leaves it for a single state's super PAC. The intermediary changed
nothing about the money and everything about who is answerable for it. This is
the angle that fits the corpus's existing work: `two-things-called-seneca.md`
is about what a name is worth once it can be bought, and this is the same
question asked of a committee. Strongest of the three, and the one the evidence
already supports.

**2. The price of a seat.** Cost per vote, against 2022 and 2024. Cold,
arithmetical, and it needs the post-general filings to say anything at all. Its
weakness is that a reader learns a number, not a thing.

**3. The purchase order.** What the money asked for, and what it got. Ties to
`elon-musk-and-the-engineering-of-chaos.md` without re-arguing DOGE: the DOGE
piece is about administration, this would be about election. Its weakness is
that it depends on the races being called, which may not be true in the window.

The brief's recommendation is **1, with 3's closing verdict if the results are
in**. Angle 2 becomes a table inside it rather than the spine.

---

## House rules that will bite this piece

- **Em-dashes: no more than three** in the prose written. Check with
  `python3 scripts/check-emdashes.py --file <path>`.
- **No sentence ends in a preposition**, including `title`, `description` and
  `hero_caption`. `check-prepositions.py --file`.
- **No figure recalled.** Every number is printed by the pack or fetched and
  linked. A wrong number here is a claim about a named person's money.
- **Quotations:** any direct quotation of Musk, a committee filing, or a
  spokesperson carries a link containing the quoted wording, verified by
  fetching it. `check-quotes.py --file`, and `--online` before publishing.
- **Anchors name the thing cited.** No `[text]`, no `[here]`.
- **Never construct a URL.** Fetch it or cite without a link.
- Closing attribution: `*PRH | [huffmanwrites.org](https://www.huffmanwrites.org) | © Philip Huffman*`.
- Frontmatter: `lastmod` required; `featuredOnHome: true` if it should reach
  the home feed (it should).

## Hero image

Next unused number is **145**: `145-musk-midterm-money_{16x9,4x5}.webp`, both
homes (`static/img/articles/` and `assets/img/articles/`, byte-identical), the
locked aesthetic (Parian marble, `#131E39`, gold `#D4820A`, chiaroscuro,
conceptual not literal). A concept that fails the "renders as a machine" test
is a box or a stack of bills; the working metaphor is a **ledger** or a
**marble balance** rather than currency.
