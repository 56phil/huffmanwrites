#!/bin/bash
# Copy that belongs to ONE SITREP edition and to no other.
#
# The runner sources this and appends whatever it prints for today's date to the
# writer's prompt; the normal case is that it prints nothing.
#
# Why here and not in skills/daily-sitrep.md: the skill is read on every run, so
# a verse written into it would be requested again every morning for the rest of
# an open-ended daily series. A dated case cannot outlive its date, and it can be
# exercised without running the job — `bash scripts/sitrep-edition-note.sh
# 2026-11-01` prints the note, `... 2026-11-02` prints nothing. Tested in
# TestSitrepEditionNote (scripts/test_gates.py), which pins both the copy and the
# fact that it stops after its own date.
#
# Keep the note in the writer's own terms: what to print, where, verbatim, and
# what would break it. A note may name a figure when the figure is the THING TO
# BE CHECKED — the 2026-11-08 note carries two snapshots of one county batch and
# tells the writer not to copy either. It may never be the licence to assert:
# the fetched page is. Anything written here has to be re-read at its source
# before it reaches a published sentence.
sitrep_edition_note() {
    case "${1:-}" in
        2026-11-01)
            cat <<'NOTE'
One addition to today's edition, and it is Philip's copy rather than report
material. Print this haiku verbatim, directly after the lede paragraph:

The clock steps backward —
dark arrives before dinner,
light waits for morning.

Rules for it. Do not edit a word of it, do not give it a title, do not put it in
quotation marks, do not attribute or link it, and do not explain it afterwards —
it is set against the day the clocks went back to standard time, which is the
date it carries. **Preserve the three lines.** In Markdown that means a block
whose line breaks survive: end every line except the last with two spaces, or set
it in a fenced block. A bare newline collapses into one line and the 5-7-5
disappears. Do not fold it into a sentence, and do not let it displace the lede:
the day's news still opens the piece.
NOTE
            ;;
        2026-11-08)
            cat <<'NOTE'
One correction to make in today's edition, in the Mississippi passage, and the
figures below are what to CHECK rather than anything to copy.

Yesterday's edition put AP's count at 5:30 p.m. ET on November 6 at a 2,498-vote
lead on 953,222 votes counted. The snapshot the outlets have carried ever since
— MS NOW, ABC, WAPT and WLBT, all reading AP — is 2,574 on 953,314 from an
update timestamped 5:02 p.m.: Colom 467,930, Hyde-Smith 465,356, Pinkins
20,028, 97 percent of the expected vote in. The difference is probably which
batch a tracker had loaded rather than a miscount, but a reader comparing two
editions sees two numbers for one evening, and the timestamp is what separates
them.

Do three things. Read the count off the fetched page, never off this note, and
give the snapshot's own timestamp alongside the margin rather than the hour you
happened to look. If no new batch has posted, say so plainly: "no votes have
been posted since Friday evening" is the fact, and a headline that the lead
widened hides it. And if you cite a change from yesterday, name both snapshots,
so a movement reads as movement and a restatement reads as a restatement.

The calendar is the story and it has not moved: mail and affidavit ballots must
be received or cured by 5 p.m. on Tuesday, November 10; counties certify by
November 13; Mississippi has no recount law; a plurality wins; the race is
uncalled.
NOTE
            ;;
    esac
}

# CLI: print the note for the date given (empty when there is none).
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    sitrep_edition_note "${1:-}"
fi
