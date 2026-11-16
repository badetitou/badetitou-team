export const meta = {
  name: 'screen-papers',
  description: 'Research team: abstract screen in batches (haiku), or intro/conclusion screen (sonnet) then full-text confirmation (opus) per paper',
  whenToUse: 'Literature search funnel (research-team skill)',
  phases: [{ title: 'Abstract' }, { title: 'Intro' }, { title: 'Confirm' }],
}

// args: {
//   criteria: '<text of criteria.md>',
//   stage: 'abstract' | 'fulltext',
//   papers: [...],            // output of `papers.py pending --stage abstract|intro`
//   batch: 20,                // abstract stage only
//   agentPrefix: 'badetitou-team:',
// }
// Returns decisions to feed to `papers.py record`:
//   abstract → { abstract: [...] };  fulltext → { intro: [...], confirm: [...] }
const PREFIX = args.agentPrefix ?? 'badetitou-team:'
const CRITERIA = `Criteria:\n${args.criteria}`
const decision = enums => ({
  type: 'object',
  properties: {
    id: { type: 'string' }, decision: { type: 'string', enum: enums }, reason: { type: 'string' },
    notes: { type: 'string' },
  },
  required: ['id', 'decision', 'reason'],
})
const BATCH = { type: 'object', properties: { decisions: { type: 'array', items: decision(['include', 'maybe', 'exclude']) } }, required: ['decisions'] }
const INTRO = decision(['include', 'uncertain', 'exclude'])
const CONFIRM = decision(['include', 'exclude'])

if (args.stage === 'abstract') {
  const size = args.batch || 20
  const batches = []
  for (let i = 0; i < args.papers.length; i += size) batches.push(args.papers.slice(i, i + size))
  const results = await parallel(batches.map((b, n) => () => {
    const list = b.map(p => `### ${p.id} — ${p.title} (${p.year})\n${p.abstract}`).join('\n\n')
    return agent(`${CRITERIA}\n\nPapers:\n\n${list}`, { label: `abstract:${n + 1}/${batches.length}`, phase: 'Abstract', schema: BATCH, agentType: `${PREFIX}research-abstract` })
      .then(r => {
        const ids = new Set(b.map(p => p.id))
        const got = (r?.decisions || []).filter(d => ids.has(d.id))
        // A paper the screener skipped is kept, never silently dropped.
        const missing = b.filter(p => !got.some(d => d.id === p.id)).map(p => ({ id: p.id, decision: 'maybe', reason: 'not screened (agent skipped it)' }))
        return [...got, ...missing]
      })
  }))
  const abstract = results.flat()
  log(`abstract: ${abstract.filter(d => d.decision !== 'exclude').length}/${abstract.length} kept`)
  return { abstract }
}

const intro = [], confirm = []
await pipeline(
  args.papers,
  p => agent(`${CRITERIA}\n\nPaper ${p.id} — ${p.title} (${p.year}).\nSections file: ${p.sections}`,
    { label: `intro:${p.id}`, phase: 'Intro', schema: INTRO, agentType: `${PREFIX}research-intro` })
    .then(r => { const d = { ...(r || { decision: 'uncertain', reason: 'intro screen failed' }), id: p.id }; intro.push(d); return d }),
  (d, p) => d.decision === 'exclude' ? null
    : agent(`${CRITERIA}\n\nPaper ${p.id} — ${p.title} (${p.year}).\nStage-2 verdict: ${d.decision} — ${d.reason}\nFull text: ${p.fulltext}`,
      { label: `confirm:${p.id}`, phase: 'Confirm', schema: CONFIRM, agentType: `${PREFIX}research-confirm` })
      .then(r => { if (r) confirm.push({ ...r, id: p.id }) }),
)
log(`intro: ${intro.filter(d => d.decision !== 'exclude').length}/${intro.length} kept; confirm: ${confirm.filter(d => d.decision === 'include').length}/${confirm.length} included`)
return { intro, confirm }
