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
# what would break it. Nothing here is a fact, so nothing here needs a source.
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
    esac
}

# CLI: print the note for the date given (empty when there is none).
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    sitrep_edition_note "${1:-}"
fi
