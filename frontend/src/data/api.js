// API 层 —— 异步 fetch，带简单内存缓存
import { bigramScore } from '../utils/bigram.js'

const API_BASE = '/api'

// ── 内存缓存 ───────────────────────────────────────────────────────
let cacheRegulations = null
let cacheAuthority = null
let cacheAuthorityMapping = null
let cacheTexts = {}
let cacheDiagrams = {}

async function fetchJSON(path) {
  const res = await fetch(`${API_BASE}${path}`)
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`)
  return res.json()
}

// ── 制度列表 ───────────────────────────────────────────────────────
export async function getRegulations() {
  if (cacheRegulations) return cacheRegulations
  const data = await fetchJSON('/regulations')
  cacheRegulations = data.filter(
    r => r.id && r.id !== '制度序号' && r.name !== '制度名称'
  )
  return cacheRegulations
}

export async function getTree() {
  const regs = await getRegulations()
  const tree = {}
  for (const r of regs) {
    const mod  = r.module || '其他'
    const item = r.item   || '其他'
    if (!tree[mod])       tree[mod] = {}
    if (!tree[mod][item]) tree[mod][item] = []
    tree[mod][item].push(r)
  }
  return tree
}

// ── 流程事项 ───────────────────────────────────────────────────────
export async function getAuthority() {
  if (cacheAuthority) return cacheAuthority
  cacheAuthority = await fetchJSON('/authority')
  return cacheAuthority
}

// ── 单条制度详情 ───────────────────────────────────────────────────
export async function getRegulation(id) {
  const [meta, textData, diagData] = await Promise.all([
    fetchJSON(`/regulations/${encodeURIComponent(id)}`).catch(() => null),
    fetchJSON(`/regulations/${encodeURIComponent(id)}/text`).catch(() => null),
    fetchJSON(`/regulations/${encodeURIComponent(id)}/diagrams`).catch(() => null),
  ])

  if (!meta) return null

  // 缓存 text / diagrams
  if (textData) cacheTexts[id] = textData
  if (diagData) cacheDiagrams[id] = diagData

  return {
    ...meta,
    text:            textData?.text   || '',
    blocks:          textData?.blocks || [],
    charts:          diagData?.charts || [],
    authority_items: await matchAuthority(id, meta.name || '', meta.module || ''),
  }
}

// ── 搜索 ───────────────────────────────────────────────────────────
export async function search(q) {
  if (!q.trim()) return []
  const res = await fetchJSON(`/search?q=${encodeURIComponent(q.trim())}&limit=30`)
  const regs = res.regulations || []
  const auths = res.authority || []
  // 后端已经排序，直接合并
  return [
    ...regs.map(r => ({ ...r, type: 'regulation', score: r.score || 0 })),
    ...auths.map(a => ({ ...a, type: 'authority', score: a.score || 0 })),
  ]
    .sort((a, b) => b.score - a.score)
    .slice(0, 30)
}

// ── 权责匹配（与后端逻辑一致）──────────────────────────────────────
const SUFFIXES = /(管理办法|实施细则|工作规则|管理规定|实施方案|操作规程|暂行规定|工作制度|管理制度|实施办法|管理规程|办法|规定|规则|细则|方案|制度)$/
const SKIP = new Set(['有限公司', '公司'])

function extractKeywords(text) {
  text = text.replace(/^有限公司/, '').trim()
  const parts = text.split(/[（）【】、，。\s]+/)
  const kws = []
  for (const p of parts) {
    if (!p || SKIP.has(p)) continue
    const core = p.replace(SUFFIXES, '').trim()
    if (core.length >= 2) kws.push(core)
    if (p.length >= 2)    kws.push(p)
  }
  return [...new Set(kws)]
}

async function matchAuthority(regId, regName, _regModule) {
  if (!cacheAuthorityMapping) {
    try {
      cacheAuthorityMapping = await fetchJSON('/regulations/authority-mapping')
    } catch {
      cacheAuthorityMapping = {}
    }
  }
  const rawAuth = await getAuthority()
  const authDict = Object.fromEntries(rawAuth.map(i => [i.key, i]))
  if (cacheAuthorityMapping[regId]) {
    return cacheAuthorityMapping[regId].map(k => authDict[k]).filter(Boolean)
  }
  const kws = extractKeywords(regName)
  if (!kws.length) return []
  const scored = []
  for (const item of rawAuth) {
    if (!item.flow?.length) continue
    const score = kws.reduce((s, kw) => s + ((item.name || '').includes(kw) ? 1 : 0), 0)
    if (score > 0) scored.push([score, item])
  }
  scored.sort((a, b) => b[0] - a[0])
  return scored.slice(0, 20).map(([, item]) => item)
}
