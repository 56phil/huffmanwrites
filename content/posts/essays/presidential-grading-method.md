---
title: "Presidential Grading: Method and Findings"
description: "A reproducible method for grading all 44 presidents on C-SPAN's ten leadership characteristics: the rubric stated, the ten-character profile string that encodes each president, the three checks that validated the data, and the measurements showing where weighting changes the answer and where it cannot."
date: 2026-09-22T16:40:00Z
author: Philip Huffman
lastmod: 2026-09-22T16:40:00Z
featuredOnHome: true
hero_desktop: "img/articles/93-grading-profile_16x9.webp"
hero_mobile: "img/articles/93-grading-profile_4x5.webp"
hero_alt: "Ten tall rectangular slabs of veined white Parian marble standing in a symmetrical arch in a deep midnight navy void, their tops rising to four distinct heights, warm amber-gold light glowing along their bases and pooling on the polished reflective floor, gold dust motes and dim stars above; every marble surface is blank and unmarked"
hero_caption: "Ten slabs, four heights. The profile is not the man. It is the man under a stated rubric."
tags:
  - civics
  - history
  - presidency
  - methodology
  - data
draft: false
---

I have graded all forty-four presidents, and I want to show the work.

What follows is the whole method, written out so that someone else can reproduce it, attack it, and see exactly where my judgment enters. The short version: the letter grades are mine, and the underlying scores are not. Every number below comes from C-SPAN's 2021 Historians Survey, and the transcription was checked three independent ways before I used any of it.

The reason to write it down is that a ranking presented as a bare list is unfalsifiable. You can disagree with it; you cannot check it. A ranking presented with its rubric lets you find the exact cut point where you would have decided differently, which is the only useful thing to learn from a disagreement of this kind.

One more thing before the method. The point of this exercise is not to produce a better number than C-SPAN's. It is to produce a number that can be argued with in public, and to be honest about which parts of it are arithmetic and which parts are me.

---

## 1. Provenance

| Item | Value |
|---|---|
| Source | C-SPAN Historians Survey of Presidential Leadership, 2021 (the 4th) |
| Released | 2021-06-30 |
| Participants | 142 historians and professional observers of the presidency |
| Presidents scored | 44 |
| Characteristics | 10, each rated 1 ("not effective") to 10 ("very effective") |
| Published form | Per-president category scores on a 0–100 rescaled axis, plus an overall score |
| Advisers | Douglas Brinkley, Edna Greene Medford, Richard Norton Smith (all four surveys); Amity Shlaes (joined 2021) |
| Data consultant | Robert X. Browning, C-SPAN Archives |

C-SPAN scores each president on ten characteristics and publishes both the
per-category scores and an overall figure. The overall figure is the equal-weighted
mean of the ten categories, which is what made the transcription checkable (§3).

This is **not** a primary-source assessment. It is a re-reading and re-grading of
expert judgments. Every factual claim underneath belongs to the 142 respondents;
only the grades, the weighting argument, and the analysis are the author's.

---

## 2. The ten characteristics

In C-SPAN's published order, which is the order used throughout this document and
in every profile string. Position matters; the string is read positionally.

| # | Characteristic | Abbrev. |
|---|---|---|
| 1 | Public Persuasion | P |
| 2 | Crisis Leadership | C |
| 3 | Economic Management | E |
| 4 | Moral Authority | M |
| 5 | International Relations | I |
| 6 | Administrative Skills | A |
| 7 | Relations with Congress | G |
| 8 | Vision / Setting an Agenda | V |
| 9 | Pursued Equal Justice for All | J |
| 10 | Performance Within Context of Times | T |

---

## 3. Transcription validation

The per-category scores were transcribed from C-SPAN's published tables. Before
any analysis, three independent checks were run against C-SPAN's own published
numbers.

**Check 1, arithmetic.** C-SPAN publishes each president's category scores and an
overall score equal to their mean. If the transcription is right, the ten values
must sum to that published overall figure.

```
43 of 44 presidents: sum of ten categories == published overall score
 1 exception: Monroe, 643.6 transcribed vs 643 published
              (0.09%, inside C-SPAN's own rounding; does not cross a grade band
               at any cut point, so Monroe's grades are unaffected)
```

**Check 2, order.** Independently of the arithmetic, the ranking implied by the
transcribed scores was compared against C-SPAN's published overall ranking.

```
44 of 44 rank-order agreement
```

**Check 3, independent re-fetch.** A later copy of C-SPAN's live results page was
fetched and parsed from scratch, with no reuse of the original transcription. The
ten category scores were then compared score by score.

```
42 of 44 presidents: all ten category scores reproduced exactly
 2 exceptions: name-format differences in the page's markup, not score differences
0 profile strings disagreed
```

Three independent checks passing is the basis for treating the dataset as faithful.
Every figure in this paper is reproducible from the C-SPAN source tables.

---

## 4. The grading scale

Each of a president's ten published scores is converted to one of four numbers:

| Grade | Label | Score band |
|---|---|---|
| 4 | superior | ≥ 85 |
| 3 | satisfactory | 70 – 84.9 |
| 2 | adequate | 55 – 69.9 |
| 1 | unsatisfactory | < 55 |

**The cut points are a choice.** They are not in C-SPAN and not in any standard.
They are stated here so they can be argued with. Sensitivity was tested: moving the
cuts to 90/75/60 or 80/65/50 leaves the ordering correlated at 0.99 and 0.98
respectively, and at no cut setting tested does the membership of the top four change.

**The bands are structurally unequal.** Bands 4, 3, and 2 are 15 points wide; band 1
spans 55 points. Consequence: 26.7 points of real C-SPAN difference collapse into a
single grade at the bottom, while 15 points separate a 3 from a 4. This is the
single largest artifact introduced by the grading scheme, and §7 discusses it.

---

## 5. The profile string

Each president is represented as a ten-character string of digits 1–4, in the
category order of §2.

```
Kennedy    3322222333
Reagan     4222312313
Eisenhower 3333333223
Obama      3223221332
Lincoln    4434343444
```

Read positionally: the first digit is Public Persuasion, the second Crisis
Leadership, and so on. `4222312313` says Reagan graded 4 on persuasion, 2 on crisis
leadership, and 1 on moral authority and equal justice.

**The string is not unique.** Of 44 presidents there are 29 distinct strings:

| String | Shared by |
|---|---|
| `1111111111` | 14 presidents (Buchanan, A. Johnson, Harding, G. W. Bush, Trump, Van Buren, Harrison W. H., Tyler, Taylor, Fillmore, Pierce, Hayes, Arthur, Harrison B.) |
| `2222222212` | Madison, McKinley |
| `1112111111` | Ford, Garfield |

Fourteen presidents receive all ten grades identical. That is a property of the
scale, not an error: 26.7 points of spread fit inside band 1.

**The string is not a hash of the man.** It is a hash of a man *under a stated
rubric*. Two profiles are comparable only if the same cut points and the same
category order produced them. Uniqueness was tested as a goal and rejected:
increasing resolution to 9 decile bands does yield 44/44 uniqueness, but under
±1.5 points of plausible scoring noise that uniqueness fails in 25% of trials.
Uniqueness for a 44-item census is a property of the sample, not of the encoding.
The encoding is kept coarse, readable, and tied to a declared rubric.

---

## 6. Sorting

Presidents are sorted by the **mean of the ten grades**, which is the arithmetic
mean of ten integers in 1–4, so its values are always multiples of 0.1.

This is the only use of averaging in the method. It is retained for sorting and for
the compact summary of the ten grades. It is **not** treated as a measure of a
president; §7 tabulates the profiles that the sort collapses.

Sorted order (first ten):

| # | President | Profile | Mean grade | C-SPAN overall |
|---|---|---|---|---|
| 1 | Lincoln | `4434343444` | 3.70 | 89.7 |
| 2 | Washington | `4434433414` | 3.40 | 85.1 |
| 3 | F. D. Roosevelt | `4433433424` | 3.40 | 84.1 |
| 4 | T. Roosevelt | `4333333423` | 3.10 | 78.5 |
| 5 | Eisenhower | `3333333223` | 2.80 | 73.4 |
| 6 | Jefferson | `3322233313` | 2.50 | 70.4 |
| 7 | Kennedy | `3322222333` | 2.50 | 69.9 |
| 8 | Truman | `2323322233` | 2.50 | 71.3 |
| 9 | Obama | `3223221332` | 2.30 | 66.4 |
| 10 | Reagan | `4222312313` | 2.30 | 68.1 |

The mean grade reproduces the C-SPAN ordering at **Spearman 0.94** while using only
17 distinct values across 44 presidents.

---

## 7. What the sorting destroys, and why no order should be quoted alone

**A mean hides which categories earned the grades.** Four examples, in each case
identical by the number and different by the record:

| Mean | Presidents | What the number conceals |
|---|---|---|
| 3.40 | Washington `4434433414`, F. D. Roosevelt `4433433424` | Washington has six 4s and one 1; FDR has five 4s and no 1 |
| 2.50 | Jefferson `3322233313`, Kennedy `3322222333`, Truman `2323322233` | Jefferson's 1 is equal justice; Truman's weakness is persuasion, not governance |
| 2.30 | Obama `3223221332`, Reagan `4222312313` | Reagan has a 4 and two 1s; Obama has neither |
| 2.00 | Monroe `2222322212`, Clinton `3231221222` | Monroe is uniformly adequate; Clinton is uneven and lower-rated |

**A mean rewards flatness and punishes distinction.** The clearest cases of the
grading shifting a president's position relative to C-SPAN's own ordering:

| President | C-SPAN | Graded | Shift | Why |
|---|---|---|---|---|
| G. W. Bush | 29 | 43 | +14 down | All ten grades mediocre and identical; nothing distinguished him upward |
| Buchanan | 44 | 32 | −12 up | Consistently awful but not extremely so; flatness graded better than spikiness |
| Arthur | 30 | 41 | +11 down | Uniformly unremarkable |
| Hoover | 36 | 27 | −9 up | Spiky in the punitive direction; his administrative skill (60.0) survives the band while his economic management (26.2) does not |

A correction to an earlier draft of this analysis: it was claimed that the scale
systematically punishes spikiness. Tested, the correlation between a president's
within-ten spread and his rank shift from grading is only **−0.275**, too weak to
support the general claim. The mechanism is real in the individual cases above, but
it is not a systematic bias of the scale, and any statement to that effect would
have been an over-claim. The flatness reward is better demonstrated by the specific
pairs in the first table of this section than asserted as a rule.

---

## 8. The rubric problem, and the weighting argument

C-SPAN weights its ten characteristics equally, each contributing 1/10 to the
overall figure. The grading inherits that weighting. It was never argued for. It
means **"Pursued Equal Justice for All" counts exactly as much as "Economic
Management,"** which is a substantive position nobody has defended.

The equal weighting also produces a baseline worth naming, because the labels imply
otherwise:

```
mean grade across all 440 ratings (44 presidents x 10) = 1.72
distribution:  4: 5.0%   3: 14.5%   2: 27.5%   1: 53.0%
```

The average president grades **below "adequate."** The labels ("superior /
satisfactory / adequate / unsatisfactory") imply a passing midpoint, but a 1–4
scale with no neutral point has its midpoint at 2.5. The labels and the arithmetic
disagree, and the labels are the ones in the published output. Either band 2 should
be relabelled, or the labels should be treated as ordinal only.

**Weighting is where authorial judgment belongs.** Because the weights are explicit,
they can be varied and the effect measured. Two findings, both reproducible:

**Finding 1: the weights do not move the top.** Across 2,000 random weightings
drawn from a Dirichlet distribution:

```
exact top four = {Lincoln, Washington, F. D. Roosevelt, T. Roosevelt}  1,926 / 2,000
presidents ever entering the top four, across all weightings          9
```

Lincoln is unassailable. Washington and T. Roosevelt can be pushed down, but only
by weightings that zero whole categories, which is no longer a ranking. **For any
defensible rubric the top four is fixed.**

**Finding 2: the weights decide the middle of the table.** This is where authorial
judgment has force, and it is the finding that matters for anyone tempted to argue
with the order:

| Tier (by consensus rank) | Mean places moved by a random rubric | Median | Max |
|---|---|---|---|
| 1–10 | 1.02 | 1.0 | 15 |
| **11–25** | **2.57** | 2.0 | 15 |
| 26–44 | 4.29 | 3.0 | 16 |

The top is stable, the bottom is volatile in a way that mostly reflects how little
the data distinguishes those presidents, and the middle is where a considered
judgment changes the answer.

---

## 9. Charisma: the empirical result

Public Persuasion is the highest-variance characteristic after grading:
**SD 1.065, the largest of the ten, 12.1% of total grade variance.**

Two measurements:

- **Excluding charisma entirely leaves 16 of 44 ranks identical**, measured against
  the graded order. (Against C-SPAN's own order it is 13/44; the two baselines
  differ, so the baseline is named here rather than left implicit.) That makes it the
  most consequential single category to include or omit among the mid-range
  categories. Economic Management is 34/44 against the same baseline, Moral
  Authority 24/44, Equal Justice 27/44.
- **Tripling its weight changes no rank by more than six places.** Reagan moves +3,
  Jackson +6. The top five never move.

Both facts hold at once, and together they are the finding: charisma is
**consequential but not directional.** It matters more than any other single
category, and it moves the order least, because at the extremes it agrees with
everything else: the presidents who scored 4 on persuasion also scored well on
vision, crisis leadership, and the rest.

Where it does bite is the middle: Jackson (persuasion 78.6, relations with Congress
51.9) and Reagan (89.1 and 68.4) are the men whose standing depends on whether mass
persuasion counts as leadership. Charisma is a **tiebreaker in the middle of the
table**, not a driver anywhere.

**A trait the single score conflates.** Public Persuasion (mass) and Relations with
Congress (retail) correlate at only **r = 0.832**, so they are related but not the same ability.
Men who had one and not the other:

| | Mass persuasion | Retail (Congress) | Gap |
|---|---|---|---|
| Obama | 76.3 | 46.9 | **+29.4** |
| Jackson | 78.6 | 51.9 | +26.7 |
| Kennedy | 84.8 | 62.0 | +22.8 |
| L. B. Johnson | 64.1 | 80.7 | **−16.6** |
| Ford | 41.6 | 54.6 | −13.0 |

A single "charisma" score double-counts the men who had both (FDR: 94.8 and 80.5)
and hides the specialists. LBJ is graded 2 on persuasion and 3 on Congress; he was
one of the most effective legislative operators in the office's history.

---

## 10. Summary of the method

1. Take C-SPAN's 2021 per-category scores for all 44 presidents (10 each, 0–100).
2. Validate the transcription twice, against C-SPAN's own published numbers
   (arithmetic and ordering). Both must pass before anything downstream is used.
3. Grade every score on a four-point scale at stated cut points (85/70/55).
4. Emit a ten-character profile string in C-SPAN's category order.
5. Sort by the mean of the ten grades, for ordering and compact summary only.
6. Report the profile alongside any mean, never the mean alone.
7. State all weights; treat the top four as rubric-invariant and the middle as
   judgment-dependent.

## 11. Stated limitations

- **Secondhand.** This re-grades 142 historians' judgments. It is not a reading of
  the primary record, and it inherits every blind spot of that survey, including
  the ones its own participants named. Edna Greene Medford, on the 2021 results:
  *"we still have slaveholding presidents at or near the top of the list."*
- **Time-bounded.** The data predates Biden's presidency and Trump's second term.
- **Recency effects are documented in the source itself.** Richard Norton Smith
  described a "boomerang effect" in which presidents are rated at a nadir just after
  leaving office and rise later; Ulysses S. Grant is the survey's largest mover,
  +13 places between 2000 and 2021.
- **No single-number score should be quoted without its profile.** §7 documents the
  specific instances where the mean states the opposite of the record.
- **The cut points are unargued.** They were chosen to be round. Sensitivity testing
  shows the ordering is robust to them, but a different author could pick others and
  is entitled to.

---

## Sources

All figures in this paper were transcribed from C-SPAN's published tables and then
verified twice: once against C-SPAN's own published totals (§3), and once against a
freshly fetched copy of the live results page, which reproduced all ten category
scores for 42 of 44 presidents exactly. The two remaining presidents differ only in
the name format used by the page, not in their scores.

- C-SPAN. *2021 Historians Survey of Presidential Leadership: Total Scores and
  Overall Rankings.*
  https://www.c-span.org/presidentsurvey2021/
  This is the primary citation. The live page carries the overall scores and all ten
  per-category tables (440 values), which is the dataset this paper grades.
- C-SPAN. *2021 Press Release: C-SPAN Releases Fourth Historians Survey of
  Presidential Leadership*, 2021-06-30. Participant count, advisory panel, and the
  survey's own commentary on category movement.
  https://static.c-span.org/assets/documents/presidentSurvey/2021%20Press%20Release.pdf

**Note on the PDF mirrors.** C-SPAN also publishes the survey as standalone PDFs
(`2021-Survey-Results-Overall.pdf` and `2021-Survey-Results-Category-Rankings.pdf`
under `static.cspanvideo.org`). Those URLs serve a GDPR consent interstitial to
automated requests rather than the file, so they are not cited as the verification
route: a reader following them may land on a consent gate instead of the data. The
HTML results page above is reachable and carries the same figures.

*PRH | [huffmanwrites.org](https://www.huffmanwrites.org/) | © Philip Huffman*
