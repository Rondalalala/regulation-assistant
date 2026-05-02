// 纯前端 API 层 —— 所有数据在构建时打包，不依赖后端
import {
  regulations as rawRegs,
  authority    as rawAuth,
  authorityMapping,
  texts,
  diagrams,
} from './bundle.js'

// ── 制度列表（过滤无效行）──────────────────────────────────────────
const regulations = rawRegs.filter(
  r => r.id && r.id !== '制度序号' && r.name !== '制度名称'
)

export function getRegulations() { return regulations }

export function getTree() {
  const tree = {}
  for (const r of regulations) {
    const mod  = r.module || '其他'
    const item = r.item   || '其他'
    if (!tree[mod])       tree[mod] = {}
    if (!tree[mod][item]) tree[mod][item] = []
    tree[mod][item].push(r)
  }
  return tree
}

export function getAuthority() { return rawAuth }

export function getRegulation(id) {
  const reg = regulations.find(r => r.id === id)
  if (!reg) return null
  const textData = texts[id]    || {}
  const diagData = diagrams[id] || {}
  return {
    ...reg,
    text:            textData.text   || '',
    blocks:          textData.blocks || [],
    charts:          diagData.charts || [],
    authority_items: matchAuthority(id, reg.name || '', reg.module || ''),
  }
}

// ── 搜索 ────────────────────────────────────────────────────────────
export function search(q) {
  if (!q.trim()) return []
  const ql = q.toLowerCase()
  return regulations.filter(r =>
    (r.name   || '').toLowerCase().includes(ql) ||
    (r.module || '').toLowerCase().includes(ql) ||
    (r.item   || '').toLowerCase().includes(ql) ||
    (r.dept   || '').toLowerCase().includes(ql) ||
    (r.id     || '').toLowerCase().includes(ql)
  ).slice(0, 30)
}

// ── 权责匹配（与后端逻辑一致）──────────────────────────────────────
const SUFFIXES = /(管理办法|实施细则|工作规则|管理规定|实施方案|操作规程|暂行规定|工作制度|管理制度|实施办法|管理规程|办法|规定|规则|细则|方案|制度)$/
const SKIP = new Set(['中交西北投资发展有限公司', '西北投资', '中交投资', '有限公司', '公司'])

function extractKeywords(text) {
  text = text.replace(/^中交西北投资发展有限公司/, '').trim()
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

function matchAuthority(regId, regName, _regModule) {
  const authDict = Object.fromEntries(rawAuth.map(i => [i.key, i]))
  if (authorityMapping[regId]) {
    return authorityMapping[regId].map(k => authDict[k]).filter(Boolean)
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
