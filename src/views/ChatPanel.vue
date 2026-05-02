<!-- src/views/ChatPanel.vue -->
<template>
  <Transition name="slide">
    <div v-if="isOpen" class="chat-panel">
      <div class="chat-header">
        <button class="chat-icon-btn" @click="showHistory = !showHistory" :title="showHistory ? '返回对话' : '历史会话'">
          <svg v-if="!showHistory" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 19l-7-7 7-7"/></svg>
        </button>
        <span class="chat-title">{{ showHistory ? '历史会话' : 'AI 智能助手' }}</span>
        <button class="chat-icon-btn" @click="handleNewChat" title="新建会话">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg>
        </button>
        <router-link to="/settings" class="chat-icon-btn" title="设置">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72 1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
        </router-link>
        <button class="chat-icon-btn" @click="closePanel" title="关闭">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12"/></svg>
        </button>
      </div>

      <!-- Session history list -->
      <div v-if="showHistory" class="chat-body">
        <div v-if="sessionList.length === 0" class="chat-empty">暂无历史会话</div>
        <div v-for="s in sessionList" :key="s.id"
          :class="['session-item', { active: s.id === activeId }]"
          @click="switchAndReturn(s.id)">
          <div class="session-info">
            <div class="session-title">{{ s.title }}</div>
            <div class="session-meta">{{ s.messages.length }} 条消息 · {{ timeAgo(s.messages[s.messages.length - 1]?.ts || s.createdAt) }}</div>
          </div>
          <template v-if="pendingDeleteId === s.id">
            <button class="session-confirm-btn confirm-yes" @click.stop="doDelete(s.id)">删除</button>
            <button class="session-confirm-btn confirm-no" @click.stop="pendingDeleteId = null">取消</button>
          </template>
          <button v-else class="session-del" @click.stop="confirmDelete(s.id)" title="删除">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12"/></svg>
          </button>
        </div>
      </div>

      <!-- Chat messages -->
      <template v-else>
        <div class="chat-body" ref="bodyRef">
          <div v-if="!hasMessages" class="chat-welcome">
            <div class="welcome-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--blue)" stroke-width="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            </div>
            <p class="welcome-text">你好！我是中交西北投资制度管理 AI 助手，可以帮你查询业务流程和审批要求。</p>
            <div class="welcome-examples">
              <button v-for="ex in examples" :key="ex" class="example-btn" @click="send(ex)">{{ ex }}</button>
            </div>
          </div>

          <div v-for="(msg, i) in messages" :key="i" :class="['chat-msg', `msg-${msg.role}`]">
            <div class="msg-avatar">{{ msg.role === 'user' ? '你' : 'AI' }}</div>
            <div class="msg-body">
              <div class="msg-content" v-html="renderMarkdown(msg.content)"></div>
              <span v-if="msg.role === 'assistant' && !msg.content && isStreaming && i === messages.length - 1" class="msg-loading">正在思考<span class="thinking-dots"></span></span>
            </div>
          </div>

          <div v-if="errorMsg" class="chat-error">
            <span>{{ errorMsg }}</span>
            <button @click="retry">重试</button>
          </div>
        </div>

        <div class="chat-input-area">
          <div v-if="!isConfigured()" class="input-hint">
            请先<router-link to="/settings">配置 API Key</router-link>后使用
          </div>
          <div v-else class="input-row">
            <div v-if="pendingFile" class="attachment-preview">
              <span class="att-name">{{ pendingFile.name }}</span>
              <button class="att-remove" @click="pendingFile = null">&times;</button>
            </div>
            <div class="input-controls">
              <button class="attach-btn" @click="triggerFileInput" title="添加附件">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"/></svg>
              </button>
              <textarea ref="inputRef" v-model="inputText" class="chat-input" placeholder="输入你的问题..." rows="1" @keydown.enter.exact.prevent="handleSend" @input="autoResize"></textarea>
              <button v-if="isStreaming" class="send-btn stop" @click="stopStreaming" title="停止">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>
              </button>
              <button v-else class="send-btn" :disabled="!inputText.trim() && !pendingFile" @click="handleSend" title="发送">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m22 2-7 20-4-9-9-4z"/><path d="m22 2-11 11"/></svg>
              </button>
            </div>
            <input ref="fileInputRef" type="file" accept=".txt,.pdf,.doc,.docx,.xls,.xlsx,.csv,.json,.md,.png,.jpg,.jpeg" style="display:none" @change="handleFileSelect">
          </div>
        </div>
      </template>
    </div>
  </Transition>
</template>

<script setup>
import { ref, nextTick, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useChat } from '../composables/useChat.js'
import { useSettings } from '../composables/useSettings.js'

const router = useRouter()
const { messages, isStreaming, isOpen, errorMsg, hasMessages, sessionList, activeId,
  closePanel, send, stopStreaming, newSession, switchSession, deleteSession } = useChat()
const { isConfigured } = useSettings()

const inputText = ref('')
const bodyRef = ref(null)
const inputRef = ref(null)
const fileInputRef = ref(null)
const lastQuery = ref('')
const pendingFile = ref(null)
const showHistory = ref(false)
const pendingDeleteId = ref(null)

const examples = [
  '采购办公设备需要走什么流程？',
  '差旅报销需要哪些审批？',
  '合同签订的审批权限是怎样的？',
]

function handleSend() {
  if (!inputText.value.trim() && !pendingFile.value) return
  lastQuery.value = inputText.value
  send(inputText.value, pendingFile.value)
  inputText.value = ''
  pendingFile.value = null
  nextTick(() => autoResize())
}

function handleNewChat() {
  newSession()
  showHistory.value = false
}

function switchAndReturn(id) {
  switchSession(id)
  showHistory.value = false
}

function confirmDelete(id) {
  pendingDeleteId.value = id
}

function doDelete(id) {
  deleteSession(id)
  pendingDeleteId.value = null
}

function timeAgo(ts) {
  if (!ts) return ''
  const diff = Date.now() - ts
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return Math.floor(diff / 60000) + ' 分钟前'
  if (diff < 86400000) return Math.floor(diff / 3600000) + ' 小时前'
  return Math.floor(diff / 86400000) + ' 天前'
}

function triggerFileInput() { fileInputRef.value?.click() }

async function handleFileSelect(e) {
  const file = e.target.files?.[0]
  if (!file) return
  e.target.value = ''

  const textExts = ['.txt', '.md', '.csv', '.json']
  const isText = textExts.some(t => file.name.toLowerCase().endsWith(t))

  if (isText || file.type.startsWith('text/')) {
    const content = await file.text()
    pendingFile.value = { name: file.name, content: content.slice(0, 10000), type: 'text' }
  } else if (file.type.startsWith('image/')) {
    pendingFile.value = { name: file.name, content: `[用户上传了图片: ${file.name}]`, type: 'image' }
  } else {
    pendingFile.value = { name: file.name, content: `[用户上传了文件: ${file.name}]`, type: 'file' }
  }
}

function retry() { if (lastQuery.value) send(lastQuery.value) }

function autoResize() {
  const el = inputRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 120) + 'px'
}

function renderMarkdown(text) {
  if (!text) return ''
  return text
    // Code blocks (```)
    .replace(/```([\s\S]*?)```/g, '<pre class="md-code"><code>$1</code></pre>')
    // Inline code
    .replace(/`([^`]+)`/g, '<code class="md-inline-code">$1</code>')
    // Bold
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // Unordered list items
    .replace(/^[-*]\s+(.+)$/gm, '<li>$1</li>')
    // Ordered list items
    .replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>')
    // Links (must come after code to avoid matching inside code)
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, href) => {
      if (href.startsWith('#')) {
        const safeHref = href.replace(/'/g, "\\'")
        return `<a href="${href}" class="deep-link" onclick="event.preventDefault();window.__chatDeepLink?.('${safeHref}')">${label}</a>`
      }
      return `<a href="${href}" target="_blank">${label}</a>`
    })
    // Wrap consecutive <li> in <ul>
    .replace(/((?:<li>.*?<\/li>\s*)+)/g, '<ul class="md-list">$1</ul>')
    // Line breaks (skip if inside <pre>)
    .replace(/\n/g, '<br>')
}

watch(() => messages.value.length, () => {
  nextTick(() => { if (bodyRef.value) bodyRef.value.scrollTop = bodyRef.value.scrollHeight })
})

onMounted(() => {
  window.__chatDeepLink = (href) => {
    const path = href.startsWith('#') ? href.slice(1) : href
    router.push(path)
  }
})
onUnmounted(() => { delete window.__chatDeepLink })
</script>

<style scoped>
.chat-panel {
  width: 380px; min-width: 320px;
  height: 100vh; position: sticky; top: 0;
  display: flex; flex-direction: column;
  background: var(--surface);
  border-left: 1px solid var(--border);
  box-shadow: -4px 0 20px rgba(0,0,0,0.06);
  z-index: 20;
}
.chat-header {
  display: flex; align-items: center; gap: 8px;
  padding: 14px 16px; border-bottom: 1px solid var(--border);
  background: var(--surface); flex-shrink: 0;
}
.chat-title { flex: 1; font-size: 14px; font-weight: 700; color: var(--fg); }
.chat-icon-btn {
  width: 28px; height: 28px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  background: none; border: none; color: var(--muted);
  cursor: pointer; transition: all 0.15s; text-decoration: none;
}
.chat-icon-btn:hover { background: var(--blue-soft); color: var(--blue); }
.chat-icon-btn:active { transform: scale(0.92); }
.chat-body {
  flex: 1; overflow-y: auto; padding: 16px;
  display: flex; flex-direction: column; gap: 16px;
}
.chat-empty { text-align: center; color: var(--muted); padding: 40px 0; font-size: 13px; }
.chat-welcome { display: flex; flex-direction: column; align-items: center; padding: 40px 20px; text-align: center; }
.welcome-icon { width: 56px; height: 56px; border-radius: 50%; background: var(--accent-soft); display: flex; align-items: center; justify-content: center; margin-bottom: 16px; }
.welcome-text { font-size: 13px; color: var(--muted); line-height: 1.6; margin-bottom: 20px; }
.welcome-examples { display: flex; flex-direction: column; gap: 8px; width: 100%; }
.example-btn {
  padding: 10px 14px; border: 1px solid var(--border); border-radius: 8px;
  background: var(--surface); color: var(--fg); font-size: 12.5px;
  cursor: pointer; text-align: left; transition: all 0.15s; font-family: var(--font);
}
.example-btn:hover { border-color: var(--blue); background: var(--accent-soft); }

/* Session list */
.session-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: 8px;
  cursor: pointer; transition: background 0.13s;
  border: 1px solid transparent;
}
.session-item:hover { background: var(--blue-soft); }
.session-item.active { background: var(--accent-soft); border-color: var(--blue); }
.session-info { flex: 1; min-width: 0; }
.session-title {
  font-size: 13px; font-weight: 500; color: var(--fg);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.session-meta { font-size: 11px; color: var(--muted); margin-top: 2px; }
.session-del {
  width: 24px; height: 24px; border-radius: 4px;
  display: flex; align-items: center; justify-content: center;
  background: none; border: none; color: var(--muted);
  cursor: pointer; opacity: 0; transition: all 0.15s; flex-shrink: 0;
}
.session-item:hover .session-del { opacity: 1; }
.session-del:hover { background: #FEE2E2; color: var(--danger); }
.session-del:active { transform: scale(0.9); }
.session-confirm-btn {
  padding: 2px 8px; border-radius: 4px; font-size: 11px;
  cursor: pointer; border: none; white-space: nowrap;
}
.confirm-yes { background: #FEE2E2; color: var(--danger); }
.confirm-yes:hover { background: #FCA5A5; }
.confirm-no { background: var(--bg); color: var(--muted); border: 1px solid var(--border); }
.confirm-no:hover { background: var(--surface); }

.chat-msg { display: flex; gap: 10px; }
.msg-user { flex-direction: row-reverse; }
.msg-avatar {
  width: 30px; height: 30px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 600;
}
.msg-user .msg-avatar { background: var(--blue); color: white; }
.msg-assistant .msg-avatar { background: var(--accent-soft); color: var(--blue); }
.msg-body { max-width: 85%; }
.msg-content { font-size: 13px; line-height: 1.7; color: var(--fg); word-break: break-word; }
.msg-user .msg-content { background: var(--blue); color: white; padding: 10px 14px; border-radius: 12px 12px 4px 12px; }
.msg-assistant .msg-content { background: var(--accent-soft); padding: 10px 14px; border-radius: 12px 12px 12px 4px; }
.msg-loading { background: none; color: var(--muted); font-size: 12px; cursor: default; padding: 0; animation: pulse 1.5s ease-in-out infinite; }
.thinking-dots::after { content: ''; animation: dots 1.2s steps(3) infinite; }
@keyframes dots { 0% { content: '.' } 33% { content: '..' } 66% { content: '...' } }
@keyframes pulse { 0%, 100% { opacity: 1 } 50% { opacity: 0.5 } }
:deep(.deep-link) { color: var(--blue); text-decoration: underline; cursor: pointer; font-weight: 500; }
:deep(.deep-link:hover) { color: var(--blue-light); }
:deep(.md-list) { margin: 6px 0; padding-left: 20px; }
:deep(.md-list li) { margin: 3px 0; font-size: 13px; line-height: 1.7; }
:deep(.md-code) { background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 10px 14px; margin: 8px 0; overflow-x: auto; font-size: 12px; line-height: 1.5; }
:deep(.md-inline-code) { background: var(--bg); padding: 1px 5px; border-radius: 3px; font-size: 12px; font-family: var(--mono); }
.chat-error {
  display: flex; align-items: center; justify-content: space-between;
  background: #FEF2F2; border: 1px solid #FECACA; border-radius: 8px;
  padding: 10px 14px; font-size: 12px; color: var(--danger);
}
.chat-error button { background: none; border: 1px solid #FECACA; border-radius: 4px; color: var(--danger); font-size: 11px; padding: 2px 10px; cursor: pointer; }
.chat-input-area { padding: 12px 16px; border-top: 1px solid var(--border); background: var(--surface); flex-shrink: 0; }
.input-hint { font-size: 12px; color: var(--muted); text-align: center; padding: 8px 0; }
.input-hint a { color: var(--blue); font-weight: 500; }
.input-row { display: flex; flex-direction: column; gap: 6px; }
.input-controls { display: flex; align-items: flex-end; gap: 6px; }
.chat-input {
  flex: 1; resize: none; border: 1px solid var(--border); border-radius: 8px;
  padding: 9px 12px; font-size: 13px; font-family: var(--font);
  outline: none; background: var(--bg); color: var(--fg);
  max-height: 120px; line-height: 1.5;
}
.chat-input:focus { border-color: var(--blue); }
.send-btn {
  width: 36px; height: 36px; border-radius: 8px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  background: var(--blue); color: white; border: none;
  cursor: pointer; transition: all 0.15s;
}
.send-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.send-btn:hover:not(:disabled) { background: #1d4ed8; }
.send-btn.stop { background: var(--danger); }
.attach-btn {
  width: 32px; height: 32px; border-radius: 6px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  background: none; border: none; color: var(--muted);
  cursor: pointer; transition: color 0.15s;
}
.attach-btn:hover { color: var(--blue); }
.attachment-preview {
  display: flex; align-items: center; gap: 6px;
  padding: 5px 10px; background: var(--accent-soft);
  border-radius: 6px; font-size: 11px; color: var(--fg);
}
.att-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.att-remove { background: none; border: none; color: var(--muted); cursor: pointer; font-size: 14px; padding: 0 2px; }
.att-remove:hover { color: var(--danger); }
.slide-enter-active, .slide-leave-active { transition: transform 0.3s ease, opacity 0.3s ease; }
.slide-enter-from, .slide-leave-to { transform: translateX(100%); opacity: 0; }
</style>
