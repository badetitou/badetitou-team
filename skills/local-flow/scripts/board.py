#!/usr/bin/env python3
"""Local issue board: one Markdown file per issue in <project>/.claude/issues/.

Usage (run from the project root, or pass --dir):
  board.py                          # board grouped by status (default: open only)
  board.py --all                    # include done
  board.py new "<title>" [--parent N]   # create an issue, print its path
  board.py move <id> <status> [--branch B]
  board.py export gh|glab [--run]   # print (or run) commands creating the open issues on a forge
"""
import argparse
import datetime
import re
import shlex
import subprocess
import sys
from pathlib import Path

STATUSES = ["todo", "in-progress", "in-review", "done"]
BODY = "## Context\n\n## Acceptance criteria\n- [ ] \n\n## Out of scope\n"


def parse(path):
    text = path.read_text()
    m = re.match(r"---\n(.*?)\n---\n?(.*)", text, re.S)
    if not m:
        return None
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            v = v.strip()
            meta[k.strip()] = None if v in ("", "null") else v
    meta["_body"] = m.group(2)
    meta["_path"] = path
    return meta


def dump(meta):
    keys = [k for k in meta if not k.startswith("_")]
    head = "\n".join(f"{k}: {meta[k] if meta[k] is not None else 'null'}" for k in keys)
    meta["_path"].write_text(f"---\n{head}\n---\n{meta['_body']}")


def load(d):
    issues = [i for i in (parse(p) for p in sorted(d.glob("*.md"))) if i]
    return {int(i["id"]): i for i in issues}


def slug(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40]


def show(issues, include_done):
    for status in STATUSES:
        if status == "done" and not include_done:
            continue
        rows = [i for i in issues.values() if i.get("status") == status]
        print(f"## {status} ({len(rows)})")
        for i in sorted(rows, key=lambda i: int(i["id"])):
            extra = []
            if i.get("parent"):
                extra.append(f"parent #{i['parent']}")
            if i.get("branch"):
                extra.append(i["branch"])
            if i.get("remote"):
                extra.append(i["remote"])
            print(f"- #{i['id']} {i['title']}" + (f"  ({', '.join(extra)})" if extra else ""))
    unknown = [i for i in issues.values() if i.get("status") not in STATUSES]
    for i in unknown:
        print(f"! #{i['id']} has unknown status {i.get('status')!r}", file=sys.stderr)


def new(d, issues, title, parent):
    n = max(issues, default=0) + 1
    path = d / f"{n:04d}-{slug(title)}.md"
    meta = {"id": n, "title": title, "status": "todo", "parent": parent,
            "branch": None, "remote": None, "created": datetime.date.today().isoformat(),
            "_body": BODY, "_path": path}
    d.mkdir(parents=True, exist_ok=True)
    dump(meta)
    print(path)


def export(issues, forge, run):
    todo = [i for i in issues.values() if i.get("status") != "done" and not i.get("remote")]
    # parents first so children can reference their new number
    todo.sort(key=lambda i: (i.get("parent") is not None, int(i["id"])))
    for i in todo:
        body = i["_body"].strip() + f"\n\nImported from local issue #{i['id']}."
        if forge == "gh":
            cmd = ["gh", "issue", "create", "--title", i["title"], "--body", body]
        else:
            cmd = ["glab", "issue", "create", "--title", i["title"], "--description", body, "--yes"]
        if not run:
            print(shlex.join(cmd))
            continue
        out = subprocess.run(cmd, capture_output=True, text=True)
        if out.returncode:
            sys.exit(f"#{i['id']}: {out.stderr.strip()}")
        url = next((w for w in out.stdout.split() if w.startswith("http")), out.stdout.strip())
        i["remote"] = url
        dump(i)
        print(f"#{i['id']} -> {url}")
    if not run and todo:
        print("# dry run: add --run to create them; set parent links on the forge afterwards", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=".claude/issues")
    ap.add_argument("--all", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("new"); p.add_argument("title"); p.add_argument("--parent", type=int)
    p = sub.add_parser("move"); p.add_argument("id", type=int); p.add_argument("status", choices=STATUSES)
    p.add_argument("--branch")
    p = sub.add_parser("export"); p.add_argument("forge", choices=["gh", "glab"]); p.add_argument("--run", action="store_true")
    a = ap.parse_args()

    d = Path(a.dir)
    issues = load(d) if d.is_dir() else {}
    if a.cmd == "new":
        new(d, issues, a.title, a.parent)
    elif a.cmd == "move":
        if a.id not in issues:
            sys.exit(f"no issue #{a.id} in {d}")
        i = issues[a.id]
        i["status"] = a.status
        if a.branch:
            i["branch"] = a.branch
        dump(i)
        print(f"#{a.id} -> {a.status}")
    elif a.cmd == "export":
        export(issues, a.forge, a.run)
    else:
        if not issues:
            print(f"no issues in {d}")
            return
        show(issues, a.all)


if __name__ == "__main__":
    main()
