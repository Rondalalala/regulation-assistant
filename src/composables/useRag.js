import { getRegulations, getAuthority } from '../data/api.js'
import { embedText } from './useLlm.js'
import { topK } from '../utils/vector.js'

let embeddingIndex = null

async function getIndex() {
  if (embeddingIndex) return embeddingIndex

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
    const text = [r.name, r.module, r.item, r.dept, r.doc_no].filter(Boolean).join(' ').toLowerCase()
    let score = 0
    for (const kw of kws) {
      if (text.includes(kw)) score += 1
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
    const text = [a.name, a.initiator, a.category].filter(Boolean).join(' ').toLowerCase()
    let score = 0
    for (const kw of kws) {
      if (text.includes(kw)) score += 1
    }
    if (score > 0) {
      authResults.push({
        type: 'authority',
        id: a.key,
        title: a.name,
        route: `#/authority?id=${a.key}`,
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

  // 完整制度目录，防止 AI 编造不存在的制度
  const allRegs = getRegulations()
  const catalog = allRegs.map(r => `${r.id} ${r.name}`).join('\n')

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

【现有制度目录】
以下是系统中全部真实存在的制度文件，只可引用此目录中的制度，绝不可编造不存在的制度名称：
${catalog}

【回答要求】
- 根据参考信息准确回答，如果参考信息不足，明确说明并建议咨询主责部门
- 引用制度时，必须使用「现有制度目录」中真实存在的制度名称和编号，链接格式为 [名称](#/regulation/编号)
- 引用权责事项时，必须使用参考信息中已有的链接，格式为 [名称](#/authority?id=编码)
- 绝对不要编造制度名称、编号或条款内容。如果目录中没有相关制度，明确告知用户
- 如果参考信息中有制度文件，回答时必须引用至少一条制度文件链接
- 如果参考信息中有权责事项，回答时必须引用至少一条权责事项链接
- 回答要简洁、准确、有条理
- 用中文回答`
}
