export const meta = {
  name: 'review-branches',
  description: 'Review team: lens reviewers per branch, then one verifier per branch that merges duplicates and refutes findings',
  whenToUse: 'Before merging one or more task branches (review-team skill)',
  phases: [{ title: 'Review' }, { title: 'Verify' }],
}

// args: {
//   repo: '/abs/path',
//   base: 'main',                                  // optional
//   branches: [{ branch, worktree, brief, checks }],  // checks = branch_checks.py output
//   lenses: ['correctness', ...],                  // optional, default all five
//   agentPrefix: 'badetitou-team:',                // '' when the project has its own copies
// }
const LENSES = args.lenses || ['correctness', 'stability', 'style', 'tests', 'contract']
const PREFIX = args.agentPrefix ?? 'badetitou-team:'
const BASE = args.base || 'main'
// Judgment calls (missing tests) and low-severity findings are reported unverified.
const VERIFY = f => f.severity !== 'low' && f.lens !== 'tests'

const FINDINGS = {
  type: 'object',
  properties: {
    findings: { type: 'array', items: { type: 'object', properties: {
      severity: { type: 'string', enum: ['high', 'medium', 'low'] },
      location: { type: 'string' }, problem: { type: 'string' }, fix: { type: 'string' },
    }, required: ['severity', 'location', 'problem', 'fix'] } },
    checks: { type: 'string' },
  },
  required: ['findings', 'checks'],
}
const VERDICTS = {
  type: 'object',
  properties: {
    verdicts: { type: 'array', items: { type: 'object', properties: {
      index: { type: 'integer' }, real: { type: 'boolean' },
      duplicateOf: { type: ['integer', 'null'] }, reason: { type: 'string' },
    }, required: ['index', 'real', 'reason'] } },
  },
  required: ['verdicts'],
}

const context = b => `Repo ${args.repo}. Branch \`${b.branch}\`, worktree ${b.worktree}; diff: \`git -C ${b.worktree} diff ${BASE}...HEAD\`.
Brief: ${b.brief}
Checks already run (don't re-run):
${b.checks || 'none given'}`

const results = await pipeline(
  args.branches,
  // Review: all lenses of one branch in parallel; the barrier is per branch only.
  b => parallel(LENSES.map(lens => () =>
    agent(context(b), { label: `${b.branch}:${lens}`, phase: 'Review', schema: FINDINGS, agentType: `${PREFIX}review-${lens}` })
      .then(r => r && { lens, checks: r.checks, findings: r.findings.map(f => ({ ...f, lens })) })))
    .then(rs => rs.filter(Boolean)),
  // Verify: one verifier per branch, all verifiable findings at once (dedup + refute).
  async (reviews, b) => {
    const all = reviews.flatMap(r => r.findings)
    const toVerify = all.filter(VERIFY)
    const unverified = all.filter(f => !VERIFY(f))
    let confirmed = [], rejected = []
    if (toVerify.length) {
      const list = toVerify.map((f, i) => `${i}. [${f.severity}/${f.lens}] ${f.location}: ${f.problem} (fix: ${f.fix})`).join('\n')
      const v = await agent(`${context(b)}\n\nFindings:\n${list}`, { label: `verify:${b.branch}`, phase: 'Verify', schema: VERDICTS, agentType: `${PREFIX}review-verifier` })
      const byIndex = new Map((v?.verdicts || []).map(x => [x.index, x]))
      toVerify.forEach((f, i) => {
        const x = byIndex.get(i)
        if (!x) unverified.push(f)
        else if (x.duplicateOf != null && x.duplicateOf !== i) return
        else (x.real ? confirmed : rejected).push({ ...f, reason: x.reason })
      })
    }
    return {
      branch: b.branch,
      checks: reviews.map(r => `${r.lens}: ${r.checks}`),
      confirmed, unverified, rejected: rejected.length,
      missingLenses: LENSES.filter(l => !reviews.some(r => r.lens === l)),
    }
  },
)
const out = results.filter(Boolean)
for (const r of out) log(`${r.branch}: ${r.confirmed.length} confirmed, ${r.unverified.length} unverified, ${r.rejected} rejected`)
return out
