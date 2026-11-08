---
description: Start a Radar session - tag and title it, read HANDOFF.md, 5-line summary, then wait for the task
---

Start-of-session routine for the Theme & Group Radar (the same as "Start of every session" in CLAUDE.md):

1. Tag and title this session with the claude-code-remote tools (load them with ToolSearch if needed):
   get_session with no id gives your session id; set_session_tags adds `project:radar`; set_session_title sets a
   title starting "Radar: " (e.g. "Radar: work session (Nov 9)"). Skip this if it is already done.
2. Check the repo goattrader40-lgtm/radar-close-snapshots is here with push access. If it is missing or read-only,
   tell the user at once (claude.ai/connect-github, or a new session with the repo selected) and stop there.
3. `git fetch origin main` and read HANDOFF.md in full as it is on main (your branch may be older).
4. Do what the user used to paste at the start, word for word:

   > Repo: goattrader40-lgtm/radar-close-snapshots. Read HANDOFF.md first and follow its ground rules (no change without
   > my explicit go; test branch first; replay my examples with tools/replay.py --regress; 2-year check; push to main
   > only when I say "go live"). Tell me in 5 short lines what you understood, what is live now and what is open. Then
   > wait for my task.

5. If the user typed something after /start, take it as their task after the 5 lines: "$ARGUMENTS"
   (explain first; nothing changes without their go).
