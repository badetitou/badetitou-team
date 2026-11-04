---
name: team-setup
description: Set up (or refresh) a team of Claude agents for a project — investigate its stack, MCP servers, existing .claude config, memories and past sessions, then write a lean CLAUDE.md, agents, .mcp.json and a team manifest. Use when the user says "set up claude for this project", "prepare a team for X", "configure agents", "onboard this repo", or opens a project that has no .claude/team.md.
---

# Team setup

Goal: give a project the smallest team that covers its real work, with the
context each agent needs and nothing more. A good team cuts tokens: cheap
models for exploration, project rules written once in CLAUDE.md instead of
rediscovered each session, and agents with narrow tool lists.

Work in the target project's directory. If the user names a project by name,
look it up in `projects.json` at the root of the badetitou-team repo
(`~/Documents/Perso/badetitou-team`).

## 1. Investigate (cheap first)

Run these yourself; they're quick. Delegate to the `scout` agent only for a large
codebase you need summarised.

1. **Stack**: `git remote -v`, manifest files (`package.json`, `BaselineOf*`,
   `.project`, `.smalltalk.ston`, `pyproject.toml`…), `README.md`, CI workflows.
2. **Existing Claude config**: `CLAUDE.md`, `AGENTS.md`, `.claude/agents/`,
   `.claude/settings*.json`, `.mcp.json`, `.claude/team.md`. Keep what works;
   never overwrite without showing the diff.
3. **MCP servers**: project `.mcp.json`, user `~/.claude.json` (`mcpServers`
   and `projects[<path>].mcpServers`), and what's live (`ToolSearch`). For Pharo,
   see the `pharo-mcp` skill (one image = one port; PLexus can route them).
4. **Memories**: `~/.claude/projects/<encoded path>/memory/MEMORY.md` and those
   of related projects. Encoded path = absolute path with every non-alphanumeric
   char replaced by `-`. Feedback memories are rules the user already stated:
   lift the ones that apply project-wide into CLAUDE.md.
5. **Past sessions**: run the retro script (see the `team-retro` skill) for a
   one-page summary — heavy tools, subagents used, corrections. Don't read raw
   transcripts.
6. **GitHub**: `gh issue list --limit 20`, `gh project list --owner <owner>`,
   labels. The team plugs into the issue/project flow (`github-flow` skill).
7. **Reusable pieces**: `catalog/references.json` in badetitou-team lists external
   skills, plugins and MCP servers worth reusing before writing new ones.

## 2. Propose

Show the user a short plan (in their language) before writing:

- the team: 2–4 agents max to start. Typical roles, from `agents/` in badetitou-team:
  - `scout` (haiku) — read-only exploration, returns conclusions not dumps
  - `implementer` (sonnet) — one issue → one minimal branch/PR
  - `reviewer` (sonnet) — reviews a diff against the project rules
  - a stack specialist only when the stack needs one (e.g. `pharo-dev`)
- which stack skills apply (`pharo-mcp`, `vscode-extension`, …)
- MCP servers to wire, and any to drop
- CLAUDE.md rules lifted from memories
- what's unknown and needs the user's answer

Ask only what you can't infer. Skip the plan for a trivial refresh.

## 3. Write

In the target project:

- `CLAUDE.md` from `templates/project/CLAUDE.md`: commands, architecture rules,
  workflow. Under ~60 lines — it's loaded every turn, every line costs.
- `.claude/agents/<name>.md` — copy from badetitou-team `agents/` and specialise:
  replace generic "sources of truth" with this project's files and commands.
  Keep `model:` explicit (haiku for read-only, sonnet for code, `inherit` only
  when the work needs the strongest model).
- `.mcp.json` for project-local servers.
- `.claude/team.md` from `templates/project/team.md`: the team manifest — who
  does what, which skills, the GitHub project, and the date of the last retro.
- `.claude/settings.json`: allow the project's read-only and test commands to
  cut permission prompts.

Write agent prompts in the language of the project's existing agents (French in
fluid, English elsewhere unless told otherwise).

## 4. Register and hand over

- Add or update the project in badetitou-team `projects.json` (path, repo, stack,
  team, MCP servers, last retro).
- Tell the user what was written, and suggest the first `task-prep` run.
- Don't commit in the target project unless asked; if asked, follow `github-flow`.

## Refresh mode

When `.claude/team.md` exists, diff the current state against it (new MCP
servers, new memories, retro findings) and propose only the changes.
