import { getRegulations, getAuthority } from '../data/api.js'
import { embedText, embedBatch } from './useLlm.js'
import { useSettings } from './useSettings.js'
import { topK } from '../utils/vector.js'
import { bigramScore } from '../utils/bigram.js'

const INDEX_KEY = 'embedding-index-v1'
let embeddingIndex = null

function chunkRegulation(reg, textData) {
  const firstText = (textData?.text || '').slice(0, 300)
  const meta = [reg.module, reg.item, reg.dept].filter(Boolean).join(' | ')
  return {
    type: 'regulation',
    id: reg.id,
    title: reg.name,
    route: `#/regulation/${reg.id}`,
    text: `${reg.name}\n${meta}\n${firstText}`.slice(0, 500),
  }
}

function chunkAuthority(auth) {
  if (!auth.flow?.length) return null
  const steps = auth.flow.map(s => `${s.role || ''}-${s.step || ''}`).join('; ')
  return {
    type: 'authority',
    id: auth.key,
    title: auth.name,
    route: `#/authority?q=${encodeURIComponent(auth.name)}`,
    text: `${auth.name}\n发起: ${auth.initiator || ''}\n审批: ${auth.final_approver || ''}\n流程: ${steps}`.slice(0, 500),
  }
}

async function getIndex() {
  if (embeddingIndex) return embeddingIndex

  // 1. Check localStorage cache
  try {
    const raw = localStorage.getItem(INDEX_KEY)
    if (raw) {
      const cache = JSON.parse(raw)
      const { settings } = useSettings()
      const expectedModel = settings.embedModel || 'jiaorong-qwen3-embedding-8b'
      const expectedBase = (settings.embedBaseUrl || settings.baseUrl).replace(/\/+$/, '')
      const cachedBase = (cache.baseUrl || '').replace(/\/+$/, '')
      if (cache.model === expectedModel && cachedBase === expectedBase) {
        embeddingIndex = cache.embeddings
        return embeddingIndex
      }
    }
  } catch { /* ignore parse errors */ }

  // 2. Check bundle pre-built
  try {
    const bundle = await import('../data/bundle.js')
    if (bundle.embeddings && bundle.embeddings.length > 0) {
      embeddingIndex = bundle.embeddings
      return embeddingIndex
    }
  } catch { /* bundle has no embeddings */ }

  return null
}

function keywordSearch(query, limit = 8) {
  const STOP = new Set(['需要','什么','怎么','如何','是否','可以','应该','流程','走','的','了','吗','呢','啊','我','要','去','在','和','与','或','有','是','一下','哪些','怎样','能','请','问','想','规定','要求','内容','相关'])
  const kws = query.replace(/[？?！!，。、：；""''（）【】]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length >= 2 && !STOP.has(w))
    .map(w => w.toLowerCase())

  if (!kws.length) return []

  const regs = getRegulations()
  const auths = getAuthority()

  // Search regulations
  const regResults = []
  for (const r of regs) {
    const name = (r.name || '').toLowerCase()
    const text = [r.module, r.item, r.dept, r.doc_no].filter(Boolean).join(' ').toLowerCase()
    let score = 0
    for (const kw of kws) {
      // 名称匹配权重×2，其他字段权重×1
      if (name.includes(kw)) {
        score += 2
      } else if (text.includes(kw)) {
        score += 1
      } else {
        const nameBigram = bigramScore(kw, name)
        const textBigram = bigramScore(kw, text)
        score += Math.max(nameBigram * 2, textBigram)  // 名称 bi-gram 同样双倍
      }
    }
    if (score > 0) {
      regResults.push({
        type: 'regulation',
        id: r.id,
        title: r.name,
        route: `#/regulation/${r.id}`,
        snippet: `${r.module || ''} - ${r.item || ''} | ${r.dept || ''}`,
        score,
      })
    }
  }

  // Search authority
  const authResults = []
  for (const a of auths) {
    if (!a.flow?.length) continue
    const name = (a.name || '').toLowerCase()
    const text = [a.initiator, a.category].filter(Boolean).join(' ').toLowerCase()
    let score = 0
    for (const kw of kws) {
      // 名称匹配权重×2，其他字段权重×1
      if (name.includes(kw)) {
        score += 2
      } else if (text.includes(kw)) {
        score += 1
      } else {
        const nameBigram = bigramScore(kw, name)
        const textBigram = bigramScore(kw, text)
        score += Math.max(nameBigram * 2, textBigram)
      }
    }
    if (score > 0) {
      authResults.push({
        type: 'authority',
        id: a.key,
        title: a.name,
        route: `#/authority?q=${encodeURIComponent(a.name)}`,
        snippet: `发起：${a.initiator || ''} | 最终审批：${a.final_approver || ''}`,
        score,
      })
    }
  }

  // Ensure balanced results: at least 3 from each type if available
  regResults.sort((a, b) => b.score - a.score)
  authResults.sort((a, b) => b.score - a.score)

  const halfLimit = Math.floor(limit / 2)
  const regTake = Math.min(regResults.length, Math.max(halfLimit, limit - authResults.length))
  const authTake = Math.min(authResults.length, limit - Math.min(regResults.length, halfLimit))

  return [
    ...regResults.slice(0, regTake),
    ...authResults.slice(0, authTake),
  ].sort((a, b) => b.score - a.score).slice(0, limit)
}

function binarize(vec) {
  const bytes = new Uint8Array(Math.ceil(vec.length / 8))
  for (let i = 0; i < vec.length; i++) {
    if (vec[i] > 0) bytes[i >> 3] |= (1 << (i & 7))
  }
  let binary = ''
  for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i])
  return btoa(binary)
}

export async function retrieve(query, limit = 8) {
  const index = await getIndex()

  if (!index) {
    return keywordSearch(query, limit)
  }

  let queryVec
  try {
    queryVec = await embedText(query)
  } catch {
    return keywordSearch(query, limit)
  }

  const queryBvec = binarize(queryVec)
  // Fetch 2x results to have room for balancing
  const hits = topK(queryBvec, index, limit * 2)

  const allResults = hits.map(h => ({
    type: h.item.type,
    id: h.item.id,
    title: h.item.title,
    route: h.item.route,
    snippet: h.item.text.slice(0, 200),
    score: h.score,
  }))

  // Balance: ensure at least half from each type
  const regResults = allResults.filter(r => r.type === 'regulation')
  const authResults = allResults.filter(r => r.type === 'authority')
  const halfLimit = Math.ceil(limit / 2)

  const regTake = regResults.slice(0, halfLimit)
  const authTake = authResults.slice(0, halfLimit)
  const remaining = limit - regTake.length - authTake.length
  const extra = remaining > 0
    ? [...regResults.slice(halfLimit), ...authResults.slice(halfLimit)]
        .sort((a, b) => b.score - a.score).slice(0, remaining)
    : []

  const results = [...regTake, ...authTake, ...extra]

  // If still fewer than 3 regulations, supplement with keyword search
  const regCount = results.filter(r => r.type === 'regulation').length
  if (regCount < 3) {
    const kwResults = keywordSearch(query, limit)
    const regFromKw = kwResults.filter(r => r.type === 'regulation' && !results.find(x => x.id === r.id))
    const fill = regFromKw.slice(0, 3 - regCount)
    results.push(...fill)
  }

  return results
}

export function buildSystemPrompt(results) {
  const regs = results.filter(r => r.type === 'regulation')
  const auths = results.filter(r => r.type === 'authority')

  let context = ''
  if (regs.length) {
    context += '【相关制度文件】\n' + regs.map((r, i) =>
      `${i + 1}. [${r.title}](${r.route})\n   ${r.snippet}`
    ).join('\n\n')
  }
  if (auths.length) {
    context += '\n\n【相关权责事项】\n' + auths.map((r, i) =>
      `${i + 1}. [${r.title}](${r.route})\n   ${r.snippet}`
    ).join('\n\n')
  }

  return `你是中交西北投资发展有限公司的制度管理AI助手。用户是公司员工，向你咨询业务流程、审批权限、制度规定等问题。

${context}

【回答要求】
- 根据参考信息准确回答，如果参考信息不足，明确说明并建议咨询主责部门
- 必须使用上面参考信息中已有的链接，原样复制，不要自己编造链接格式
- 制度文件链接格式一定是 [名称](#/regulation/编号)，编号格式如 5-2-1（含连字符），例如 [采购管理办法](#/regulation/5-2-1)
- 权责事项链接格式一定是 [名称](#/authority?q=名称) ，例如 [物资采购审批](#/authority?q=%E7%89%A9%E8%B5%84%E9%87%87%E8%B5%AD%E5%AE%A1%E6%89%B9)
- 如果参考信息中有制度文件，回答时必须引用至少一条制度文件链接
- 如果参考信息中有权责事项，回答时必须引用至少一条权责事项链接
- 不要编造制度名称或条款内容
- 回答要简洁、准确、有条理
- 用中文回答`
}

// ── 运行时索引管理 ─────────────────────────────────────────────────

export async function buildIndex(onProgress) {
  const bundle = await import('../data/bundle.js')
  const regs = getRegulations().filter(r => r.id && r.id !== '制度序号' && r.name !== '制度名称')
  const auths = getAuthority()

  const allChunks = []
  for (const reg of regs) {
    allChunks.push(chunkRegulation(reg, bundle.texts?.[reg.id]))
  }
  for (const auth of auths) {
    const chunk = chunkAuthority(auth)
    if (chunk) allChunks.push(chunk)
  }

  const batchSize = 20
  const embedded = []
  const total = allChunks.length

  for (let i = 0; i < total; i += batchSize) {
    const batch = allChunks.slice(i, i + batchSize)
    const vecs = await embedBatch(batch.map(c => c.text))

    for (let j = 0; j < batch.length; j++) {
      if (vecs[j]) {
        embedded.push({ ...batch[j], bvec: binarize(vecs[j]) })
      }
    }

    if (onProgress) {
      onProgress(Math.min(i + batchSize, total), total)
    }
  }

  const { settings } = useSettings()
  const cache = {
    model: settings.embedModel || 'jiaorong-qwen3-embedding-8b',
    baseUrl: settings.embedBaseUrl || settings.baseUrl,
    generated_at: Date.now(),
    count: embedded.length,
    embeddings: embedded,
  }

  localStorage.setItem(INDEX_KEY, JSON.stringify(cache))
  embeddingIndex = embedded
  return embedded
}

export function getIndexStatus() {
  try {
    const raw = localStorage.getItem(INDEX_KEY)
    if (!raw) return { exists: false }
    const cache = JSON.parse(raw)
    return {
      exists: true,
      model: cache.model,
      baseUrl: cache.baseUrl,
      generated_at: cache.generated_at,
      count: cache.count,
    }
  } catch {
    return { exists: false }
  }
}

export function clearIndex() {
  localStorage.removeItem(INDEX_KEY)
  embeddingIndex = null
}
