---
name: team-retro
description: Run a retrospective on a project's Claude sessions — token use, heavy tools, user corrections, agent usage — and turn findings into concrete improvements to the project's team (CLAUDE.md, agents, memories) and to badetitou-team itself. Use when the user says "retro", "how did the team do", "improve yourself", "réduis les tokens", or when the session-start reminder says a retro is due.
---

# Team retro

The loopback: measure, find the cause, change the setup, record it.

## 1. Measure (script, not transcripts)

```sh
python3 <this skill's dir>/scripts/session_stats.py <project-path> --since <last retro date>
```

It covers the project and its `.claude/worktrees/*` sessions and prints:
token totals, heaviest sessions, tool and subagent counts, and user messages
that look like corrections. Read raw `.jsonl` only to check one specific
finding, with `grep`, never whole.

## 2. Diagnose

Look for these patterns, in this order:

| Signal | Likely cause | Fix |
| --- | --- | --- |
| Same correction in several sessions | rule never written down | memory → CLAUDE.md or agent prompt |
| One generic tool dominates (`image_evaluate`, `Bash`) | missing dedicated tool or skill | point to the dedicated MCP tool; add a script; allowlist |
| Heavy sessions with many `Read`/`Grep` | exploration in the main context | `scout` agent on haiku, better CLAUDE.md map |
| Cache write ≫ output | context rebuilt often (forks, long CLAUDE.md, big tool results) | trim CLAUDE.md, fewer forks, narrower results |
| Agents defined but never used | wrong description / not needed | rewrite description or delete the agent |
| `general-purpose` subagents for one recurring job | missing specialist | create one narrow agent |

## 3. Change

Propose the changes as a short list (in the user's language), then apply the
ones they accept:

- **Project-specific** → that project's `CLAUDE.md`, `.claude/agents/`,
  `.claude/settings.json`, memory files.
- **Generic** (applies to several projects, or to how teams are built) → a
  change in badetitou-team: a skill, an agent template, the script, the catalog.
  Open an issue on `badetitou/badetitou-team` (English), and a minimal PR if the
  user wants it now.

## 4. Record

- Update `Last retro:` in the project's `.claude/team.md` and in
  `~/.claude/badetitou-team/projects.json`.
- Add an entry at the top of `~/.claude/badetitou-team/retro-log.md`
  (create it if missing): date, project,
  the numbers, what changed. Next retro compares against it.
