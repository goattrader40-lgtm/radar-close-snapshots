# Theme & Group Radar: read this first

Claude Code loads this file by itself at the start of every session in this repo (goattrader40-lgtm/radar-close-snapshots).
It holds the start routine, the user's short commands and their ground rules. Everything else is in HANDOFF.md, which
is deliberately not imported here (keep this file short). The user doesn't code: answer in plain English.

## Scheduled runs: skip the routine

If the session's first message comes from a scheduled task (the 8:45 AM pre-market grading, the code-grade check-ins,
any message that lists its own steps or says nobody is watching), do only what that message says: no start routine,
no new tag or title, no waiting for a task. The 8:45 AM grading has its own session: leave it alone.

## Start of every session (the user types /start; any first message counts)

1. Tag and title your own session with the claude-code-remote tools (load them with ToolSearch if needed):
   get_session with no id gives your session id; set_session_tags adds `project:radar`; set_session_title sets a
   title starting "Radar: " (e.g. "Radar: work session (Nov 9)"). Other projects have their own repo and prefix.
2. Check the repo is here with push access. If it is missing or read-only, tell the user at once
   (claude.ai/connect-github, or a new session with the repo selected) before any other work.
3. Read HANDOFF.md in full, as it is on main (`git fetch origin main`; your branch may be older), and follow its
   ground rules (copied below).
4. Tell the user in 5 short lines what you understood, what is live now and what is open.
5. Then wait for their task. If their first message already was a task, give the 5 lines first, then take it as the
   task (explain first: ground rule 1).

## The user's short commands

**Short commands during the session** (what each one means):

| The user says | Claude does |
|---|---|
| "explain first" | the reasoning and the dates/prices it would change, no code |
| "test it" | builds it on a test branch only, replays the examples, shows what changed |
| "2-year check" | runs radar-tools.yml `catalyst` on the test branch, reports the numbers per signal |
| "go live" | pushes to main, rebuilds Launches (picks.yml), checks the result |
| "replay TICKER from DATE to DATE" | tools/replay.py on that stock: what the portal and alerts did each day |
| "add it to the examples" | the agreed read goes into tools/examples.txt and tools/expected_reads.txt |
| "stop" | stops and waits |

## The user's ground rules (word for word from HANDOFF.md: change both together)

1. **No change without an explicit go.** Explain the reasoning first and get it agreed ("dont do anything without
   finalizing rationale"). A question from the user is not a go.
2. **Test before live.** Work on a test branch (`test/...`), replay the agreed examples (`tools/replay.py --regress`),
   report, then wait for the go. Pushing to `main` is going live: only when the user says so ("go live").
   **The 2-year check only when the user changes a main pattern, a buy point or adds a new rule — and ask first, with
   the reason it's needed** (Nov 1 2026: "next time ask me, and tell me the reason why we should do it"). Not for
   thresholds of the list, the table, alerts or the off-list rules.
3. **Never change the Launches design while fixing something else** (the Watchlist, the portal...). Say what a change
   would touch before making it.
4. The ntfy topic is private: it is in the `NTFY_TOPIC` secret only. Never write it in a file, a commit or a message.
5. Don't work around a permission denial; tell the user and let them decide.
6. Commits: end with the attribution lines the session gives; no model names anywhere else.
6b. **The rules workbook follows the code**: any change to a rule, a threshold, a buy point, an alert or the grading
   updates `rules/make_rules.py` and re-runs it (`python3 rules/make_rules.py`) in the same commit, so
   `rules/scanner_rules.xlsx` and `rules/SCANNER_RULES.md` always match what is live (the user, Nov 2 2026).
7. How the user trades: enters only on a break of the 5-minute opening-range high; stop under the day's low. Launches
   (and catalyst launches) are for tracking a stock and finding the best entry: a breakout or a pullback.
8. How the user talks: short numbered feedback with dates, prices and chart screenshots. Answer point by point with
   dates and prices, in plain words, and say which of their reads the code matches and which it doesn't.

## End of every session (the user types /wrapup)

/wrapup runs the user's 4 wrap-up steps and moves status sections older than the last 2 sessions to
HANDOFF_ARCHIVE.md (.claude/commands/wrapup.md). Suggest it yourself when the conversation has been compacted, when
you catch yourself asking again about agreed things, or after one topic or one working day (roughly 30-50 of the
user's messages).

After each "go live", add the change to this session's own status section in HANDOFF.md right away (create the
section, as /wrapup describes, at the first go live), so nothing is lost if the session ends early; /wrapup completes
it. No separate "LIVE …" sections.

The handoff reminder (a Stop hook: .claude/hooks/handoff_reminder.py) speaks up when this session changed code or data
after HANDOFF.md was last updated. If it does: a change just went live, or we are wrapping up -> update HANDOFF.md
now; work still only on a test branch -> don't touch HANDOFF.md, just end your reply with one short line asking the
user to type /wrapup before they leave.

## Where things are

- **HANDOFF.md**: read it in full at the start. The latest session's status, the system and its jobs, how to check a
  change, what the user agreed (with their examples), open items.
- **HANDOFF_ARCHIVE.md**: older session notes and every past change, unchanged, with a one-line index at the top.
  Don't read it all: search it (`grep -n "word" HANDOFF_ARCHIVE.md`) for why and when something was decided, and
  always before telling the user something wasn't agreed or proposing a change in an area it covers.
- **rules/SCANNER_RULES.md** (and rules/scanner_rules.xlsx): every live rule, kept in step with the code (rule 6b).
- **The code comments** carry the same rules with the user's examples (scanner/launch.py, scanner/run.py,
  radar/alerts.py); the portal legend (docs/index.html) shows them to the user.
- **docs/** is the public portal (GitHub Pages): no notes, logs or secrets there.
