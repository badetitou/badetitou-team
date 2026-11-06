# Teams

A project's team has three groups. The **core** is always there; a
**specialist** joins only when the stack needs one; the **review team** is
called before merging task branches. Skills orchestrate them; agents do the work.

## Who is in the team

```mermaid
flowchart LR
  user([User]) --> main[Main session<br/>opus]

  subgraph skills[Skills: how the work flows]
    direction TB
    setup[team-setup]
    prep[task-prep]
    flow[github-flow / gitlab-flow / local-flow]
    rteam[review-team]
    retro[team-retro]
  end
  main --- skills

  subgraph core[Core team · 2–4 agents]
    scout[scout<br/>haiku · read-only]
    impl[implementer<br/>sonnet · one brief → one branch]
    rev[reviewer<br/>sonnet · quick single pass]
  end

  subgraph spec[Specialists · only if the stack needs one]
    pharo[pharo-dev<br/>sonnet · live Pharo image via MCP]
  end

  subgraph review[Review team · before merge]
    direction TB
    checks[[branch_checks.py<br/>fmt · lint · tests, once]]
    subgraph lenses[Lens reviewers · in parallel, per branch]
      c[review-correctness<br/>sonnet]
      s[review-stability<br/>sonnet]
      st[review-style<br/>haiku]
      t[review-tests<br/>sonnet]
      k[review-contract<br/>sonnet]
    end
    v[review-verifier<br/>sonnet · dedup + refute]
    checks --> lenses --> v
  end

  prep --> scout
  prep --> impl
  prep --> pharo
  rteam --> checks
  main --> rev
```

## A task, end to end

```mermaid
flowchart TD
  ask([“I want …” / “work on #12”]) --> prep[task-prep:<br/>issue · split into slices · brief per slice]
  prep --> board[(GitHub project / GitLab board /<br/>.claude/issues)]
  prep --> fan{independent slices?}
  fan -- one --> i1[implementer<br/>worktree A]
  fan -- several --> i2[implementer<br/>worktree A] & i3[implementer<br/>worktree B] & i4[implementer<br/>worktree C]
  i1 & i2 & i3 & i4 --> checks[[branch_checks.py · once per branch]]
  checks --> wf[review-branches workflow<br/>5 lenses per branch → 1 verifier per branch]
  wf --> res{result per branch}
  res -- confirmed --> fix[SendMessage to the same implementer<br/>it keeps its context] --> checks
  res -- unverified --> user([User picks what to fix])
  res -- clean --> merge[merge / PR · MR<br/>remove worktree + branch]
  merge --> retro[team-retro, every couple of weeks<br/>feeds rules back into CLAUDE.md, agents, this kit]
```

## Why this shape

- **Cheap where possible**: exploration on haiku, style lens on haiku, the
  main session only orchestrates.
- **Several reviewers, one verifier**: a narrow lens digs deeper than a
  generalist, so lenses stay separate. Verification is grouped per branch,
  which removes the duplicates the lenses share. In the Structure run, one
  verifier per finding cost twice the review itself.
- **Checks once**: fmt, lint and tests run by script before the reviewers,
  who read the output instead of rebuilding the branch.
- **Unverified ≠ rejected**: missing-test and low-severity findings are
  judgment calls; they go to the user instead of a verifier.
