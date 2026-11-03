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

## The collector

The repo's rule for a data-driven piece is a collector, not a writer's memory:
`scripts/sitrep-pack.py` and `scripts/chiefs-report.py` exist for exactly this
reason, and a November 2026 SITREP already ran with a number the writer could
not have recalled.

Shipped as **`scripts/fec-spending-pack.py`**. Per committee it prints:

1. Committee identity from the FEC's committee endpoint, with a NOTE when the
   registered name does not match the label the piece would use.
2. Form 3X summary filings with `total_receipts` and `total_disbursements` —
   the layer the Post-General report lands in on 2026-12-03.
3. Schedule A itemized receipts filtered strictly to Elon Musk's own names.
4. Schedule E independent expenditures by candidate and support/oppose.
5. A coverage count, per the repo's gate rule: a pack that inspected nothing
   must say so.

**Blocker: resolved 2026-11-02.** Philip supplied the key; it lives in the login
keychain (`huffmanwrites-fec`) and `~/.secrets` (`FEC_API_KEY`), is registered in
`scripts/check-secrets.py` with a live/stale probe (both failure directions are
HTTP 403, separated only by the body's `API_KEY_INVALID` / `API_KEY_MISSING`
code), and `check-secrets.py --online` reports `FEC_API_KEY: authenticates
(HTTP 200)` among six credentials.

The collector is written and runs: **`scripts/fec-spending-pack.py`**. It prints
identity, Form 3X summary filings, Musk's itemized Schedule A receipts and
Schedule E totals per committee, with `SOURCE UNAVAILABLE` for a failed source
and a coverage line. Twelve requests, 508 rows, exit 0.

## What the filings already say, read on 2026-11-02

Committee ids below were reached by query and verified against the committee's
own record. None of them is recalled.

| Committee | Id | Registered name | Q3 2026 receipts |
|---|---|---|---|
| America PAC | C00879510 | AMERICA PAC, Austin TX | $88,866,369 |
| Senate Leadership Fund | C00571703 | **SLF PAC**, Washington DC | $272,944,767 |
| Texas PAC | C00960211 | TEXAS PAC, Austin TX | **$158,000,000** |

- **The $158 million is on a filing**, as Texas PAC's Q3 Form 3X `total_receipts`,
  filed 2026-10-15. Its summary disbursements were $131,751,387.
- **The payer is not itemized yet.** Texas PAC's Schedule A returns **zero rows**
  in the API while its summary reports $158 million, so the piece can say the
  filing reports the receipt but cannot yet name who sent it.
- **The corpus's AP-sourced sentence does not check out itemized today.**
  `senate-race-report-2026-10-18.md` says Musk gave $158 million to the Senate
  Leadership Fund; SLF PAC's Schedule A holds **two** Musk receipts totalling
  **$10,000,000**, dated June 27 and December 15, 2025. A $158 million receipt
  could sit inside its $272,944,767 Q3 summary with the itemization lagging, but
  that is a hypothesis, not a finding. **Re-check this before the piece leans on
  it**, and correct the earlier report under the corpus correction rule if the
  filing shows something else.
- **America PAC's Musk money is older than the campaign.** $50,326,939 across 23
  itemized rows, the last dated 2026-06-30. Its independent expenditures are the
  live part: 4,063 Schedule E rows this cycle, with the 10/26–10/30 window alone
  carrying $12.6 million against Talarico.
- **Texas PAC's independent expenditures total $181,850,225** across 56 rows
  (9/11–10/26): $112,153,742 against Talarico, $69,696,483 for Paxton.

**One error this pack caught in its own first draft, worth keeping in the
record.** The Senate Leadership Fund does not appear in the FEC's committee name
index; a Schedule A row naming it as a contributor returned `C00694323`, and that
committee is **WINRED**, the conduit, not the fund. The real id came from the
same rows' `contributor_id` field. The pack now prints a NOTE when a committee's
registered name does not contain the label expected, which is what surfaced the
mistake.

**And a filter that would have inflated the number.** The API's
`contributor_name` filter is a substring match: `MUSK` returns MUSKAR, MUSKE,
MUSKER and MUSKETT. On SLF PAC, 166 rows matched and 2 were Elon Musk. The pack
filters locally and prints the server's count beside the strict one.

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
