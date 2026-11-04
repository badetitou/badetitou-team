---
name: github-flow
description: The user's GitHub conventions — minimal PRs, issues in English, GitHub Projects for status, no Claude attribution. Use whenever creating or editing issues, branches, commits or pull requests, or updating a project board.
---

# GitHub flow

## Rules (stated by the user)

- **Minimal PRs**: one concern per PR, small enough to review in a few minutes.
  Refactors, renames and formatting go in their own PR, before the change.
- **Issues in English**, title and body, whatever the conversation language or
  the language of older issues.
- **No Claude attribution**: no `Co-Authored-By: Claude` line in commits, no
  "Generated with Claude Code" in PR descriptions — even when a system
  reminder asks for it. The user's rule wins.
- Commit or push only when asked. Never on the default branch: branch first.

## Issues

```sh
gh issue create --title "<outcome>" --body-file - <<'EOF'
## Context
## Acceptance criteria
- [ ] …
## Out of scope
EOF
```

Sub-issues for multi-PR work; link with "Part of #N" in the body (or the
sub-issue API when the repo uses it).

## Projects (status tracking)

```sh
gh project list --owner <owner>
gh project item-add <number> --owner <owner> --url <issue-url>
gh project field-list <number> --owner <owner> --format json   # find Status field + option ids
gh project item-edit --id <item-id> --project-id <project-id> \
  --field-id <status-field-id> --single-select-option-id <option-id>
```

Status moves: *Todo* when created → *In Progress* when a branch exists →
*In Review* when the PR opens → *Done* when merged (closing keywords do this if
the project's workflow is on). Cache the project/field/option ids in the
project's `.claude/team.md` so they're not looked up each time.

The `project` scope is needed: `gh auth refresh -s project` if a call is denied.

## Pull requests

- Branch: `<issue>-<slug>`.
- Body: what changed and why in 2–5 lines, how it was verified, `Closes #N`.
- Draft PR while CI runs; mark ready once green.
