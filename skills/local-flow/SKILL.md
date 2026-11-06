---
name: local-flow
description: Local task tracking for projects with no GitHub/GitLab remote yet — one Markdown issue per file in .claude/issues/, a board script for status, and export to gh/glab when the project goes public. Use when the project's team file or projects.json says repo is none/null, or the user says "suivi local", "pas encore sur GitHub", "local issues", "board local".
---

# Local flow

For projects not on a forge yet. Same rules as `github-flow`: minimal changes
(one concern per branch), issues in English, no Claude attribution, commit only
when asked, never on the default branch.

Script: `S=<this skill's dir>/scripts/board.py`, run from the project root. Read the board with the script, not by opening every
issue file.

## Issues

- `python3 $S` — open issues by status (`--all` adds done).
- `python3 $S new "<outcome>" [--parent N]` — creates
  `.claude/issues/NNNN-<slug>.md` and prints its path. Fill its body:
  Context, Acceptance criteria, Out of scope. `--parent` = sub-issue, one per branch.
- `python3 $S move <id> in-progress --branch <id>-<slug>` — status is one of
  `todo`, `in-progress`, `in-review`, `done`. Edit the file by hand only for
  the body.

Issue files are committed with the code (in the same branch as the work, or on
their own for a new backlog).

## Branches and "PRs"

- Branch `<id>-<slug>`; commit messages end with `Refs #<id>` (local id).
- There is no PR: *in-review* = branch ready, run `review-team` on the
  branch (`reviewer` alone for a one-file fix), then the user merges. Move to *done* in the
  merge commit or right after.

## Going public

1. Create the remote, then `python3 $S export gh|glab` (dry run) →
   `--run` once the user approves. It creates every open issue, parents
   first, and writes its URL in the file's `remote:` field.
2. Link sub-issues on the forge (see `github-flow` / `gitlab-flow`), set the
   project's `repo` in `~/.claude/badetitou-team/projects.json` and its team file, and switch to that flow.
