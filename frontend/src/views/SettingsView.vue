<!-- src/views/SettingsView.vue -->
<template>
  <div class="settings-page">
    <div class="sticky-header">
      <h2>AI 助手设置</h2>
    </div>

    <div class="settings-body">
      <!-- 企业信息配置 -->
      <div class="card settings-card">
        <h3>企业信息</h3>

        <div class="field">
          <label>应用名称</label>
          <input v-model="appName" type="text" class="input" placeholder="制度助手">
          <span class="hint">显示在页面标题、侧边栏 Logo 等位置</span>
        </div>

        <div class="field">
          <label>制度模块名称</label>
          <input v-model="regModuleName" type="text" class="input" placeholder="制度管理">
          <span class="hint">替代默认的“制度库”等叫法</span>
        </div>

        <div class="field">
          <label>流程模块名称</label>
          <input v-model="flowModuleName" type="text" class="input" placeholder="流程管理">
          <span class="hint">替代默认的“权责清单”等叫法</span>
        </div>

        <div class="field">
          <label>企业名称</label>
          <input v-model="companyName" type="text" class="input" placeholder="">
          <span class="hint">用于落地页、AI 助手欢迎语等品牌展示，留空则不显示</span>
        </div>
      </div>

      <!-- API 配置 -->
      <div class="card settings-card">
        <h3>API 配置</h3>

        <div class="field">
          <label>API Base URL</label>
          <input v-model="baseUrl" type="text" class="input" placeholder="https://...">
          <span class="hint">交融大模型默认地址，也可填入其他 OpenAI 兼容 API 地址（如阿里通义、智谱 GLM 等）</span>
        </div>

        <div class="field">
          <label>API Key</label>
          <div class="key-row">
            <input v-model="apiKey" :type="showKey ? 'text' : 'password'" class="input" placeholder="sk-...">
            <button class="toggle-key" @click="showKey = !showKey">{{ showKey ? '隐藏' : '显示' }}</button>
          </div>
          <span class="hint">在交融大模型平台获取的 API Key</span>
        </div>

        <div class="field">
          <label>模型</label>
          <select v-model="modelSelect" class="input" @change="onModelSelect">
            <option value="jiaorong-instruct">jiaorong-instruct（推荐）</option>
            <option value="jiaorong-deepseek-v4-flash">jiaorong-deepseek-v4-flash</option>
            <option value="__custom">自定义模型...</option>
          </select>
          <input
            v-if="modelSelect === '__custom'"
            v-model="model"
            type="text"
            class="input custom-model"
            placeholder="输入模型名称，如 qwen-plus"
          >
        </div>
      </div>

      <!-- 向量搜索配置 -->
      <div class="card settings-card">
        <h3>向量搜索配置</h3>

        <div class="field">
          <label>向量模型</label>
          <input v-model="embedModel" type="text" class="input" placeholder="jiaorong-qwen3-embedding-8b">
          <span class="hint">用于 AI 助手语义检索的向量化模型，需与索引构建时使用的模型一致</span>
        </div>

        <div class="field">
          <label>向量 API Base URL（可选）</label>
          <input v-model="embedBaseUrl" type="text" class="input" placeholder="留空则复用上方 API 地址">
          <span class="hint">如需使用独立的 Embedding API 服务，可单独配置</span>
        </div>

        <div class="field">
          <label>向量 API Key（可选）</label>
          <div class="key-row">
            <input v-model="embedApiKey" :type="showEmbedKey ? 'text' : 'password'" class="input" placeholder="留空则复用上方 Key">
            <button class="toggle-key" @click="showEmbedKey = !showEmbedKey">{{ showEmbedKey ? '隐藏' : '显示' }}</button>
          </div>
          <span class="hint">留空则使用上方 API Key</span>
        </div>
      </div>

      <!-- 搜索索引管理 -->
      <div class="card settings-card">
        <h3>搜索索引状态</h3>

        <div v-if="indexStatus.exists" class="index-info">
          <p><span class="dot ok"/> 状态：已构建</p>
          <p>模型：{{ indexStatus.model }} | 条目数：{{ indexStatus.count }}</p>
          <p>生成时间：{{ formatDate(indexStatus.generated_at) }}</p>
        </div>
        <div v-else class="index-info">
          <p><span class="dot warn"/> 状态：未构建</p>
          <p>AI 助手目前使用关键词搜索，语义搜索需先构建向量索引。</p>
          <p class="hint">预计耗时约 2-3 分钟（811 条 / 20 条/批）</p>
        </div>

        <div v-if="indexProgress != null" class="progress-bar-wrap">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: indexProgress + '%' }"/>
          </div>
          <p class="progress-text">已处理 {{ indexDone }} / {{ indexTotal }}</p>
        </div>

        <div class="actions" style="margin-top:18px">
          <button
            class="btn primary"
            @click="buildIdx"
            :disabled="building || !apiKey"
          >
            {{ building ? '构建中...' : '重建索引' }}
          </button>
          <button
            class="btn"
            @click="clearIdx"
            :disabled="building || !indexStatus.exists"
          >
            清除索引
          </button>
        </div>
      </div>

      <!-- 保存 + 测试 -->
      <div class="card settings-card" style="margin-top:0">
        <div class="actions">
          <button class="btn primary" @click="save" :disabled="saving">
            {{ saving ? '保存中...' : '保存配置' }}
          </button>
          <button class="btn" @click="testConn" :disabled="testing || !apiKey">
            {{ testing ? '测试中...' : '测试连接' }}
          </button>
        </div>

        <div v-if="testResult" :class="['test-result', testResult.ok ? 'ok' : 'fail']">
          {{ testResult.msg }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useSettings } from '../composables/useSettings.js'
import { useEnterprise } from '../composables/useEnterprise.js'
import { buildIndex, getIndexStatus, clearIndex } from '../composables/useRag.js'

const {
  settings,
  setApiKey, setBaseUrl, setModel,
  setEmbedModel, setEmbedBaseUrl, setEmbedApiKey,
  testConnection,
} = useSettings()

const {
  settings: entSettings,
  setAppName, setRegModuleName, setFlowModuleName, setCompanyName,
} = useEnterprise()

const baseUrl = ref(settings.baseUrl)
const apiKey = ref(settings.apiKey)
const model = ref(settings.model)
const embedModel = ref(settings.embedModel)
const embedBaseUrl = ref(settings.embedBaseUrl)
const embedApiKey = ref(settings.embedApiKey)

const appName = ref(entSettings.appName)
const regModuleName = ref(entSettings.regModuleName)
const flowModuleName = ref(entSettings.flowModuleName)
const companyName = ref(entSettings.companyName)

const presetModels = ['jiaorong-instruct', 'jiaorong-deepseek-v4-flash']
const modelSelect = ref(presetModels.includes(settings.model) ? settings.model : '__custom')
const showKey = ref(false)
const showEmbedKey = ref(false)
const saving = ref(false)
const testing = ref(false)
const testResult = ref(null)

const indexStatus = ref({ exists: false })
const building = ref(false)
const indexDone = ref(0)
const indexTotal = ref(0)
const indexProgress = ref(null)

onMounted(() => {
  indexStatus.value = getIndexStatus()
})

function save() {
  saving.value = true
  setBaseUrl(baseUrl.value)
  setApiKey(apiKey.value)
  setModel(model.value)
  setEmbedModel(embedModel.value)
  setEmbedBaseUrl(embedBaseUrl.value)
  setEmbedApiKey(embedApiKey.value)
  setAppName(appName.value)
  setRegModuleName(regModuleName.value)
  setFlowModuleName(flowModuleName.value)
  setCompanyName(companyName.value)
  saving.value = false
  testResult.value = { ok: true, msg: '配置已保存' }
}

function onModelSelect() {
  if (modelSelect.value !== '__custom') {
    model.value = modelSelect.value
  } else {
    model.value = ''
  }
}

async function testConn() {
  save()
  testing.value = true
  testResult.value = null
  try {
    const data = await testConnection()
    const count = data.data?.length || 0
    testResult.value = { ok: true, msg: `连接成功，可用模型 ${count} 个` }
  } catch (err) {
    testResult.value = { ok: false, msg: `连接失败：${err.message}` }
  } finally {
    testing.value = false
  }
}

async function buildIdx() {
  save()
  if (!apiKey.value) {
    testResult.value = { ok: false, msg: '请先配置 API Key' }
    return
  }
  building.value = true
  indexProgress.value = 0
  indexDone.value = 0
  indexTotal.value = 0
  testResult.value = null
  try {
    await buildIndex((done, total) => {
      indexDone.value = done
      indexTotal.value = total
      indexProgress.value = total > 0 ? Math.round((done / total) * 100) : 0
    })
    indexStatus.value = getIndexStatus()
    testResult.value = { ok: true, msg: `索引构建完成，共 ${indexDone.value} 条` }
  } catch (err) {
    testResult.value = { ok: false, msg: `索引构建失败：${err.message}` }
  } finally {
    building.value = false
    indexProgress.value = null
  }
}

function clearIdx() {
  clearIndex()
  indexStatus.value = getIndexStatus()
  testResult.value = { ok: true, msg: '索引已清除' }
}

function formatDate(ts) {
  if (!ts) return '-'
  const d = new Date(ts)
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}
</script>

<style scoped>
.settings-page { min-height: 100vh; }
.settings-body { padding: 0 24px 40px; max-width: 600px; }
.settings-card { margin-bottom: 20px; }
.settings-card h3 { font-size: 15px; margin-bottom: 20px; color: var(--fg); }
.field { margin-bottom: 18px; }
.field label { display: block; font-size: 12px; font-weight: 600; color: var(--muted); margin-bottom: 6px; }
.input {
  width: 100%; padding: 8px 12px; border: 1px solid var(--border); border-radius: 6px;
  font-size: 13px; font-family: var(--font); background: var(--surface); color: var(--fg);
  outline: none; transition: border-color 0.15s;
}
.input:focus { border-color: var(--blue); }
select.input { cursor: pointer; }
.custom-model { margin-top: 8px; }
.hint { font-size: 11px; color: var(--subtle); margin-top: 4px; display: block; }
.key-row { display: flex; gap: 8px; }
.key-row .input { flex: 1; }
.toggle-key {
  padding: 0 12px; background: var(--bg); border: 1px solid var(--border); border-radius: 6px;
  font-size: 11px; color: var(--muted); cursor: pointer; white-space: nowrap;
}
.toggle-key:hover { border-color: var(--blue); color: var(--blue); }
.actions { display: flex; gap: 10px; margin-top: 24px; }
.btn {
  padding: 8px 20px; border-radius: 6px; font-size: 13px; font-family: var(--font);
  cursor: pointer; border: 1px solid var(--border); background: var(--surface); color: var(--fg);
  transition: all 0.15s;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn.primary { background: var(--blue); color: white; border-color: var(--blue); }
.btn.primary:hover:not(:disabled) { background: #1d4ed8; }
.test-result {
  margin-top: 14px; padding: 10px 14px; border-radius: 6px;
  font-size: 12px;
}
.test-result.ok { background: var(--success-bg); color: var(--success); border: 1px solid #BBF7D0; }
.test-result.fail { background: #FEF2F2; color: var(--danger); border: 1px solid #FECACA; }

.index-info { font-size: 12.5px; color: var(--fg); }
.index-info p { margin-bottom: 4px; }
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.dot.ok { background: #22C55E; }
.dot.warn { background: #F59E0B; }
.progress-bar-wrap { margin-top: 12px; }
.progress-bar {
  height: 6px; background: var(--border); border-radius: 3px; overflow: hidden;
}
.progress-fill {
  height: 100%; background: var(--blue); border-radius: 3px;
  transition: width 0.2s;
}
.progress-text { font-size: 11px; color: var(--muted); margin-top: 6px; }
</style>
