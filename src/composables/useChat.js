import { ref, computed } from 'vue'
import { retrieve, buildSystemPrompt } from './useRag.js'
import { streamChat, formatError } from './useLlm.js'
import { useSettings } from './useSettings.js'

const STORAGE_KEY = 'ai-chat-sessions'
const ACTIVE_KEY = 'ai-chat-active'
const OLD_KEY = 'ai-chat-history'
const MAX_MESSAGES = 50
const MAX_SESSIONS = 20

function genId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 6)
}

function genTitle(firstMsg) {
  const t = firstMsg.slice(0, 20).replace(/\n/g, ' ')
  return t.length < firstMsg.length ? t + '…' : t
}

function loadSessions() {
  try {
    const oldRaw = localStorage.getItem(OLD_KEY)
    if (oldRaw && !localStorage.getItem(STORAGE_KEY)) {
      const oldMsgs = JSON.parse(oldRaw)
      if (Array.isArray(oldMsgs) && oldMsgs.length) {
        const id = Date.now().toString(36) + 'migrate'
        const title = oldMsgs[0]?.content ? genTitle(oldMsgs[0].content) : '历史会话'
        const sessions = { [id]: { id, title, messages: oldMsgs.slice(-MAX_MESSAGES), createdAt: Date.now() } }
        localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions))
        localStorage.setItem(ACTIVE_KEY, id)
        localStorage.removeItem(OLD_KEY)
        return sessions
      }
      localStorage.removeItem(OLD_KEY)
    }
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : {}
  } catch { return {} }
}

function saveSessions(sessions) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions))
}

const allSessions = ref(loadSessions())
const activeId = ref(localStorage.getItem(ACTIVE_KEY) || genId())

if (!allSessions.value[activeId.value]) {
  allSessions.value[activeId.value] = { id: activeId.value, title: '新会话', messages: [], createdAt: Date.now() }
}

export const messages = ref(allSessions.value[activeId.value].messages || [])
export const isStreaming = ref(false)
export const isOpen = ref(false)
export const errorMsg = ref('')

export const sessionList = computed(() => {
  return Object.values(allSessions.value)
    .sort((a, b) => (b.messages[b.messages.length - 1]?.ts || b.createdAt) - (a.messages[a.messages.length - 1]?.ts || a.createdAt))
})

export const hasMessages = computed(() => messages.value.length > 0)

let abortCtrl = null

function syncToSession() {
  const s = allSessions.value[activeId.value]
  if (s) s.messages = messages.value
}

function syncFromSession() {
  const s = allSessions.value[activeId.value]
  messages.value = s ? [...s.messages] : []
}

function persist() {
  syncToSession()
  const sorted = Object.values(allSessions.value)
    .sort((a, b) => (b.messages[b.messages.length - 1]?.ts || b.createdAt) - (a.messages[a.messages.length - 1]?.ts || a.createdAt))
    .slice(0, MAX_SESSIONS)
  const trimmed = {}
  for (const s of sorted) {
    trimmed[s.id] = { ...s, messages: s.messages.slice(-MAX_MESSAGES) }
  }
  allSessions.value = trimmed
  saveSessions(trimmed)
  localStorage.setItem(ACTIVE_KEY, activeId.value)
}

export function useChat() {
  const { isConfigured } = useSettings()

  function togglePanel() { isOpen.value = !isOpen.value }
  function closePanel() { isOpen.value = false }

  function switchSession(id) {
    if (id === activeId.value || isStreaming.value) return
    syncToSession()
    activeId.value = id
    if (!allSessions.value[id]) {
      allSessions.value[id] = { id, title: '新会话', messages: [], createdAt: Date.now() }
    }
    syncFromSession()
    errorMsg.value = ''
    localStorage.setItem(ACTIVE_KEY, id)
  }

  function newSession() {
    const id = genId()
    allSessions.value[id] = { id, title: '新会话', messages: [], createdAt: Date.now() }
    activeId.value = id
    messages.value = []
    errorMsg.value = ''
    localStorage.setItem(ACTIVE_KEY, id)
    persist()
  }

  function deleteSession(id) {
    syncToSession()
    delete allSessions.value[id]
    if (activeId.value === id) {
      const remaining = Object.keys(allSessions.value)
      if (remaining.length) {
        activeId.value = remaining[0]
      } else {
        const newId = genId()
        allSessions.value[newId] = { id: newId, title: '新会话', messages: [], createdAt: Date.now() }
        activeId.value = newId
      }
      syncFromSession()
      localStorage.setItem(ACTIVE_KEY, activeId.value)
    }
    persist()
  }

  async function send(text, attachment) {
    if (!text.trim() || isStreaming.value) return
    if (!isConfigured()) {
      errorMsg.value = '请先在设置中配置 API Key'
      return
    }

    errorMsg.value = ''

    let userContent = text.trim()
    if (attachment) {
      userContent += `\n\n【用户附件：${attachment.name}】\n${attachment.content}`
    }

    messages.value.push({ role: 'user', content: userContent, ts: Date.now() })

    const session = allSessions.value[activeId.value]
    if (messages.value.length === 1 || session.title === '新会话') {
      session.title = genTitle(userContent)
    }

    const aiMsg = { role: 'assistant', content: '', ts: Date.now() }
    messages.value.push(aiMsg)
    messages.value = [...messages.value]

    isStreaming.value = true

    try {
      const results = await retrieve(text.trim())
      const systemPrompt = buildSystemPrompt(results)

      const history = messages.value.slice(0, -1).map(m => ({
        role: m.role,
        content: m.content,
      }))

      abortCtrl = new AbortController()
      aiMsg.content = await streamChat(
        systemPrompt,
        history,
        (token) => {
          aiMsg.content += token
          messages.value = [...messages.value]
        },
        abortCtrl.signal,
      )
    } catch (err) {
      if (err.name !== 'AbortError') {
        aiMsg.content = ''
        errorMsg.value = formatError(err)
      }
    } finally {
      isStreaming.value = false
      abortCtrl = null
      persist()
    }
  }

  function stopStreaming() {
    if (abortCtrl) abortCtrl.abort()
  }

  return {
    messages,
    isStreaming,
    isOpen,
    errorMsg,
    hasMessages,
    sessionList,
    activeId,
    togglePanel,
    closePanel,
    send,
    stopStreaming,
    newSession,
    switchSession,
    deleteSession,
  }
}
