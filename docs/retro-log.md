# Retro log

Newest first. One entry per retro: date, project, numbers from
`session_stats.py`, what changed (with links to issues/PRs).

## 2026-11-04 — baseline (before badetitou-team)

| Project | Sessions | Output tokens | Cache write | Top tools |
| --- | --- | --- | --- | --- |
| vscode-pharo (+ worktrees) | 40 | 5.8 M | 18.9 M | Bash 1157, pharo-pls image_evaluate 686, method_compile 187 |
| fluid (+ worktrees) | 78 | 6.9 M | 19.1 M | Bash 2221, browser_batch 478, Write 367 |

Findings that shaped v0.1:
- Recurring rules stated by hand in sessions (issues in English, no Claude
  attribution, image-only Pharo work) → `github-flow` and `pharo-mcp` skills.
- `image_evaluate` dominates Pharo work → `pharo-mcp` pushes dedicated tools first.
- Exploration ran in the main context (`general-purpose` subagents only) → `scout` on haiku.
