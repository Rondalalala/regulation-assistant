<template>
  <div class="reg-page">
    <!-- 粘性面包屑头 -->
    <div v-if="reg" class="sticky-header">
      <nav class="breadcrumb">
        <router-link to="/home" class="bc-link">首页</router-link>
        <span class="bc-sep">›</span>
        <router-link to="/regulations" class="bc-link">制度库</router-link>
        <span class="bc-sep">›</span>
        <router-link
          :to="`/regulations?module=${encodeURIComponent(reg.module || '')}`"
          class="bc-link"
        >{{ reg.module || '制度库' }}</router-link>
        <span class="bc-sep">›</span>
        <span class="bc-current">{{ reg.name }}</span>
      </nav>
    </div>

    <div class="reg-body">
      <div v-if="loading" style="text-align:center;color:var(--muted);padding:80px 0;font-size:14px">加载中…</div>

      <template v-else-if="reg">
        <!-- 头部信息 -->
        <div class="reg-header">
          <div class="reg-header-top">
            <span class="reg-id">{{ reg.id }}</span>
            <div style="flex:1">
              <div class="reg-title">{{ reg.name }}</div>
              <div class="reg-sub" v-if="reg.dept">{{ reg.dept }} · {{ reg.issued_date }}</div>
            </div>
            <div style="display:flex;gap:8px;align-items:center">
              <span class="level-badge" :class="levelClass">{{ levelText }}</span>
              <span class="tag" :class="reg.status === '施行' ? 'tag-success' : 'tag-warn'">
                {{ reg.status || '施行' }}
              </span>
            </div>
          </div>

          <div class="meta-grid">
            <div class="meta-cell">
              <div class="meta-cell-lbl">职能模块</div>
              <div class="meta-cell-val">{{ reg.module || '—' }}</div>
            </div>
            <div class="meta-cell">
              <div class="meta-cell-lbl">主责部门</div>
              <div class="meta-cell-val">{{ reg.dept || '—' }}</div>
            </div>
            <div class="meta-cell">
              <div class="meta-cell-lbl">印发时间</div>
              <div class="meta-cell-val">{{ reg.issued_date || '—' }}</div>
            </div>
            <div class="meta-cell">
              <div class="meta-cell-lbl">制度类型</div>
              <div class="meta-cell-val">{{ reg.type || '—' }}</div>
            </div>
            <div class="meta-cell" style="border-right:none">
              <div class="meta-cell-lbl">文号</div>
              <div class="meta-cell-val">{{ reg.doc_no || '—' }}</div>
            </div>
          </div>

          <p v-if="reg.remark" style="margin-top:10px;font-size:12px;color:var(--warn)">备注：{{ reg.remark }}</p>
        </div>

        <!-- Tab 栏 -->
        <div class="tab-bar">
          <button v-for="tab in tabs" :key="tab.key"
            class="tab-btn" :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key">
            {{ tab.label }}
          </button>
        </div>

        <!-- 制度原文 -->
        <div v-if="activeTab === 'text'" class="tab-panel active">
          <div class="text-layout">
            <div class="reg-text">
              <template v-if="reg.blocks && reg.blocks.length">
                <template v-for="(block, i) in reg.blocks" :key="i">
                  <div v-if="block.type === 'table'" style="overflow-x:auto;margin:14px 0">
                    <table class="reg-table">
                      <tbody>
                        <tr v-for="(row, ri) in block.rows" :key="ri">
                          <td v-for="(cell, ci) in row" :key="ci"
                            :colspan="cell.colspan > 1 ? cell.colspan : undefined">
                            {{ cell.text }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <template v-else-if="block.type === 'para'">
                    <div v-if="isChapter(block.text)" :id="`toc-${i}`" class="reg-chapter">{{ block.text }}</div>
                    <div v-else-if="isSection(block.text)" :id="`toc-${i}`" class="reg-section">{{ block.text }}</div>
                    <div v-else-if="isAppendix(block.text)" :id="`toc-${i}`" class="reg-appendix">{{ block.text }}</div>
                    <div v-else-if="articleMatch(block.text)" class="reg-article">
                      <span class="art-num">{{ articleMatch(block.text)[1] }}</span>
                      <span>{{ articleMatch(block.text)[2] }}</span>
                    </div>
                    <p v-else-if="isItem1(block.text)" class="reg-item1">{{ block.text }}</p>
                    <p v-else-if="isItem2(block.text)" class="reg-item2">{{ block.text }}</p>
                    <p v-else-if="i < firstStructuralIdx && isDocNo(block.text)" class="reg-doc-no">{{ block.text }}</p>
                    <p v-else-if="i < firstStructuralIdx" class="reg-doc-title">{{ block.text }}</p>
                    <p v-else class="reg-para">{{ block.text }}</p>
                  </template>
                </template>
              </template>
              <div v-else style="text-align:center;color:var(--muted);padding:32px 0;font-size:13px">暂无原文数据</div>
            </div>

            <!-- 浮动目录 -->
            <nav v-if="tocItems.length" class="reg-toc">
              <div class="reg-toc-title">目录</div>
              <ul class="reg-toc-list">
                <li
                  v-for="item in tocItems" :key="item.id"
                  class="reg-toc-item"
                  :class="[`toc-${item.level}`, { active: activeSection === item.id }]"
                  @click="scrollToSection(item.id)"
                >{{ item.label }}</li>
              </ul>
            </nav>
          </div>
        </div>

        <!-- 流程图 -->
        <div v-if="activeTab === 'charts'" class="tab-panel active">
          <div class="flow-wrap">
            <div v-if="reg.charts && reg.charts.length" style="display:flex;flex-direction:column;gap:28px">
              <MermaidChart v-for="(chart, i) in reg.charts" :key="i"
                :title="chart.title" :code="chart.mermaid" />
            </div>
            <div v-else style="text-align:center;color:var(--muted);padding:32px 0;font-size:13px">该制度暂未生成流程图</div>
          </div>
        </div>

        <!-- 相关权责 -->
        <div v-if="activeTab === 'authority'" class="tab-panel active">
          <div class="auth-wrap">
            <template v-if="reg.authority_items && reg.authority_items.length">
              <div class="flow-legend">
                <span class="legend-item"><span class="legend-dot" style="background:var(--accent-soft);border:2px solid var(--blue);color:var(--blue)">①</span>审核步骤（顺序执行）</span>
                <span class="legend-item"><span class="legend-dot" style="background:var(--success-bg);border:2px solid var(--success);color:var(--success);text-decoration:underline;font-weight:800">②</span>最终审批</span>
                <span class="legend-item"><span class="legend-dot" style="background:#FFF7ED;border:2px solid rgba(251,146,60,0.4);color:#C2410C">○</span>会签（并行）</span>
                <span class="legend-item"><span class="legend-dot" style="background:var(--bg);border:2px solid var(--subtle);color:var(--muted)">△</span>报备</span>
              </div>
              <div v-for="item in reg.authority_items" :key="item.key" class="auth-card" style="margin-bottom:10px">
                <div class="auth-card-header">
                  <span class="key-badge">{{ item.key }}</span>
                  <span v-if="item.is_authorized" class="tag tag-warn" style="font-size:10px">授权</span>
                  <span class="auth-card-title">{{ item.name }}</span>
                  <span v-if="item.system" class="tag tag-navy auth-card-src">{{ item.system }}</span>
                </div>
                <div v-if="item.initiator" class="initiator-bar">
                  <span class="initiator-icon">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>
                  </span>
                  <span class="initiator-label">发起部门</span>
                  <span class="initiator-value">{{ item.initiator }}</span>
                </div>
                <FlowSteps :flow="item.flow || []" />
                <p v-if="item.remark && item.remark !== 'nan'"
                  style="margin-top:8px;padding-top:8px;border-top:1px solid var(--blue-border);font-size:11px;color:var(--warn)">{{ item.remark }}</p>
              </div>
            </template>
            <div v-else style="text-align:center;color:var(--muted);padding:32px 0;font-size:13px">未匹配到相关权责事项</div>
          </div>
        </div>
      </template>

      <div v-else style="text-align:center;color:var(--muted);padding:80px 0;font-size:14px">制度不存在</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useRoute, onBeforeRouteUpdate } from 'vue-router'
import { getRegulation } from '../data/api.js'
import MermaidChart from '../components/MermaidChart.vue'
import FlowSteps from '../components/FlowSteps.vue'

const route = useRoute()
const reg = ref(null)
const loading = ref(false)
const activeTab = ref('text')
const activeSection = ref('')
const tabs = [
  { key: 'text', label: '制度原文' },
  { key: 'charts', label: '流程图表' },
  { key: 'authority', label: '相关权责' },
]

function load(id) {
  loading.value = true
  reg.value = null
  try {
    reg.value = getRegulation(id)
    activeTab.value = 'text'
  } finally {
    loading.value = false
  }
}

const levelClass = computed(() => {
  if (!reg.value) return ''
  const map = { 'A级': 'level-a', 'B级': 'level-b', 'C级': 'level-c' }
  return map[reg.value.level] || 'level-c'
})
const levelText = computed(() => reg.value?.level?.replace('级', '') || 'C')

const CHAPTER  = /^第[一二三四五六七八九十百千\d]+章/
const SECTION  = /^第[一二三四五六七八九十百千\d]+节/
const ARTICLE  = /^(第[一二三四五六七八九十百千\d]+条)\s*([\s\S]*)/
const ITEM1    = /^[一二三四五六七八九十]+[、.]/
const ITEM2    = /^（[一二三四五六七八九十]+）/
const APPENDIX = /^附件[\s\d一二三四五六七八九十：:（]/
const DOC_NO   = /^（.*号）$/

function isChapter(t)  { return CHAPTER.test(t) }
function isSection(t)  { return SECTION.test(t) }
function articleMatch(t) { return t.match(ARTICLE) }
function isItem1(t)    { return ITEM1.test(t) }
function isItem2(t)    { return ITEM2.test(t) }
function isAppendix(t) { return APPENDIX.test(t) }
function isDocNo(t)    { return DOC_NO.test(t) }

// ── 目录 ──────────────────────────────────────────────────────────────────────
const tocItems = computed(() => {
  if (!reg.value?.blocks) return []
  return reg.value.blocks
    .map((b, i) => ({ ...b, _idx: i }))
    .filter(b => b.type === 'para' && (isChapter(b.text) || isSection(b.text) || isAppendix(b.text)))
    .map(b => {
      const level = isChapter(b.text) ? 'chapter' : isSection(b.text) ? 'section' : 'appendix'
      const label = level === 'appendix' && b.text.length > 14 ? b.text.slice(0, 14) + '…' : b.text
      return { text: b.text, label, level, id: `toc-${b._idx}` }
    })
})

const firstStructuralIdx = computed(() => {
  if (!reg.value?.blocks) return 0
  const idx = reg.value.blocks.findIndex(b =>
    b.type === 'para' && (isChapter(b.text) || isSection(b.text) || isAppendix(b.text) || !!articleMatch(b.text))
  )
  return idx === -1 ? 0 : idx
})

function scrollToSection(id) {
  const el = document.getElementById(id)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    activeSection.value = id
  }
}

let observer = null

function setupObserver() {
  if (observer) { observer.disconnect(); observer = null }
  if (!tocItems.value.length) return
  observer = new IntersectionObserver(
    (entries) => {
      const visible = entries.filter(e => e.isIntersecting)
      if (visible.length) activeSection.value = visible[0].target.id
    },
    { rootMargin: '-10% 0px -75% 0px' }
  )
  nextTick(() => {
    tocItems.value.forEach(item => {
      const el = document.getElementById(item.id)
      if (el) observer.observe(el)
    })
  })
}

watch([reg, activeTab], ([newReg, tab]) => {
  if (tab === 'text' && newReg) nextTick(setupObserver)
  else if (observer) { observer.disconnect(); observer = null }
})

function loadFromRoute() {
  const id = route.params.id
  if (id) load(Array.isArray(id) ? id.join('/') : id)
}

watch(() => route.params.id, id => {
  if (id) load(Array.isArray(id) ? id.join('/') : id)
}, { immediate: true })

onMounted(loadFromRoute)

onBeforeRouteUpdate((to) => {
  const id = to.params.id
  if (id) load(Array.isArray(id) ? id.join('/') : id)
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})
</script>

<style scoped>
.reg-page { min-height: 100%; }
.reg-body { padding: 0 24px 24px; }

.breadcrumb {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; color: var(--muted);
}
.bc-link { color: var(--muted); text-decoration: none; transition: color 0.13s; }
.bc-link:hover { color: var(--blue); }
.bc-sep { color: var(--subtle); font-size: 11px; }
.bc-current {
  color: var(--fg); font-weight: 500;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 380px;
}

.reg-header {
  background: var(--surface);
  border: 1px solid var(--blue-border); border-radius: 12px;
  padding: 18px 22px; margin-bottom: 0;
  border-top: 3px solid var(--blue);
  box-shadow: var(--blue-glow);
}

.reg-header-top {
  display: flex; align-items: flex-start; gap: 12px; margin-bottom: 14px;
}

.reg-id {
  font-family: var(--mono); font-size: 11px;
  background: var(--blue); color: white;
  padding: 3px 9px; border-radius: 4px;
  flex-shrink: 0; margin-top: 3px;
}

.reg-title { font-size: 17px; font-weight: 700; color: var(--fg); line-height: 1.3; }
.reg-sub   { font-size: 12.5px; color: var(--muted); margin-top: 3px; }

.level-badge {
  display: inline-flex; align-items: center; justify-content: center;
  width: 26px; height: 26px; border-radius: 50%;
  font-size: 13px; font-weight: 700; flex-shrink: 0;
}
.level-a { background: #FEF2F2; color: var(--danger); box-shadow: 0 0 8px rgba(220,38,38,0.15); }
.level-b { background: var(--warn-bg); color: var(--warn); box-shadow: 0 0 8px rgba(217,119,6,0.15); }
.level-c { background: var(--accent-soft); color: var(--blue); box-shadow: 0 0 8px rgba(37,99,235,0.15); }

.meta-grid {
  display: grid; grid-template-columns: repeat(5, 1fr);
  border: 1px solid var(--blue-border); border-radius: 8px; overflow: hidden;
}
.meta-cell {
  padding: 9px 14px;
  border-right: 1px solid var(--blue-border);
  transition: background 0.13s;
}
.meta-cell:hover { background: var(--blue-soft); }
.meta-cell-lbl { font-size: 11px; color: var(--muted); margin-bottom: 3px; }
.meta-cell-val { font-size: 12.5px; font-weight: 500; }

.tab-bar {
  display: flex;
  background: rgba(37,99,235,0.04);
  border: 1px solid rgba(37,99,235,0.1);
  border-bottom: none;
  border-radius: 8px 8px 0 0;
  padding: 0 20px;
  margin-top: 14px;
}

.tab-btn {
  padding: 11px 18px;
  font-size: 13px; font-family: var(--font); font-weight: 500;
  color: var(--muted); background: transparent; border: none;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: all 0.13s;
}
.tab-btn:hover { color: var(--fg); }
.tab-btn.active {
  color: var(--blue);
  border-bottom-color: var(--blue);
  background: rgba(37,99,235,0.06);
}

.tab-panel {
  display: block;
  animation: tabFadeIn 0.18s ease;
}

@keyframes tabFadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── 原文双栏布局 ── */
.text-layout {
  display: flex;
  align-items: flex-start;
  gap: 0;
}

.reg-text {
  flex: 1;
  min-width: 0;
  background: var(--surface);
  border: 1px solid var(--blue-border);
  border-top: none; border-radius: 0 0 8px 8px;
  padding: 26px 36px;
  font-size: 14px; line-height: 2; color: var(--fg);
  box-shadow: var(--blue-glow);
}

.text-layout .reg-text:has(+ .reg-toc) {
  border-radius: 0 0 0 8px;
  border-right: none;
}

/* ── 目录面板 ── */
.reg-toc {
  width: 196px;
  flex-shrink: 0;
  position: sticky;
  top: 48px;
  align-self: flex-start;
  background: var(--surface);
  border: 1px solid var(--blue-border);
  border-top: none;
  border-radius: 0 0 8px 0;
  padding: 16px 12px 20px;
  max-height: calc(100vh - 200px);
  overflow-y: auto;
  box-shadow: var(--blue-glow);
}

.reg-toc-title {
  font-size: 10.5px;
  font-weight: 700;
  color: var(--muted);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--blue-border);
}

.reg-toc-list {
  list-style: none;
  margin: 0; padding: 0;
  display: flex; flex-direction: column; gap: 1px;
}

.reg-toc-item {
  font-size: 11.5px;
  color: var(--muted);
  cursor: pointer;
  padding: 5px 8px;
  border-radius: 5px;
  line-height: 1.45;
  transition: background 0.13s, color 0.13s;
  user-select: none;
}

.reg-toc-item:hover {
  color: var(--blue);
  background: var(--accent-soft);
}

.reg-toc-item.active {
  color: var(--blue);
  font-weight: 600;
  background: var(--accent-soft);
}

.toc-chapter {
  color: var(--fg);
  font-weight: 500;
}

.toc-section {
  padding-left: 18px;
  font-size: 11px;
}

.reg-chapter {
  font-size: 14.5px; font-weight: 700; text-align: center;
  margin: 24px 0 14px; color: var(--fg);
}
.reg-section {
  font-size: 13px; font-weight: 600; text-align: center;
  margin: 16px 0 10px; color: var(--fg);
}
.reg-appendix {
  font-size: 14px; font-weight: 700; color: var(--blue);
  margin: 28px 0 10px;
  padding: 8px 14px;
  background: var(--accent-soft);
  border-left: 3px solid var(--blue);
  border-radius: 0 4px 4px 0;
}
.toc-appendix { color: var(--fg); font-weight: 600; }
.reg-doc-title {
  text-align: center; font-size: 19px; font-weight: 700;
  color: var(--fg); margin: 4px 0; line-height: 1.6; letter-spacing: 0.01em;
}
.reg-doc-no {
  text-align: center; font-size: 13px; color: var(--muted);
  margin: 2px 0 20px;
}
.reg-article { display: flex; gap: 8px; margin: 8px 0; }
.art-num { font-weight: 600; color: var(--blue); flex-shrink: 0; min-width: 46px; }
.reg-item1 { padding-left: 28px; font-weight: 500; margin: 4px 0; }
.reg-item2 { padding-left: 56px; margin: 2px 0; }
.reg-para  { text-align: justify; margin: 6px 0; }

.reg-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.reg-table td { padding: 8px 13px; border: 1px solid var(--blue-border); vertical-align: top; white-space: pre-wrap; }
.reg-table tr:first-child td { background: var(--accent-soft); font-weight: 600; color: var(--blue); }

.flow-wrap {
  background: var(--surface);
  border: 1px solid var(--blue-border);
  border-top: none; border-radius: 0 0 8px 8px;
  padding: 28px 32px;
  box-shadow: var(--blue-glow);
}

.auth-wrap {
  background: var(--surface);
  border: 1px solid var(--blue-border);
  border-top: none; border-radius: 0 0 8px 8px;
  padding: 18px 22px;
  box-shadow: var(--blue-glow);
}

.auth-card {
  background: var(--surface);
  border: 1px solid var(--blue-border); border-radius: 12px;
  padding: 14px 18px;
  transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
}
.auth-card:hover {
  border-color: rgba(37,99,235,0.3);
  box-shadow: 0 8px 24px rgba(37,99,235,0.12);
  transform: translateY(-2px);
}
.auth-card-header {
  display: flex; align-items: center; gap: 8px; margin-bottom: 8px; flex-wrap: wrap;
}
.key-badge {
  font-family: var(--mono); font-size: 10px;
  background: var(--blue); color: white;
  padding: 2px 6px; border-radius: 4px; flex-shrink: 0;
}
.auth-card-title { font-size: 13px; font-weight: 600; flex: 1; min-width: 0; }
.auth-card-src {
  font-size: 10px; margin-left: auto; white-space: nowrap;
  overflow: hidden; text-overflow: ellipsis; max-width: 160px;
}

.initiator-bar {
  display: flex; align-items: center; gap: 6px;
  background: var(--accent-soft);
  border-left: 3px solid var(--blue);
  border-radius: 0 4px 4px 0;
  padding: 5px 10px;
  margin-bottom: 10px;
}
.initiator-icon { color: var(--blue); display: flex; align-items: center; flex-shrink: 0; }
.initiator-label {
  font-size: 11px; font-weight: 600; color: var(--blue);
  white-space: nowrap; flex-shrink: 0;
}
.initiator-value { font-size: 12px; color: var(--fg); }

.flow-legend {
  display: flex; gap: 16px; flex-wrap: wrap;
  margin-bottom: 14px; font-size: 11px; color: var(--muted);
  align-items: center;
}
.legend-item { display: flex; align-items: center; gap: 5px; }
.legend-dot {
  display: inline-flex; align-items: center; justify-content: center;
  width: 20px; height: 20px; border-radius: 50%;
  font-size: 10px; font-weight: 700; flex-shrink: 0;
}
</style>
