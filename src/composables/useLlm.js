import { useSettings } from './useSettings.js'

function buildProxyHeaders(baseUrl, extra) {
  const isRemote = baseUrl.startsWith('http://') || baseUrl.startsWith('https://')
  const headers = { ...extra }
  if (isRemote) {
    headers['X-Api-Base'] = baseUrl.replace(/\/+$/, '')
  }
  return { headers, isRemote }
}

function resolveUrl(baseUrl, path) {
  const isRemote = baseUrl.startsWith('http://') || baseUrl.startsWith('https://')
  if (isRemote) return `/api-proxy/${path}`
  return `${baseUrl.replace(/\/+$/, '')}/${path}`
}

export async function streamChat(systemPrompt, history, onToken, signal) {
  const { settings } = useSettings()

  const recentHistory = history.slice(-10)

  const body = {
    model: settings.model,
    messages: [
      { role: 'system', content: systemPrompt },
      ...recentHistory,
    ],
    stream: false,
  }

  const { headers, isRemote } = buildProxyHeaders(settings.baseUrl, {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${settings.apiKey}`,
    'User-Agent': 'XBTZ-RegulationPlatform/2.0',
  })

  const url = resolveUrl(settings.baseUrl, 'chat/completions')

  const res = await fetch(url, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
    signal,
  })

  if (!res.ok) {
    const text = await res.text()
    const err = new Error(`API Error ${res.status}: ${text.slice(0, 200)}`)
    err.status = res.status
    err.body = text
    throw err
  }

  const data = await res.json()
  const full = data.choices?.[0]?.message?.content || ''
  onToken(full)
  return full
}

export async function embedText(text) {
  const { settings } = useSettings()

  const { headers } = buildProxyHeaders(settings.baseUrl, {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${settings.apiKey}`,
    'User-Agent': 'XBTZ-RegulationPlatform/2.0',
  })

  const url = resolveUrl(settings.baseUrl, 'embeddings')

  const res = await fetch(url, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      model: 'jiaorong-qwen3-embedding-8b',
      input: text,
    }),
  })

  if (!res.ok) {
    const err = new Error(`Embedding Error ${res.status}`)
    err.status = res.status
    throw err
  }

  const data = await res.json()
  return data.data[0].embedding
}

export function formatError(err) {
  if (err.name === 'AbortError') return '请求已取消'
  if (err.message.includes('Failed to fetch')) return '无法连接 AI 服务，请检查网络或 API 地址'
  if (err.status === 401 || err.status === 403) return 'API Key 无效或已过期，请检查设置'
  if (err.status === 429) return '请求过于频繁，请稍后再试'
  if (err.status === 500) return 'AI 服务暂时不可用，请稍后重试'
  return err.message || '未知错误'
}
