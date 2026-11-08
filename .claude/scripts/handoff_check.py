#!/usr/bin/env python3
"""Prove that moving sections from HANDOFF.md to HANDOFF_ARCHIVE.md lost nothing.

  python3 .claude/scripts/handoff_check.py                 # before = the last commit (HEAD), after = the files on disk
  python3 .claude/scripts/handoff_check.py --ref main      # before = main
  python3 .claude/scripts/handoff_check.py --handoff X --archive Y   # after = other files

"Before" is HANDOFF.md + HANDOFF_ARCHIVE.md as committed at --ref (the archive may not exist yet).
"After" is the two files on disk. It checks, line by line, that every line of "before" is still in exactly one
place in "after" (lines lost must be 0), lists every line that is new, and checks that each section that left
HANDOFF.md sits in the archive byte for byte. Exit code 0 = OK, 1 = something lost or changed.
Used by /wrapup: commit the session's HANDOFF.md update first, then move the old sections, then run this.
"""
import argparse, collections, os, subprocess, sys


def git_show(ref, path, root):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=root, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def sections(text):
    """[(title, block)] split on '## ' headings; consecutive '## ' lines are one title; the part before the
    first heading is the 'header'."""
    lines = text.split("\n")
    out, start, title = [], 0, "(header)"
    i = 0
    while i < len(lines):
        if lines[i].startswith("## ") and (i == 0 or not lines[i - 1].startswith("## ")):
            if i > start:
                out.append((title, "\n".join(lines[start:i])))
            j = i
            while j + 1 < len(lines) and lines[j + 1].startswith("## "):
                j += 1
            title, start = " ".join(l[3:] for l in lines[i:j + 1]), i
            i = j + 1
            continue
        i += 1
    out.append((title, "\n".join(lines[start:])))
    return out


def body_lines(text):
    return text.split("\n")[:-1] if text.endswith("\n") else text.split("\n") if text else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--handoff", default="HANDOFF.md")
    ap.add_argument("--archive", default="HANDOFF_ARCHIVE.md")
    a = ap.parse_args()
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or "."

    b_h, b_a = git_show(a.ref, "HANDOFF.md", root), git_show(a.ref, "HANDOFF_ARCHIVE.md", root)
    rd = lambda p: open(p if os.path.isabs(p) else os.path.join(root, p), encoding="utf-8").read() if os.path.exists(
        p if os.path.isabs(p) else os.path.join(root, p)) else ""
    n_h, n_a = rd(a.handoff), rd(a.archive)

    before = collections.Counter(body_lines(b_h)) + collections.Counter(body_lines(b_a))
    after = collections.Counter(body_lines(n_h)) + collections.Counter(body_lines(n_a))
    lost = before - after
    added = after - before

    kb = lambda s: f"{len(s.encode('utf-8')) / 1024:.1f} KB"
    print(f"Before ({a.ref}): HANDOFF.md {len(body_lines(b_h))} lines, {kb(b_h)}; "
          f"HANDOFF_ARCHIVE.md {len(body_lines(b_a))} lines, {kb(b_a)}")
    print(f"After (on disk): HANDOFF.md {len(body_lines(n_h))} lines, {kb(n_h)}; "
          f"HANDOFF_ARCHIVE.md {len(body_lines(n_a))} lines, {kb(n_a)}")

    ok = True
    n_lost = sum(lost.values())
    print(f"\nLines lost: {n_lost}")
    for line, k in lost.items():
        ok = False
        print(f"  LOST x{k}: {line[:110]}")

    dup = {l: k for l, k in added.items() if l.strip() and before[l]}
    new = {l: k for l, k in added.items() if l.strip() and not before[l]}
    blank = sum(k for l, k in added.items() if not l.strip())
    print(f"Old lines now in both files (duplicates): {sum(dup.values())}")
    for line, k in dup.items():
        ok = False
        print(f"  DUPLICATE x{k}: {line[:110]}")
    print(f"New lines (written this time, not from the old files): {sum(new.values())} text + {blank} blank")
    for line, k in new.items():
        print(f"  + {line[:114]}" + (f"  (x{k})" if k > 1 else ""))

    # Section by section: where each section of the old HANDOFF.md is now.
    new_titles = {t: blk for t, blk in sections(n_h)}
    print("\nEach section of the old HANDOFF.md:")
    counts = collections.Counter()
    for t, blk in sections(b_h):
        if t in new_titles:
            if new_titles[t] == blk:
                where = "stays in HANDOFF.md, unchanged"
            else:
                o, n = collections.Counter(blk.split("\n")), collections.Counter(new_titles[t].split("\n"))
                where = f"stays in HANDOFF.md, {sum((n - o).values())} lines added, {sum((o - n).values())} replaced"
            counts["stay"] += 1
        elif blk.strip("\n") in n_a:
            where = "moved to HANDOFF_ARCHIVE.md, byte for byte"
            counts["moved"] += 1
        else:
            where = "NOT FOUND byte for byte in either file"
            counts["missing"] += 1
            ok = False
        print(f"  {kb(blk):>8}  {where:<55} {t[:70]}")
    print(f"\n{counts['stay']} sections stay, {counts['moved']} moved, {counts['missing']} not found.")
    print("RESULT: OK, nothing lost" if ok else "RESULT: PROBLEM, see above")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
