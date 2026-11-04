#!/usr/bin/env python3
"""Summarise Claude Code session transcripts for a project, cheaply.

Reads ~/.claude/projects/<encoded-path>/*.jsonl and prints one compact report:
token usage per session, the heaviest tools, subagent usage, and the user
messages that look like corrections. The retro skill reads this report instead
of the raw transcripts, which keeps a retro to a few thousand tokens.

Usage:
  session_stats.py <project-path> [--since YYYY-MM-DD] [--top N] [--json]
"""
import argparse
import collections
import json
import pathlib
import re
import sys

PROJECTS = pathlib.Path.home() / ".claude" / "projects"
CORRECTION = re.compile(
    r"\b(no|non|stop|arr[eê]te|don'?t|ne fais pas|pas [cç]a|wrong|faux|instead|plut[oô]t|"
    r"again|encore|why did you|pourquoi tu|I said|j'ai dit|never|jamais|always|toujours)\b",
    re.IGNORECASE,
)


def encode(path: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", str(pathlib.Path(path).expanduser().resolve()))


def transcript_dirs(project: str):
    prefix = encode(project)
    for d in sorted(PROJECTS.iterdir()):
        if d.name == prefix or d.name.startswith(prefix + "--claude-worktrees-"):
            yield d


def user_text(msg):
    content = msg.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [c.get("text", "") for c in content if c.get("type") == "text"]
        return "\n".join(parts)
    return ""


def analyse(path: pathlib.Path, since: str):
    s = {
        "session": path.stem[:8], "dir": path.parent.name[-40:], "start": None,
        "turns": 0, "input": 0, "cache_read": 0, "cache_write": 0, "output": 0,
        "tools": collections.Counter(), "subagents": collections.Counter(),
        "corrections": [], "title": "",
    }
    for line in path.open(encoding="utf-8", errors="replace"):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = d.get("type")
        ts = d.get("timestamp")
        if ts and not s["start"]:
            s["start"] = ts[:10]
        if t == "ai-title":
            s["title"] = d.get("title") or d.get("aiTitle") or s["title"]
        if t == "assistant":
            m = d.get("message", {})
            u = m.get("usage") or {}
            s["input"] += u.get("input_tokens", 0)
            s["cache_read"] += u.get("cache_read_input_tokens", 0)
            s["cache_write"] += u.get("cache_creation_input_tokens", 0)
            s["output"] += u.get("output_tokens", 0)
            for c in m.get("content") or []:
                if c.get("type") == "tool_use":
                    name = c.get("name", "?")
                    s["tools"][name] += 1
                    if name in ("Agent", "Task"):
                        s["subagents"][c.get("input", {}).get("subagent_type", "general-purpose")] += 1
        elif t == "user" and not d.get("isMeta") and not d.get("toolUseResult"):
            text = user_text(d.get("message", {})).strip()
            if text and not text.startswith("<") and CORRECTION.search(text):
                s["turns"] += 1
                s["corrections"].append(text[:200].replace("\n", " "))
            elif text and not text.startswith("<"):
                s["turns"] += 1
    if since and (s["start"] or "") < since:
        return None
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--since", default="")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    sessions = [s for d in transcript_dirs(a.project) for f in d.glob("*.jsonl")
                if (s := analyse(f, a.since))]
    if not sessions:
        sys.exit(f"no transcripts for {a.project} under {PROJECTS}")
    sessions.sort(key=lambda s: s["start"] or "")

    tools, agents = collections.Counter(), collections.Counter()
    for s in sessions:
        tools.update(s["tools"])
        agents.update(s["subagents"])
    total = lambda k: sum(s[k] for s in sessions)

    if a.json:
        for s in sessions:
            s["tools"], s["subagents"] = dict(s["tools"]), dict(s["subagents"])
        json.dump({"sessions": sessions, "tools": dict(tools), "subagents": dict(agents)}, sys.stdout, indent=1)
        return

    print(f"# {a.project}: {len(sessions)} sessions"
          f" ({sessions[0]['start']} → {sessions[-1]['start']})")
    print(f"tokens: output {total('output'):,} | cache read {total('cache_read'):,}"
          f" | cache write {total('cache_write'):,} | uncached input {total('input'):,}")
    print("\n## Heaviest sessions (output + cache write)")
    for s in sorted(sessions, key=lambda s: -(s["output"] + s["cache_write"]))[: a.top]:
        print(f"- {s['start']} {s['session']} {s['title'][:50]!r}: out {s['output']:,},"
              f" write {s['cache_write']:,}, {sum(s['tools'].values())} tool calls,"
              f" {len(s['corrections'])} corrections")
    print("\n## Tools: " + ", ".join(f"{k} {v}" for k, v in tools.most_common(a.top)))
    if agents:
        print("## Subagents: " + ", ".join(f"{k} {v}" for k, v in agents.most_common()))
    print("\n## User messages that look like corrections (deduplicated, forks share history)")
    seen = set()
    for s in sessions:
        for c in s["corrections"]:
            if c not in seen:
                seen.add(c)
                print(f"- [{s['start']} {s['session']}] {c}")


if __name__ == "__main__":
    main()
