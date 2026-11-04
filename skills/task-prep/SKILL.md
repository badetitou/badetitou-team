---
name: task-prep
description: Prepare a new task before coding — find or create the GitHub issue, put it on the project board, split it into minimal PRs, pick the agent and worktree, and load only the context it needs. Use when the user asks for a new feature, fix or task ("I want…", "j'aimerais…", "work on #12", "nouvelle tâche"), before writing code.
---

# Task preparation

A task starts from an issue and ends in one or more small PRs. Preparing it
first is what keeps sessions short: the agent that does the work gets a brief,
not the whole conversation.

## Steps

1. **Read the team**: `.claude/team.md` and `CLAUDE.md` of the project. No team
   file → suggest `team-setup` and continue with defaults.
2. **Find the issue**: `gh issue list --search "<keywords>" --state all`. If the
   user gave a number, `gh issue view <n> --comments`.
3. **Create it if missing** — in English, whatever the conversation language:
   title as an outcome, body = context, acceptance criteria, out of scope.
   Add it to the GitHub project and set status (see `github-flow`).
4. **Split**: if the work needs more than one reviewable PR (rule of thumb:
   > ~300 changed lines, or two independent concerns), create sub-issues and
   order them. Each sub-issue = one PR.
5. **Brief**: for the first slice, write a 10–20 line brief —
   goal, files/classes to read first, commands to verify, done criteria, rules
   from memories that apply. That brief is the prompt for the implementer.
6. **Place**: one worktree per issue (`EnterWorktree`, branch
   `<issue-number>-<slug>`). For Pharo image work, there is no worktree: name the
   image and MCP server to use instead.
7. **Move the card** to *In Progress* and start, or hand the brief to the
   `implementer` agent when the work can run in the background.

Ask the user only when the scope is ambiguous enough that two readings would
lead to different PRs.
