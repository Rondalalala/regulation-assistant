<template>
  <div class="dm-page">
    <div class="page-header">
      <div>
        <h1 class="ph-title">数据管理</h1>
        <p class="ph-sub">上传任意格式的清单,AI 自动识别并标准化,无需关心列名是否匹配</p>
      </div>
      <button class="dm-btn ghost" @click="showLogs = !showLogs">
        {{ showLogs ? '关闭日志' : '查看日志' }}
      </button>
    </div>

    <div class="dm-body">
      <!-- 当前数据 -->
      <div class="dm-card">
        <h3>当前数据</h3>
        <div class="dm-stats">
          <div class="dm-stat">
            <div class="dm-stat-val">{{ config.regulations_count ?? '-' }}</div>
            <div class="dm-stat-lbl">{{ settings.regModuleName }}</div>
          </div>
          <div class="dm-stat">
            <div class="dm-stat-val">{{ config.authority_count ?? '-' }}</div>
            <div class="dm-stat-lbl">{{ settings.flowModuleName }}</div>
          </div>
          <div class="dm-stat">
            <div class="dm-stat-val">{{ config.texts_count ?? '-' }}</div>
            <div class="dm-stat-lbl">原文</div>
          </div>
          <div class="dm-stat">
            <div class="dm-stat-val">{{ config.diagrams_count ?? '-' }}</div>
            <div class="dm-stat-lbl">流程图</div>
          </div>
        </div>
        <p v-if="config.last_modified" class="dm-meta">最后更新:{{ formatTime(config.last_modified) }}</p>
      </div>

      <!-- AI 配置缺失提示 -->
      <div v-if="!aiConfigured" class="dm-card dm-warning">
        <h3>⚠️ 还没有配置 AI</h3>
        <p class="dm-hint">
          智能导入需要先在【设置】里配置 AI(API Key)。AI 会在后台静默把你上传的任意格式
          (列名/分类名不一致都没关系)转换为系统标准格式。
        </p>
        <router-link to="/settings" class="dm-btn primary">去设置 →</router-link>
      </div>

      <!-- 上传制度清单 -->
      <div class="dm-card">
        <h3>上传 {{ settings.regModuleName }}清单</h3>
        <p class="dm-hint">
          支持 .xlsx / .csv,列名可以是任意中文/英文。AI 会自动识别"制度名称""所属类别""主责部门"等并标准化。
        </p>
        <input ref="regFile" type="file" accept=".xlsx,.csv" style="display:none" @change="handleRegImport">
        <div class="dm-actions">
          <button class="dm-btn primary" :disabled="!aiConfigured || regImport.busy"
                  @click="$refs.regFile.click()">
            {{ regImport.busy ? regImport.label : '选择文件并智能导入' }}
          </button>
        </div>
        <div v-if="regImport.busy" class="dm-progress">
          <div class="dm-progress-bar"><div class="dm-progress-fill indeterminate"></div></div>
          <p class="dm-progress-label">{{ regImport.label }}</p>
        </div>
        <div v-if="regImport.result" class="dm-success">
          ✓ 已导入 {{ regImport.result.count }} 条 {{ settings.regModuleName }}
          (识别字段:{{ regImport.result.raw_columns.join('、') }};耗时
          {{ Math.round(regImport.result.duration_ms / 1000) }}s)
        </div>
        <div v-if="regImport.error" class="dm-error">{{ regImport.error }}</div>
      </div>

      <!-- 上传流程清单 -->
      <div class="dm-card">
        <h3>上传 {{ settings.flowModuleName }}清单</h3>
        <p class="dm-hint">
          支持 .xlsx / .csv,审批流程字段可以是 "A→B→C" 这种文本,AI 会自动拆分成结构化步骤。
        </p>
        <input ref="authFile" type="file" accept=".xlsx,.csv" style="display:none" @change="handleAuthImport">
        <div class="dm-actions">
          <button class="dm-btn primary" :disabled="!aiConfigured || authImport.busy"
                  @click="$refs.authFile.click()">
            {{ authImport.busy ? authImport.label : '选择文件并智能导入' }}
          </button>
        </div>
        <div v-if="authImport.busy" class="dm-progress">
          <div class="dm-progress-bar"><div class="dm-progress-fill indeterminate"></div></div>
          <p class="dm-progress-label">{{ authImport.label }}</p>
        </div>
        <div v-if="authImport.result" class="dm-success">
          ✓ 已导入 {{ authImport.result.count }} 条 {{ settings.flowModuleName }}
          (识别字段:{{ authImport.result.raw_columns.join('、') }};耗时
          {{ Math.round(authImport.result.duration_ms / 1000) }}s)
        </div>
        <div v-if="authImport.error" class="dm-error">{{ authImport.error }}</div>
      </div>

      <!-- 上传制度原文 -->
      <div class="dm-card">
        <h3>上传制度原文</h3>
        <p class="dm-hint">支持 .pdf / .docx,先填写制度编号(已导入的制度)再选文件</p>
        <div class="dm-row">
          <input v-model="pdfRegId" class="dm-input" placeholder="制度编号,如 1-1-1">
          <input ref="pdfFile" type="file" accept=".pdf,.docx" style="display:none" @change="handlePdfFile">
          <button class="dm-btn" :disabled="!pdfRegId.trim()" @click="$refs.pdfFile.click()">选择文件</button>
        </div>
        <div v-if="pdfPreview" class="dm-preview">
          <p>文本长度:{{ pdfPreview.text_length }} 字</p>
          <pre class="dm-text-preview">{{ pdfPreview.text_preview }}</pre>
          <button class="dm-btn primary" @click="confirmPdf">确认导入</button>
        </div>
      </div>

      <!-- AI 解析(对已导入的制度原文做结构化 + 流程图) -->
      <div class="dm-card">
        <h3>AI 智能解析(原文→结构化 + 流程图)</h3>
        <p class="dm-hint">把所有已导入原文的制度,用 AI 解析成章节/条款 + 自动生成 Mermaid 流程图</p>
        <div class="dm-actions">
          <button class="dm-btn primary" :disabled="!aiConfigured || parsing.status.value === 'running'" @click="startParse">
            {{ parsing.status.value === 'running' ? '解析中…' : '开始 AI 解析' }}
          </button>
          <button v-if="parsing.status.value === 'completed'" class="dm-btn" @click="saveParseResult">保存结果</button>
          <button v-if="parsing.status.value !== 'idle'" class="dm-btn ghost" @click="parsing.reset()">重置</button>
        </div>
        <div v-if="parsing.status.value === 'running'" class="dm-progress">
          <div class="dm-progress-bar">
            <div class="dm-progress-fill" :style="{ width: pct + '%' }"></div>
          </div>
          <p class="dm-progress-label">
            {{ parsing.progress.value }} / {{ parsing.total.value }}
            <span v-if="parsing.currentItem.value" class="dm-progress-cur">— {{ parsing.currentItem.value }}</span>
          </p>
        </div>
        <div v-if="parsing.error.value" class="dm-error">{{ parsing.error.value }}</div>
        <div v-if="parsing.status.value === 'completed'" class="dm-success">解析完成,可点击"保存结果"</div>
      </div>

      <!-- 调试日志 -->
      <div v-if="showLogs" class="dm-card dm-logs">
        <div class="dm-logs-header">
          <h3>后端调试日志</h3>
          <div class="dm-actions">
            <button class="dm-btn ghost" @click="loadLogs">刷新</button>
            <button class="dm-btn ghost" @click="clearLogs">清空</button>
          </div>
        </div>
        <div v-if="!logs.length" class="dm-hint">暂无日志</div>
        <div v-else class="dm-log-list">
          <div v-for="(l, i) in logs" :key="i" class="dm-log-row" :class="`lv-${l.level}`">
            <span class="lv-tag">{{ l.level }}</span>
            <span class="lv-scope">{{ l.scope }}</span>
            <span class="lv-time">{{ formatTime(l.ts) }}</span>
            <span class="lv-msg">{{ l.message }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useEnterprise } from '../composables/useEnterprise.js'
import { useSettings } from '../composables/useSettings.js'
import { useParsing } from '../composables/useParsing.js'

const { settings } = useEnterprise()
const { settings: aiSettings, isConfigured } = useSettings()
const parsing = useParsing()

const config = ref({})
const showLogs = ref(false)
const logs = ref([])
const pdfPreview = ref(null)
const pdfRegId = ref('')

const regImport = reactive({ busy: false, label: '', result: null, error: '' })
const authImport = reactive({ busy: false, label: '', result: null, error: '' })

const aiConfigured = computed(() => isConfigured())

const pct = computed(() => {
  const t = parsing.total.value || 0
  const p = parsing.progress.value || 0
  return t ? Math.min(100, Math.round((p / t) * 100)) : 0
})

async function fetchConfig() {
  const res = await fetch('/api/config')
  if (res.ok) config.value = await res.json()
}

async function loadLogs() {
  const res = await fetch('/api/debug/logs?limit=200')
  if (res.ok) {
    const data = await res.json()
    logs.value = (data.logs || []).slice().reverse()
  }
}

async function clearLogs() {
  await fetch('/api/debug/logs', { method: 'DELETE' })
  logs.value = []
}

watch(showLogs, (v) => { if (v) loadLogs() })

onMounted(fetchConfig)

function formatTime(ts) {
  if (!ts) return ''
  try {
    const d = new Date(ts)
    return d.toLocaleString('zh-CN', { hour12: false })
  } catch { return ts }
}

async function smartImport(kind, file, slot) {
  slot.busy = true
  slot.result = null
  slot.error = ''
  slot.label = '上传中…'

  const form = new FormData()
  form.append('file', file)
  form.append('kind', kind)
  form.append('base_url', aiSettings.baseUrl || '')
  form.append('api_key', aiSettings.apiKey || '')
  form.append('model', aiSettings.model || '')

  // 进度文案的 fake-stage(后端是同步的,这里只是给用户视觉反馈)
  let stage = 0
  const stageLabels = ['上传中…', 'AI 正在识别字段…', 'AI 正在标准化数据…', '保存中…']
  const timer = setInterval(() => {
    stage = Math.min(stage + 1, stageLabels.length - 1)
    slot.label = stageLabels[stage]
  }, 4000)

  try {
    const res = await fetch('/api/upload/smart-import', { method: 'POST', body: form })
    if (!res.ok) {
      let msg = `HTTP ${res.status}`
      try {
        const err = await res.json()
        msg = err.detail || msg
      } catch { /* ignore */ }
      throw new Error(msg)
    }
    slot.result = await res.json()
    await fetchConfig()
    if (showLogs.value) await loadLogs()
  } catch (e) {
    slot.error = e?.message || String(e)
  } finally {
    clearInterval(timer)
    slot.busy = false
    slot.label = ''
  }
}

async function handleRegImport(e) {
  const file = e.target.files?.[0]
  if (!file) return
  e.target.value = ''
  await smartImport('regulations', file, regImport)
}

async function handleAuthImport(e) {
  const file = e.target.files?.[0]
  if (!file) return
  e.target.value = ''
  await smartImport('authority', file, authImport)
}

async function handlePdfFile(e) {
  const file = e.target.files?.[0]
  if (!file) return
  e.target.value = ''
  if (!pdfRegId.value.trim()) {
    alert('请先输入制度编号')
    return
  }
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`/api/upload/regulation-pdf?reg_id=${encodeURIComponent(pdfRegId.value)}`, {
    method: 'POST',
    body: form,
  })
  if (!res.ok) {
    alert('解析失败:' + ((await res.json()).detail || res.status))
    return
  }
  pdfPreview.value = await res.json()
}

async function confirmPdf() {
  if (!pdfPreview.value) return
  const res = await fetch('/api/upload/confirm-pdf', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      reg_id: pdfPreview.value.reg_id,
      text: pdfPreview.value.text_preview,
      blocks: [{ type: 'para', text: pdfPreview.value.text_preview }],
    }),
  })
  if (!res.ok) {
    alert('导入失败:' + ((await res.json()).detail || res.status))
    return
  }
  pdfPreview.value = null
  await fetchConfig()
  alert('导入成功')
}

async function startParse() {
  const taskId = await parsing.startParsing('all', ['structure', 'diagrams'], {
    base_url: aiSettings.baseUrl,
    api_key: aiSettings.apiKey,
    model: aiSettings.model,
  })
  parsing.pollProgress(taskId)
}

async function saveParseResult() {
  await parsing.saveResult(parsing.taskId.value)
  await fetchConfig()
  alert('保存成功')
}
</script>

<style scoped>
.dm-page { min-height: 100%; }
.dm-body { padding: 0 24px 24px; display: flex; flex-direction: column; gap: 16px; }

.page-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 18px 24px 14px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 20px;
  background: var(--surface);
  box-shadow: 0 1px 0 var(--border);
  position: sticky; top: 0; z-index: 5;
}
.ph-title { font-size: 17px; font-weight: 700; color: var(--fg); line-height: 1.2; }
.ph-sub { font-size: 11.5px; color: var(--muted); margin-top: 2px; }

.dm-card {
  background: var(--surface);
  border: 1px solid var(--border); border-radius: 10px;
  padding: 18px 22px;
}
.dm-card h3 { font-size: 14px; font-weight: 600; margin-bottom: 10px; color: var(--fg); }
.dm-hint { font-size: 12px; color: var(--muted); margin-bottom: 10px; line-height: 1.6; }

.dm-warning { border-color: var(--warn, #d97706); background: rgba(217,119,6,0.04); }

.dm-stats { display: flex; gap: 24px; flex-wrap: wrap; }
.dm-stat { text-align: center; }
.dm-stat-val { font-size: 22px; font-weight: 700; color: var(--blue); }
.dm-stat-lbl { font-size: 11px; color: var(--muted); margin-top: 2px; }
.dm-meta { font-size: 12px; color: var(--subtle); margin-top: 8px; }

.dm-actions { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.dm-btn {
  padding: 7px 16px;
  border: 1px solid var(--border); border-radius: 6px;
  background: var(--bg); color: var(--fg);
  font-size: 13px; font-family: var(--font);
  cursor: pointer; transition: all 0.13s;
  text-decoration: none; display: inline-block;
}
.dm-btn:hover { border-color: var(--navy); color: var(--navy); }
.dm-btn.primary { background: var(--blue); color: white; border-color: var(--blue); }
.dm-btn.primary:hover { background: #1d4ed8; }
.dm-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.dm-btn.ghost { background: transparent; border-color: transparent; color: var(--muted); }

.dm-row { display: flex; gap: 8px; align-items: center; }
.dm-input {
  flex: 1; min-width: 120px;
  padding: 7px 10px;
  border: 1px solid var(--border); border-radius: 6px;
  font-size: 13px; font-family: var(--font);
  background: var(--bg); color: var(--fg);
}

.dm-preview { margin-top: 12px; }
.dm-text-preview {
  background: var(--bg); border: 1px solid var(--border); border-radius: 6px;
  padding: 10px; font-size: 12px; line-height: 1.6; max-height: 200px; overflow: auto;
  white-space: pre-wrap; margin-top: 8px;
}

.dm-progress { margin-top: 10px; }
.dm-progress-bar {
  height: 8px; background: var(--bg); border-radius: 4px; overflow: hidden;
}
.dm-progress-fill {
  height: 100%; background: var(--blue); border-radius: 4px;
  transition: width 0.3s ease;
}
.dm-progress-fill.indeterminate {
  width: 35% !important;
  background: linear-gradient(90deg, transparent, var(--blue), transparent);
  animation: dm-shimmer 1.4s infinite;
}
@keyframes dm-shimmer {
  0%   { transform: translateX(-100%); }
  100% { transform: translateX(285%); }
}
.dm-progress-label { font-size: 12px; color: var(--muted); margin-top: 4px; }
.dm-progress-cur { color: var(--fg); }

.dm-error { color: var(--danger); font-size: 12px; margin-top: 8px; line-height: 1.6; word-break: break-all; }
.dm-success { color: var(--success); font-size: 12px; margin-top: 8px; line-height: 1.6; }

/* 日志面板 */
.dm-logs-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.dm-log-list {
  border: 1px solid var(--border); border-radius: 6px;
  background: var(--bg);
  max-height: 360px; overflow: auto;
  font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  font-size: 11.5px;
}
.dm-log-row {
  display: grid;
  grid-template-columns: 60px 90px 130px 1fr;
  gap: 8px;
  padding: 5px 10px;
  border-bottom: 1px solid var(--border);
  line-height: 1.5;
}
.dm-log-row:last-child { border-bottom: none; }
.lv-tag { text-transform: uppercase; font-weight: 600; font-size: 10px; padding: 1px 6px; border-radius: 3px; text-align: center; align-self: start; }
.lv-info .lv-tag { background: rgba(37, 99, 235, 0.12); color: #2563eb; }
.lv-warn .lv-tag { background: rgba(217, 119, 6, 0.14); color: #d97706; }
.lv-error .lv-tag { background: rgba(220, 38, 38, 0.14); color: #dc2626; }
.lv-scope { color: var(--muted); }
.lv-time { color: var(--subtle); }
.lv-msg { color: var(--fg); word-break: break-word; }
</style>
