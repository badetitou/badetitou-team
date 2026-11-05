---
name: gitlab-flow
description: The user's GitLab conventions — work items (issues and child tasks), issue boards for status, milestones, minimal merge requests, no Claude attribution. Use whenever the project's remote is GitLab and you create or edit issues, tasks, branches, commits or merge requests, move a board card, or set a milestone ("issue gitlab", "board", "milestone", "MR").
---

# GitLab flow

Same rules as `github-flow`: minimal changes (one concern per MR), issues in
English, no Claude attribution in commits or MRs, commit or push only when
asked, never on the default branch.

CLI: `glab` (`glab auth status`; self-hosted → `glab auth login --hostname <host>`).
In `glab api`, `:id` and `:fullpath` resolve to the current repo.

## Work items: issues and tasks

```sh
glab issue list --search "<keywords>" --all
glab issue view <iid> --comments
glab issue create --title "<outcome>" --label "<labels>" --milestone "<title>" \
  --description-file - <<'EOF'
## Context
## Acceptance criteria
- [ ] …
## Out of scope
EOF
```

Multi-MR work: the issue is the parent, each slice is a child **task** work
item (one task = one MR). Tasks share the project's iid sequence, so
`Closes #<task iid>` works in an MR. `glab work-items list --type task` lists
them; `glab work-items create` (experimental) has no parent flag, so create
child tasks through GraphQL:

```sh
# once per project, cache in team.md: Task type id
glab api graphql -f query='{ project(fullPath:"<path>") { workItemTypes { nodes { id name } } } }'
# parent work item id = gid://gitlab/WorkItem/<issue .id>  (glab api projects/:id/issues/<iid> | jq .id)
glab api graphql -f query='mutation { workItemCreate(input: {
  namespacePath: "<path>", title: "<slice>", workItemTypeId: "<Task type id>",
  hierarchyWidget: { parentId: "gid://gitlab/WorkItem/<id>" } }) {
  workItem { iid webUrl } errors } }'
```

Work spanning several issues: an epic (group level, Premium) if the group has
them, otherwise a parent issue with "Related to #N" links.

## Issue boards (status)

Board lists are driven by labels. Default mapping, adjust to what the project
already uses (`glab label list`, `glab api projects/:id/boards`):

| Status | Board list |
| --- | --- |
| Todo | *Open* (no workflow label) |
| In Progress | `workflow::in progress` |
| In Review | `workflow::in review` |
| Done | *Closed* (MR merged with `Closes #N`) |

Scoped labels (`scope::value`) replace each other, so a move is one call:

```sh
glab issue update <iid> --label "workflow::in progress"
```

Missing setup (only with the user's OK): `glab label create --name "workflow::in progress"`,
then add a list: `glab api -X POST projects/:id/boards/<board id>/lists -f label_id=<id>`.
If the project uses the native work item *Status* field instead (GitLab 18+, Premium),
note it in team.md and set it on the work item rather than with labels.

## Milestones

```sh
glab milestone list --state active --include-ancestors   # project + group milestones
glab issue update <iid> --milestone "<title>"             # tasks: glab work-items update <iid> -m
glab mr create … --milestone "<title>"
glab milestone create --title "<title>" --due-date <ISO date>   # only when asked
```

Use the milestone the user is working in; when several are active and none is
obvious, ask. Create, edit or close a milestone only when asked.

## Merge requests

- Branch: `<iid>-<slug>` (GitLab's own convention).
- `glab mr create --draft --title "<outcome>" --label "<labels>" --milestone "<title>" --description-file -`
  with a body of 2–5 lines (what and why, how verified) ending in `Closes #<iid>`.
- Move the card to *In Review* when the MR opens; mark ready once CI is green
  (`glab mr update <n> --ready`). `glab mr diff <n>`, `glab ci status`.

Cache project path, Task type id, board id, workflow label names and the
current milestone in the project's `.claude/team.md`.
