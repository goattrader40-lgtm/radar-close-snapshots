#!/usr/bin/env python3
"""Stop hook: remind Claude to update HANDOFF.md when this session changed code or data after the handoff.

Claude Code runs this at the end of every reply (that is what "Stop" means), with a small JSON on stdin.
It speaks up (by asking Claude to continue once, with a reminder) only when all of these hold:
  - this is not already a reminder round (stop_hook_active is false: never twice in a row);
  - this session changed files other than the handoff files, either not yet committed or in commits that carry
    this session's id (the "Claude-Session: ..." line), and those changes are newer than the session's last commit
    to HANDOFF.md (nightly robot commits and other sessions' commits don't count);
  - HANDOFF.md isn't being edited right now (not modified on disk);
  - it hasn't already reminded about this same batch of changes.
Anything unexpected (no git, a bad input, a timeout): it stays silent. It never stops a session.
"""
import hashlib, json, os, subprocess, sys

HANDOFF_FILES = {"HANDOFF.md", "HANDOFF_ARCHIVE.md", "CLAUDE.md", "README.md"}


def is_handoff(path):
    return path in HANDOFF_FILES or path.startswith(".claude/")


def git(root, *args):
    r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, timeout=8)
    if r.returncode:
        raise RuntimeError(r.stderr.strip())
    return r.stdout


def session_tag():
    """The part of this cloud session's id that also appears in its commits' Claude-Session line."""
    sid = os.environ.get("CLAUDE_CODE_REMOTE_SESSION_ID", "")  # e.g. cse_01Pk...; commits say session_01Pk...
    tail = sid.split("_", 1)[1] if "_" in sid else ""
    return tail if len(tail) >= 12 else ""


def pending_changes(root):
    """Files this session changed after its last HANDOFF.md update, and whether HANDOFF.md is being edited now."""
    files, handoff_dirty = set(), False
    for line in git(root, "status", "--porcelain", "--untracked-files=all").splitlines():
        path = line[3:].split(" -> ")[-1].strip().strip('"')
        if path == "HANDOFF.md":
            handoff_dirty = True
        elif not is_handoff(path):
            files.add(path)
    tag, commits = session_tag(), []
    if tag:
        out = git(root, "log", "--all", f"--grep={tag}", "--fixed-strings", "--format=@%H %ct", "--name-only")
        for line in out.splitlines():
            if line.startswith("@"):
                h, ct = line[1:].split()
                commits.append([h, int(ct), set()])
            elif line.strip() and commits:
                commits[-1][2].add(line.strip())
    last_handoff = max((ct for _, ct, fs in commits if "HANDOFF.md" in fs), default=0)
    newer = sorted(h for h, ct, fs in commits if ct > last_handoff and any(not is_handoff(f) for f in fs))
    for h, ct, fs in commits:
        if ct > last_handoff:
            files |= {f for f in fs if not is_handoff(f)}
    return sorted(files), newer, handoff_dirty


def main():
    data = json.loads(sys.stdin.read() or "{}")
    if data.get("stop_hook_active"):
        return  # this reply is already the answer to a reminder: never block twice in a row
    root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    root = git(root, "rev-parse", "--show-toplevel").strip()
    files, commits, handoff_dirty = pending_changes(root)
    if not files or handoff_dirty:
        return
    # once per batch: remember what was reminded about, in .git (never committed)
    batch = hashlib.sha1("\n".join(files + commits).encode()).hexdigest()
    state = os.path.join(git(root, "rev-parse", "--absolute-git-dir").strip(),
                         f"handoff-reminder-{session_tag() or data.get('session_id', 'local')}")
    try:
        if open(state).read().strip() == batch:
            return
    except OSError:
        pass
    with open(state, "w") as f:
        f.write(batch)
    shown = ", ".join(files[:4]) + (f" and {len(files) - 4} more" if len(files) > 4 else "")
    print(json.dumps({
        "decision": "block",
        "reason": (f"Handoff reminder: this session changed {shown} since HANDOFF.md was last updated. "
                   "If a change just went live, add it to this session's status section in HANDOFF.md now; if we "
                   "are wrapping up, update HANDOFF.md (the /wrapup steps). If the work is still only on a test "
                   "branch, don't edit HANDOFF.md: just end your reply with one short line asking the user to type "
                   "/wrapup before they leave. (Shown once per new batch of changes.)"),
    }))


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        pass  # never crash or block a session because of this reminder
    sys.exit(0)
