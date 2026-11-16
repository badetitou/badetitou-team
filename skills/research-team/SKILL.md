---
name: research-team
description: Literature search with the research team — search OpenAlex, then a three-stage funnel: title/abstract screen (haiku), intro/conclusion screen (sonnet), full-text confirmation (opus), with a report of the included papers. Use only in projects whose team.md lists the research team, or when the user asks for one ("recherche biblio", "état de l'art", "trouve des papiers sur", "literature search", "related work", "find papers on").
---

# Research team

Opt-in: only projects whose `.claude/team.md` has a *Research team* section
(added by `team-setup` on request). A code project gets none.

Script `P=<this skill's dir>/scripts/papers.py`, workflow
`<this skill's dir>/screen-papers.js`. State: `D=research/<topic-slug>/` in the
project (see the script's docstring for the files). Re-runs resume: `pending`
lists only what a stage hasn't decided yet.

## Steps

1. **Criteria first**, with the user, in `$D/criteria.md`: research question,
   inclusion criteria, exclusion criteria, year range, kinds of work (tools,
   empirical studies, surveys…). Every stage screens against this file only;
   don't start screening until the user agrees with it.
2. **Search**: 2–4 queries (synonyms, the field's own terms), e.g.
   `python3 $P search --dir $D --query "<q>" --limit 50 --from-year 2015`.
   Papers the user already knows or a `.bib` they give: add their titles as
   queries. Show the count; ask before going past ~300 candidates. Rate
   limited → the user can set a free `OPENALEX_API_KEY`.
3. **Stage 1 — abstract** (haiku, batches of 20, lenient):
   `python3 $P pending --dir $D --stage abstract > $D/.pending.json`, then
   `Workflow({scriptPath: "<this skill's dir>/screen-papers.js", args: {criteria, stage: "abstract", papers}})`.
   Write its `abstract` list to a file and
   `python3 $P record --dir $D --stage abstract --file <it>`.
4. **Fetch**: `python3 $P fetch --dir $D` downloads open-access PDFs of the
   papers kept and extracts text + intro/conclusion. It lists the ones with
   no PDF: give the user that list (DOIs) to drop PDFs into `$D/pdfs/<id>.pdf`
   (their library access), then re-run `fetch`. Missing pypdf → `pip install pypdf`.
5. **Stages 2 and 3 — intro, then confirm** (one pipeline: sonnet per paper,
   opus only for those it keeps):
   `pending --stage intro`, then the workflow with `stage: "fulltext"`; record
   its `intro` list with `--stage intro` and its `confirm` list with `--stage confirm`.
6. **Report**: `python3 $P report --dir $D` writes `$D/report.md` (funnel
   counts, included papers with reason and notes). Give the user the counts and
   the path; don't paste the report.

No Workflow tool → the same stages with the Agent tool: one `research-abstract`
per batch, then per paper `research-intro` and, if not excluded,
`research-confirm`, in parallel.

## Checks and limits

- Before trusting stage 1 on a new topic, show the user 5 of its `exclude`
  reasons; tighten `criteria.md` if one is wrong, then re-run it (record again:
  the latest decision wins).
- OpenAlex only covers what it indexes, abstracts are sometimes missing (kept
  as `maybe`), and snowballing (references, citations) is not automated.
- This is the everyday funnel. For a formal systematic review (PRISMA, dual
  blinded screening, kappa) use `academic-research-skills:sr-screener`; to
  write up the included papers, `academic-research-skills:deep-research` or
  `academic-paper` (lit-review mode).
