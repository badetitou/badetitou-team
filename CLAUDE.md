# badetitou-team — notes for Claude

This repo is a Claude Code plugin (and its own marketplace) that builds and
improves agent teams for the user's other projects. See `README.md` for the map.

## Working on this repo

- Everything here is loaded into other sessions: every line of a skill, agent
  or hook output costs tokens in every project. Prefer short, checkable rules;
  move detail to files a skill reads on demand.
- Skills: `skills/<name>/SKILL.md` with `name` + `description` frontmatter. The
  description decides when it triggers — say when to use it, with phrases the
  user actually says (French or English).
- Agents: explicit `model:` (haiku for read-only, sonnet for code), narrow `tools:`.
- Scripts beat transcripts: anything a skill would compute by reading lots of
  text belongs in a script (see `skills/team-retro/scripts/session_stats.py`).
- Reuse upstream before writing: check `catalog/references.json`; reference
  upstream skills instead of copying them.
- Bump `version` in `.claude-plugin/plugin.json` on each merged change that
  alters behaviour.
- Validate: `claude plugin validate .`; test the script on a real project:
  `python3 skills/team-retro/scripts/session_stats.py ~/Documents/LSP/vscode-pharo`.

## Workflow

- Repo files in English; talk to the user in their language (often French).
- One issue → one minimal PR (`skills/github-flow`). No Claude attribution in
  commits or PRs.
- After a retro on any project, log it in `~/.claude/badetitou-team/retro-log.md` and update
  `~/.claude/badetitou-team/projects.json` (never commit it here).
