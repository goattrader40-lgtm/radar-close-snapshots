#!/usr/bin/env python3
"""Save files to the radar-data branch (the portal reads its data from there).

  python3 radar/publish.py [--branch NAME] [--keep-history] "<commit message>" <file> [<file> ...]

Each file is stored at the branch root under its own name; the other files on the branch are kept.
The branch always holds a single commit (no history), so the 5-minute updates don't grow the repo
(--keep-history adds a normal commit instead; used for the radar-backup branch).
Safe when several jobs write at once: the push only succeeds if nobody else pushed in between,
otherwise it re-reads the branch and tries again.
Run it from inside a clone of the repo (any branch).
"""
import os, random, subprocess, sys, tempfile, time

BRANCH = "radar-data"
KEEP = False


def git(*a, inp=None, env=None, check=True):
    r = subprocess.run(("git",) + a, input=inp, capture_output=True, text=True, env=env)
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(a)} failed: {r.stderr.strip()}")
    return r


def tip():
    git("fetch", "-q", "--depth", "2" if KEEP else "1", "origin", f"+refs/heads/{BRANCH}:refs/remotes/origin/{BRANCH}", check=False)
    r = git("rev-parse", "-q", "--verify", f"refs/remotes/origin/{BRANCH}", check=False)
    return r.stdout.strip() if r.returncode == 0 else None


def main():
    global BRANCH, KEEP
    for k, v in (("GIT_AUTHOR_NAME", "radar-bot"), ("GIT_COMMITTER_NAME", "radar-bot"),
                 ("GIT_AUTHOR_EMAIL", "radar-bot@users.noreply.github.com"),
                 ("GIT_COMMITTER_EMAIL", "radar-bot@users.noreply.github.com")):
        os.environ.setdefault(k, v)
    args = sys.argv[1:]
    while args and args[0].startswith("--"):
        if args[0] == "--branch":
            BRANCH = args[1]; args = args[2:]
        elif args[0] == "--keep-history":
            KEEP = True; args = args[1:]
        else:
            sys.exit(f"unknown option {args[0]}")
    msg, files = args[0], args[1:]
    for f in files:
        if not os.path.isfile(f) or os.path.getsize(f) == 0:
            sys.exit(f"refusing to publish missing or empty file: {f}")
    blobs = {os.path.basename(f): git("hash-object", "-w", f).stdout.strip() for f in files}
    for attempt in range(8):
        old = tip()
        with tempfile.TemporaryDirectory() as td:
            env = dict(os.environ, GIT_INDEX_FILE=os.path.join(td, "index"))
            if old:
                git("read-tree", old, env=env)
            for name, sha in blobs.items():
                git("update-index", "--add", "--cacheinfo", f"100644,{sha},{name}", env=env)
            tree = git("write-tree", env=env).stdout.strip()
        parent = ["-p", old] if (KEEP and old) else []
        commit = git("commit-tree", tree, *parent, "-m", msg).stdout.strip()
        lease = f"--force-with-lease=refs/heads/{BRANCH}:{old or ''}"
        r = git("push", "-q", lease, "origin", f"{commit}:refs/heads/{BRANCH}", check=False)
        if r.returncode == 0:
            print(f"published {', '.join(blobs)} to {BRANCH} ({commit[:7]})")
            return
        print(f"push attempt {attempt + 1} rejected, retrying: {r.stderr.strip()[:200]}", file=sys.stderr)
        time.sleep(2 + random.random() * 4)
    sys.exit("could not publish after 8 attempts")


if __name__ == "__main__":
    main()
