#!/usr/bin/env python3
"""Run a project's checks once per branch, in that branch's worktree, and print
a compact summary to hand to the review team.

  branch_checks.py --repo <path> --branch <b> [--branch <b2> ...] -- "<cmd>" ["<cmd>" ...]

Prints, per branch: the worktree path, then PASS/FAIL per command with the
last lines of output on failure. A branch with no worktree gets a temporary
detached one, kept for the reviewers; the last line prints how to remove it.
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

TAIL = 30


def worktrees(repo):
    out = subprocess.run(["git", "-C", repo, "worktree", "list", "--porcelain"],
                         capture_output=True, text=True, check=True).stdout
    found, path = {}, None
    for line in out.splitlines():
        if line.startswith("worktree "):
            path = line[9:]
        elif line.startswith("branch refs/heads/"):
            found.setdefault(line[18:], path)
    return found


def run(cmd, cwd):
    p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if p.returncode == 0:
        return f"PASS `{cmd}`"
    lines = (p.stdout + p.stderr).rstrip().splitlines()
    tail = "\n".join("    " + l for l in lines[-TAIL:])
    return f"FAIL `{cmd}` (exit {p.returncode}, last {min(TAIL, len(lines))} lines)\n{tail}"


def main():
    if "--" not in sys.argv:
        sys.exit(__doc__)
    i = sys.argv.index("--")
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--branch", action="append", required=True)
    a = ap.parse_args(sys.argv[1:i])
    cmds = sys.argv[i + 1:]
    repo = str(Path(a.repo).expanduser().resolve())
    wts = worktrees(repo)
    temps = []
    for b in a.branch:
        tmp = None
        wt = wts.get(b)
        if not wt:
            tmp = tempfile.mkdtemp(prefix=f"checks-{b.replace('/', '-')}-")
            subprocess.run(["git", "-C", repo, "worktree", "add", "--detach", "-q", tmp, b], check=True)
            wt = tmp
        print(f"## {b}  worktree: {wt}{'  (temporary)' if tmp else ''}")
        for c in cmds:
            print(run(c, wt))
        print()
        if tmp:
            temps.append(tmp)
    if temps:
        print("# after the review: " + " && ".join(f"git -C {repo} worktree remove --force {t}" for t in temps))


if __name__ == "__main__":
    main()
