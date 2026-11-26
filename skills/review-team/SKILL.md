---
name: review-team
description: Review one or more finished task branches with the review team — the project's checks run once, five lens reviewers per branch (correctness, stability, style, tests, contract), one verifier per branch that merges duplicates and refutes false positives. Use before merging branches or opening PRs/MRs ("review", "relis les branches", "revue avant merge", "review-branches").
---

# Review team

Scripts: `C=<this skill's dir>/scripts/branch_checks.py`,
workflow `<this skill's dir>/review-branches.js`.

## Steps

1. **List the branches** to review, each with its brief (acceptance criteria
   from the issue / `.claude/issues/` file) and worktree (`git worktree list`).
2. **Run the checks once**, not once per reviewer, with the project's verify
   commands from its `CLAUDE.md`:
   `python3 $C --repo <repo> --branch a --branch b -- "<fmt>" "<lint>" "<test>"`.
   Pass each branch's section as its `checks`.
3. **Run the workflow** (this skill counts as the user's opt-in):
   `Workflow({scriptPath: "<this skill's dir>/review-branches.js", args: {repo, base, branches: [{branch, worktree, brief, checks}]}})`.
   Options: `lenses` (subset, e.g. drop `style` for a pure test change),
   `agentPrefix: ""` when the project has its own `review-*` copies, `models`
   (per lens or `verifier`). The script pins each lens's model (sonnet, haiku for
   style): workflow agents otherwise inherit the session model, frontmatter or not.
   If `scriptPath` is refused (the skill dir is not readable from the session),
   `Read` the script once and retry, or pass it inline as `script`.
   No Workflow tool → spawn the five `review-*` agents per branch in parallel
   with the Agent tool, then one `review-verifier` with all their findings.
4. **Act on the result**, per branch: `confirmed` → send to the branch's
   implementer (`SendMessage`, it keeps its context) or fix; `unverified`
   (missing tests, low severity) → show the user, fix only what they pick;
   `rejected` is a count, nothing to do.
5. **Merge** when fixed and green. The orchestrator (main session) does it,
   inline, once the verifier is clean and CI is green (forge: `gh pr merge <n>
   --squash` / `glab mr merge <n> --squash --remove-source-branch`; local:
   `git merge`). Allowed only when `.claude/team.md` says `Merge: orchestrator`;
   otherwise stop and tell the user the PR is ready. Push and PR inline; CI
   waits on haiku or in workflow code, never on the session model
   (`task-prep` step 9). Then remove the branch's worktree and branch, and any
   temporary worktree `branch_checks.py` printed.

## Sizing

All five lenses by default: a reviewer costs ~15k tokens, a missed bug more.
Drop a lens only when it has nothing to read (no tests touched → keep `tests`
anyway: it reports what's missing). One `reviewer` agent alone is enough for a
one-file fix or a docs change.
