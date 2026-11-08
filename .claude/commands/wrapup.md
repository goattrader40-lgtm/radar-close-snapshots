---
description: End a Radar session - update HANDOFF.md, archive old sections, commit and push, 5-line summary
---

The user's end-of-session steps, word for word (what they used to paste):

> We're wrapping up. 1) Update HANDOFF.md with what we changed and agreed today (rules with my example dates, what is
> live, what is only on the test branch, open items). 2) If I agreed new reads, add them to tools/examples.txt and
> rewrite tools/expected_reads.txt. 3) Commit and push that (docs and tools only), and check nothing is left
> uncommitted. 4) Give me a 5-line summary: live, test only, open.

How to do it so HANDOFF.md stays small:

A. Step 1: write this session as ONE section just under "Session routine", titled
   `## Status at the end of the session "<this session's title>" (<dates>)`: each change with its branch and the
   user's go, the rules with the user's example dates, live / test only, answered with no change, open items, first
   things to check. It may already exist (CLAUDE.md: each "go live" is added to it right away): complete it. Don't
   add separate "LIVE …" sections any more. If the ground rules or the short commands changed,
   change them in CLAUDE.md too (it holds word-for-word copies). Do step 2, then commit this update (step 3's commit).

B. Then move the old sections to HANDOFF_ARCHIVE.md, in a second commit:
   - Keep the status sections of the last 2 sessions (this one and the one before). Move every older dated section:
     "Status …" and "LIVE …" / "live …" change notes. Never move: the header, Session routine, The user's ground
     rules, The system, Checking a change, the two "What the user agreed" sections, Open items, and any section that
     Open items says to keep for now (e.g. the code grade section until the Nov 18 check-in has run).
   - Before moving a section, read it for anything still open, not decided or "to check", and give each a one-line
     pointer in Open items (what it is + the archive section's name in brackets). Pointers, not copies. Drop pointers
     that are done.
   - Move each section unchanged, byte for byte: cut it from HANDOFF.md and paste it at the top of the archive's
     sections (right under the index), keeping the order they had in HANDOFF.md; add one index line per section at
     the top of the index (`- <date> · <title>`).
   - Prove nothing was lost: `python3 .claude/scripts/handoff_check.py` (compares the files on disk with the last
     commit). It must end with "RESULT: OK, nothing lost": 0 lines lost, 0 duplicates, every moved section byte for
     byte in the archive. The only new lines allowed are the index lines, the pointers and blank lines. If it fails,
     fix it before committing.
   - If nothing is older than the last 2 sessions, skip B and say so.

C. Push both commits (docs only), check `git status` shows nothing uncommitted, and in the 5-line summary add the
   handoff's new size and the check's result in one line.
