<template>
  <div class="dm-page">
    <div class="page-header">
      <div>
        <h1 class="ph-title">数据管理</h1>
        <p class="ph-sub">导入制度、流程数据，运行 AI 解析</p>
      </div>
    </div>

    <div class="dm-body">
      <!-- 当前数据 -->
      <div class="dm-card">
        <h3>当前数据</h3>
        <div class="dm-stats">
          <div class="dm-stat">
            <div class="dm-stat-val">{{ config.regulations_count ?? '-' }}</div>
            <div class="dm-stat-lbl">制度文件</div>
          </div>
          <div class="dm-stat">
            <div class="dm-stat-val">{{ config.authority_count ?? '-' }}</div>
            <div class="dm-stat-lbl">流程事项</div>
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
        <p v-if="config.last_modified" class="dm-meta">最后更新：{{ config.last_modified }}</p>
      </div>

      <!-- 上传制度框架 -->
      <div class="dm-card">
        <h3>上传 {{ settings.regModuleName }}清单</h3>
        <p class="dm-hint">支持 .xlsx / .csv 格式</p>
        <input ref="regFile" type="file" accept=".xlsx,.csv" style="display:none" @change="handleRegFile">
        <div class="dm-actions">
          <button class="dm-btn" @click="$refs.regFile.click()">选择文件</button>
        </div>
        <div v-if="regPreview" class="dm-preview">
          <p>共 {{ regPreview.total_rows }} 条，预览前 {{ regPreview.preview_count }} 条：</p>
          <table class="dm-table">
            <thead><tr><th v-for="(v,k) in regPreview.preview[0]" :key="k">{{ k }}</th></tr></thead>
            <tbody><tr v-for="(row,i) in regPreview.preview" :key="i"><td v-for="(v,k) in row" :key="k">{{ v }}</td></tr></tbody>
          </table>
          <button class="dm-btn primary" @click="confirmRegulations">确认导入</button>
        </div>
      </div>

      <!-- 上传流程清单 -->
      <div class="dm-card">
        <h3>上传 {{ settings.flowModuleName }}清单</h3>
        <p class="dm-hint">支持 .xlsx / .csv 格式</p>
        <input ref="authFile" type="file" accept=".xlsx,.csv" style="display:none" @change="handleAuthFile">
        <div class="dm-actions">
          <button class="dm-btn" @click="$refs.authFile.click()">选择文件</button>
        </div>
        <div v-if="authPreview" class="dm-preview">
          <p>共 {{ authPreview.total_rows }} 条，预览前 {{ authPreview.preview_count }} 条：</p>
          <table class="dm-table">
            <thead><tr><th v-for="(v,k) in authPreview.preview[0]" :key="k">{{ k }}</th></tr></thead>
            <tbody><tr v-for="(row,i) in authPreview.preview" :key="i"><td v-for="(v,k) in row" :key="k">{{ v }}</td></tr></tbody>
          </table>
          <button class="dm-btn primary" @click="confirmAuthority">确认导入</button>
        </div>
      </div>

      <!-- 上传制度原文 -->
      <div class="dm-card">
        <h3>上传制度原文</h3>
        <p class="dm-hint">支持 .pdf / .docx 格式</p>
        <div class="dm-row">
          <input v-model="pdfRegId" class="dm-input" placeholder="制度编号，如 5-2-1">
          <input ref="pdfFile" type="file" accept=".pdf,.docx" style="display:none" @change="handlePdfFile">
          <button class="dm-btn" @click="$refs.pdfFile.click()">选择文件</button>
        </div>
        <div v-if="pdfPreview" class="dm-preview">
          <p>文本长度：{{ pdfPreview.text_length }} 字</p>
          <pre class="dm-text-preview">{{ pdfPreview.text_preview }}</pre>
          <button class="dm-btn primary" @click="confirmPdf">确认导入</button>
        </div>
      </div>

      <!-- AI 解析 -->
      <div class="dm-card">
        <h3>AI 智能解析</h3>
        <p class="dm-hint">自动解析制度结构并生成流程图（需要配置 API Key）</p>
        <div class="dm-actions">
          <button class="dm-btn primary" :disabled="parsing.status.value === 'running'" @click="startParse">
            {{ parsing.status.value === 'running' ? '解析中...' : '开始 AI 解析' }}
          </button>
          <button v-if="parsing.status.value === 'completed'" class="dm-btn" @click="saveParseResult">保存结果</button>
          <button v-if="parsing.status.value !== 'idle'" class="dm-btn ghost" @click="parsing.reset()">重置</button>
        </div>
        <div v-if="parsing.status.value === 'running'" class="dm-progress">
          <div class="dm-progress-bar">
            <div class="dm-progress-fill" :style="{width: (parsing.total.value ? (parsing.progress.value / parsing.total.value * 100) : 0) + '%'}"></div>
          </div>
          <p>{{ parsing.progress.value }} / {{ parsing.total.value }}</p>
        </div>
        <div v-if="parsing.error.value" class="dm-error">{{ parsing.error.value }}</div>
        <div v-if="parsing.status.value === 'completed'" class="dm-success">解析完成，可点击保存</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useEnterprise } from '../composables/useEnterprise.js'
import { useSettings } from '../composables/useSettings.js'
import { useParsing } from '../composables/useParsing.js'

const { settings } = useEnterprise()
const { settings: aiSettings } = useSettings()
const parsing = useParsing()

const config = ref({})
const regPreview = ref(null)
const authPreview = ref(null)
const pdfPreview = ref(null)
const pdfRegId = ref('')

async function fetchConfig() {
  const res = await fetch('/api/config')
  if (res.ok) config.value = await res.json()
}

onMounted(fetchConfig)

async function uploadFile(endpoint, file) {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`/api/upload/${endpoint}`, { method: 'POST', body: form })
  if (!res.ok) throw new Error((await res.json()).detail || `HTTP ${res.status}`)
  return res.json()
}

async function handleRegFile(e) {
  const file = e.target.files?.[0]
  if (!file) return
  e.target.value = ''
  regPreview.value = await uploadFile('regulations-excel', file)
}

async function confirmRegulations() {
  if (!regPreview.value) return
  const rows = regPreview.value.preview
  // In a real implementation we'd keep the full parsed data server-side
  // Here we just send preview rows as a simplified flow
  const res = await fetch('/api/upload/confirm-regulations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data: rows }),
  })
  if (!res.ok) throw new Error((await res.json()).detail || '导入失败')
  regPreview.value = null
  await fetchConfig()
  alert('导入成功')
}

async function handleAuthFile(e) {
  const file = e.target.files?.[0]
  if (!file) return
  e.target.value = ''
  authPreview.value = await uploadFile('authority-excel', file)
}

async function confirmAuthority() {
  if (!authPreview.value) return
  const rows = authPreview.value.preview
  const res = await fetch('/api/upload/confirm-authority', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data: rows }),
  })
  if (!res.ok) throw new Error((await res.json()).detail || '导入失败')
  authPreview.value = null
  await fetchConfig()
  alert('导入成功')
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
  if (!res.ok) throw new Error((await res.json()).detail || '解析失败')
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
  if (!res.ok) throw new Error((await res.json()).detail || '导入失败')
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
.dm-hint { font-size: 12px; color: var(--muted); margin-bottom: 10px; }

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
.dm-table { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 8px; }
.dm-table th, .dm-table td { padding: 6px 10px; border: 1px solid var(--border); text-align: left; }
.dm-table th { background: var(--accent-soft); font-weight: 600; }
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
.dm-error { color: var(--danger); font-size: 12px; margin-top: 8px; }
.dm-success { color: var(--success); font-size: 12px; margin-top: 8px; }
</style>
