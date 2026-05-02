import { reactive } from 'vue'

const STORAGE_KEY = 'ai-settings'

const defaults = {
  baseUrl: 'https://c4ai.ccccltd.cn/api/compatible/v1',
  apiKey: '',
  model: 'jiaorong-instruct',
}

function load() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { ...defaults }
    const saved = JSON.parse(raw)
    return { ...defaults, ...saved }
  } catch {
    return { ...defaults }
  }
}

function save(s) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    baseUrl: s.baseUrl,
    apiKey: btoa(s.apiKey),
    model: s.model,
  }))
}

const state = reactive(load())

// Migrate old local proxy path to real URL
if (state.baseUrl.startsWith('/jrcc-api')) {
  state.baseUrl = 'https://c4ai.ccccltd.cn/api/compatible/v1'
  save(state)
}

if (state.apiKey && !state.apiKey.startsWith('sk-')) {
  try { state.apiKey = atob(state.apiKey) } catch { /* already plaintext */ }
}

function resolveUrl(baseUrl, path) {
  const isRemote = baseUrl.startsWith('http://') || baseUrl.startsWith('https://')
  if (isRemote) return `/api-proxy/${path}`
  return `${baseUrl.replace(/\/+$/, '')}/${path}`
}

export function useSettings() {
  function setApiKey(key) { state.apiKey = key; save(state) }
  function setBaseUrl(url) { state.baseUrl = url; save(state) }
  function setModel(m) { state.model = m; save(state) }
  function isConfigured() { return !!state.apiKey }

  async function testConnection() {
    if (!state.apiKey) throw new Error('未配置 API Key')

    const isRemote = state.baseUrl.startsWith('http://') || state.baseUrl.startsWith('https://')
    const headers = {
      'Authorization': `Bearer ${state.apiKey}`,
      'User-Agent': 'XBTZ-RegulationPlatform/2.0',
    }
    if (isRemote) headers['X-Api-Base'] = state.baseUrl.replace(/\/+$/, '')

    const url = resolveUrl(state.baseUrl, 'models')
    const res = await fetch(url, { headers })
    if (!res.ok) {
      const body = await res.text()
      throw new Error(`HTTP ${res.status}: ${body.slice(0, 200)}`)
    }
    return await res.json()
  }

  return { settings: state, setApiKey, setBaseUrl, setModel, isConfigured, testConnection }
}
