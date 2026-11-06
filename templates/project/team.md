# Team — <project>

Last retro: <YYYY-MM-DD or "none">

## Agents

| Agent | Model | Does | Doesn't |
| --- | --- | --- | --- |
| scout | haiku | read-only exploration, answers with references | edit |
| implementer | sonnet | one brief → one minimal branch | widen scope |
| reviewer | sonnet | diff vs rules and acceptance criteria | edit |

## Skills

- badetitou-team: `task-prep`, `github-flow`, `gitlab-flow` or `local-flow`, `team-retro`, <stack skills>
- other: <plugins / upstream skills in use>

## MCP servers

| Server | Where | Used for |
| --- | --- | --- |

## GitHub (keep one of the three sections)

- Repo: <owner/repo>
- Project: <owner> #<number> — project id `<PVT_…>`, Status field `<PVTSSF_…>`
  - Todo `<id>` · In Progress `<id>` · In Review `<id>` · Done `<id>`

## GitLab

- Repo: <host>/<group/project>
- Board: <name> (id `<id>`) — status by labels: In Progress `workflow::in progress` · In Review `workflow::in review` (or: native Status field)
- Task work item type id: `gid://gitlab/WorkItems::Type/<n>`
- Current milestone: <title> (due <date>)

## Local

- No remote yet: issues in `.claude/issues/` (`local-flow`). Export with `board.py export gh|glab` when a remote exists.

## Notes from retros

<Dated one-liners: what changed and why. Newest first.>
