<!-- src/views/SettingsView.vue -->
<template>
  <div class="settings-page">
    <div class="sticky-header">
      <h2>AI 助手设置</h2>
    </div>

    <div class="settings-body">
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
import { ref } from 'vue'
import { useSettings } from '../composables/useSettings.js'

const { settings, setApiKey, setBaseUrl, setModel, testConnection } = useSettings()

const baseUrl = ref(settings.baseUrl)
const apiKey = ref(settings.apiKey)
const model = ref(settings.model)
const presetModels = ['jiaorong-instruct', 'jiaorong-deepseek-v4-flash']
const modelSelect = ref(presetModels.includes(settings.model) ? settings.model : '__custom')
const showKey = ref(false)
const saving = ref(false)
const testing = ref(false)
const testResult = ref(null)

function save() {
  saving.value = true
  setBaseUrl(baseUrl.value)
  setApiKey(apiKey.value)
  setModel(model.value)
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
</script>

<style scoped>
.settings-page { min-height: 100vh; }
.settings-body { padding: 0 24px 40px; max-width: 600px; }
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
</style>
