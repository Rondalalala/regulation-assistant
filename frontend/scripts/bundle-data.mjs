import { readFileSync, writeFileSync, readdirSync, mkdirSync } from 'fs'
import { resolve, dirname, join } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const dataDir = resolve(__dirname, '../../data')
const outDir  = resolve(__dirname, '../src/data')
const outFile = join(outDir, 'bundle.js')

console.log('📦 正在打包数据:', dataDir)

const regulations     = JSON.parse(readFileSync(join(dataDir, 'regulations.json'),      'utf8'))
const authority       = JSON.parse(readFileSync(join(dataDir, 'authority.json'),        'utf8'))
const authorityMapping= JSON.parse(readFileSync(join(dataDir, 'authority_mapping.json'),'utf8'))

const texts = {}
for (const f of readdirSync(join(dataDir, 'texts'))) {
  if (f.endsWith('.json'))
    texts[f.replace('.json', '')] = JSON.parse(readFileSync(join(dataDir, 'texts', f), 'utf8'))
}

const diagrams = {}
for (const f of readdirSync(join(dataDir, 'diagrams'))) {
  if (f.endsWith('.json'))
    diagrams[f.replace('.json', '')] = JSON.parse(readFileSync(join(dataDir, 'diagrams', f), 'utf8'))
}

// ── 切片 ──────────────────────────────────────────────────────────────

function chunkRegulation(reg, textData) {
  const firstText = (textData?.text || '').slice(0, 300)
  const meta = [reg.module, reg.item, reg.dept].filter(Boolean).join(' | ')
  return [{
    type: 'regulation',
    id: reg.id,
    title: reg.name,
    route: `#/regulation/${reg.id}`,
    text: `${reg.name}\n${meta}\n${firstText}`.slice(0, 500),
  }]
}

function chunkAuthority(auth) {
  if (!auth.flow?.length) return []
  const steps = auth.flow.map((s, i) => `${s.role || ''}-${s.step || ''}`).join('; ')
  return [{
    type: 'authority',
    id: auth.key,
    title: auth.name,
    route: `#/authority?q=${encodeURIComponent(auth.name)}`,
    text: `${auth.name}\n发起: ${auth.initiator || ''}\n审批: ${auth.final_approver || ''}\n流程: ${steps}`.slice(0, 500),
  }]
}

// ── 二值量化：4096 floats → 512 bytes → base64 ~683 chars ─────────────
function binaryQuantize(vec) {
  const bytes = new Uint8Array(Math.ceil(vec.length / 8))
  for (let i = 0; i < vec.length; i++) {
    if (vec[i] > 0) bytes[i >> 3] |= (1 << (i & 7))
  }
  return Buffer.from(bytes).toString('base64')
}

// ── Embedding ──────────────────────────────────────────────────────────

const EMBED_URL = process.env.JRCC_EMBED_URL || 'https://c4ai.ccccltd.cn/api/compatible/v1'
const EMBED_KEY = process.env.JRCC_API_KEY
const EMBED_MODEL = process.env.JRCC_EMBED_MODEL || 'jiaorong-qwen3-embedding-8b'

async function embedChunks(chunks) {
  if (!EMBED_KEY) {
    console.log('⚠️  JRCC_API_KEY not set, skipping embedding')
    return []
  }

  const batchSize = 20
  const result = []
  const total = chunks.length

  for (let i = 0; i < total; i += batchSize) {
    const batch = chunks.slice(i, i + batchSize)
    process.stdout.write(`\r🔍 Embedding ${Math.min(i + batchSize, total)}/${total}`)

    try {
      const res = await fetch(`${EMBED_URL}/embeddings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${EMBED_KEY}`,
          'User-Agent': 'XBTZ-RegulationPlatform/2.0',
        },
        body: JSON.stringify({
          model: EMBED_MODEL,
          input: batch.map(c => c.text),
        }),
      })

      if (!res.ok) {
        const body = await res.text()
        console.error(`\n❌ Embedding failed: HTTP ${res.status} ${body.slice(0, 200)}`)
        return result
      }

      const data = await res.json()
      for (let j = 0; j < batch.length; j++) {
        if (data.data[j]?.embedding) {
          result.push({ ...batch[j], bvec: binaryQuantize(data.data[j].embedding) })
        }
      }
    } catch (err) {
      console.error(`\n❌ Embedding error: ${err.message}`)
      return result
    }
  }

  console.log('')
  return result
}

// ── 主流程 ─────────────────────────────────────────────────────────────

mkdirSync(outDir, { recursive: true })

const allChunks = []
for (const reg of regulations) {
  if (!reg.id || reg.id === '制度序号' || reg.name === '制度名称') continue
  allChunks.push(...chunkRegulation(reg, texts[reg.id]))
}
for (const auth of authority) {
  allChunks.push(...chunkAuthority(auth))
}
console.log(`📋 Total chunks: ${allChunks.length}`)

const embeddedChunks = await embedChunks(allChunks)
console.log(`✅ Embeddings: ${embeddedChunks.length} / ${allChunks.length}`)

const parts = [
  '// 自动生成，请勿手动编辑',
  `export const regulations      = ${JSON.stringify(regulations)};`,
  `export const authority        = ${JSON.stringify(authority)};`,
  `export const authorityMapping = ${JSON.stringify(authorityMapping)};`,
  `export const texts            = ${JSON.stringify(texts)};`,
  `export const diagrams         = ${JSON.stringify(diagrams)};`,
]

if (embeddedChunks.length > 0) {
  parts.push(`export const embeddings = ${JSON.stringify(embeddedChunks)};`)
} else {
  parts.push('export const embeddings = [];')
}

writeFileSync(outFile, parts.join('\n'), 'utf8')

const stat = readFileSync(outFile)
console.log(`📦 bundle.js 生成完成，大小 ${(stat.length / 1024 / 1024).toFixed(1)} MB`)
