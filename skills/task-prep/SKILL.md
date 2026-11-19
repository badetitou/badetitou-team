---
name: task-prep
description: Prepare a new task before coding — find or create the GitHub, GitLab or local issue, put it on the project or issue board (and milestone on GitLab), split it into minimal PRs, pick the agent and worktree, and load only the context it needs. Use when the user asks for a new feature, fix or task ("I want…", "j'aimerais…", "work on #12", "nouvelle tâche"), before writing code.
---

# Task preparation

A task starts from an issue and ends in one or more small PRs. Preparing it
first is what keeps sessions short: the agent that does the work gets a brief,
not the whole conversation.

## Steps

1. **Read the team**: `.claude/team.md` and `CLAUDE.md` of the project. No team
   file → suggest `team-setup` and continue with defaults. Forge = the team
   file's, else `git remote get-url origin`: GitHub → `github-flow` (`gh`),
   GitLab → `gitlab-flow` (`glab`), no remote → `local-flow` (`board.py`, steps 2–7
   with local ids; no board card beyond the file's status). Below, "PR" means MR on GitLab.
2. **Find the issue**: `gh issue list --search "<keywords>" --state all` /
   `glab issue list --search "<keywords>" --all`. If the user gave a number,
   `gh|glab issue view <n> --comments`.
3. **Create it if missing** — in English, whatever the conversation language:
   title as an outcome, body = context, acceptance criteria, out of scope.
   Put it on the board (GitHub project / GitLab issue board) and, on GitLab,
   in the current milestone.
4. **Split**: if the work needs more than one reviewable PR (rule of thumb:
   > ~300 changed lines, or two independent concerns), create sub-issues
   (GitHub) or child tasks (GitLab work items) and order them. Each = one PR.
5. **Brief**: for the first slice, write a 10–20 line brief —
   goal, files/classes to read first, commands to verify, done criteria, rules
   from memories that apply. That brief is the prompt for the implementer.
6. **Place**: one worktree per issue (`EnterWorktree`, branch
   `<issue-number>-<slug>`). For Pharo image work, there is no worktree: name the
   image and MCP server to use instead.
7. **Move the card** to *In Progress* (GitLab: `workflow::in progress` label) and start, or hand the brief to the
   `implementer` agent when the work can run in the background. Independent
   slices can each get an implementer in its own worktree, in parallel.
8. **Review before merge**: `review-team` for task branches (one or many),
   `reviewer` alone for a one-file fix.
9. **Ship** (push → PR → wait for CI → merge). Push and opening the draft PR are
   two commands: run them inline with Bash (~1 k tokens); a subagent for them
   costs ~60 k of context. Waiting for CI and merging is the mechanical loop:
   workflow code or an agent with `model: haiku`, never the session model.
   A subagent can merge only if `Bash(gh pr merge:*)` / `Bash(glab mr merge:*)`
   is allowed in the project's `.claude/settings.json`; otherwise it stops at a
   green PR and the main session merges.

Ask the user only when the scope is ambiguous enough that two readings would
lead to different PRs.

## Many issues, run autonomously

One session per batch of issues (`start_session`, or `hand_off_to_session`
mid-task), each with its short brief — not one session driving everything:
every workflow or agent notification makes the main loop re-read its whole,
ever-growing context (one 26-PR run: 52 M cache read for ~17 k output; one
7-PR run: 506 M cache read). The same holds when the user drives it ("next
PR", "lance #N"): from the second PR in a session, offer to start the next issue
in a fresh session with its brief (`start_session`) instead of continuing here.
