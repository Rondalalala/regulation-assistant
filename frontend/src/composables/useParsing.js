import { ref } from 'vue'

const API_BASE = '/api'

async function fetchJSON(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, options)
  if (!res.ok) {
    const body = await res.text()
    throw new Error(`HTTP ${res.status}: ${body.slice(0, 200)}`)
  }
  return res.json()
}

export function useParsing() {
  const status = ref('idle')
  const progress = ref(0)
  const total = ref(0)
  const error = ref(null)
  const result = ref(null)
  const taskId = ref('')
  let pollTimer = null

  async function startParsing(scope, tasks, llmConfig) {
    status.value = 'running'
    progress.value = 0
    total.value = 0
    error.value = null
    result.value = null

    const data = await fetchJSON('/parse/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scope, tasks, llm_config: llmConfig }),
    })

    total.value = data.total || 0
    taskId.value = data.task_id
    return data.task_id
  }

  function reset() {
    stopPoll()
    status.value = 'idle'
    progress.value = 0
    total.value = 0
    error.value = null
    result.value = null
    taskId.value = ''
  }

  function pollProgress(taskId, onUpdate) {
    stopPoll()

    async function tick() {
      try {
        const data = await fetchJSON(`/parse/progress/${encodeURIComponent(taskId)}`)
        status.value = data.status
        progress.value = data.progress || 0
        total.value = data.total || total.value
        if (onUpdate) onUpdate(data)

        if (data.status === 'running') {
          pollTimer = setTimeout(tick, 2000)
        } else if (data.status === 'completed') {
          progress.value = total.value
        } else if (data.status === 'failed') {
          error.value = data.error || '解析失败'
        }
      } catch (err) {
        error.value = err.message
        status.value = 'failed'
      }
    }

    tick()
  }

  function stopPoll() {
    if (pollTimer) {
      clearTimeout(pollTimer)
      pollTimer = null
    }
  }

  async function getResult(taskId) {
    const data = await fetchJSON(`/parse/result/${encodeURIComponent(taskId)}`)
    result.value = data
    return data
  }

  async function saveResult(taskId) {
    const data = await fetchJSON(`/parse/save/${encodeURIComponent(taskId)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    })
    return data.saved
  }

  return {
    status,
    progress,
    total,
    error,
    result,
    taskId,
    startParsing,
    pollProgress,
    stopPoll,
    getResult,
    saveResult,
    reset,
  }
}
