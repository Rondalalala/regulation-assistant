<template>
  <div>
    <!-- 页面头 -->
    <div class="page-header">
      <div>
        <h1 class="ph-title">权责清单</h1>
        <p class="ph-sub">共 {{ realItems.length }} 条权责事项</p>
      </div>
    </div>

    <div style="padding: 0 24px 24px">

    <!-- 职能域筛选 -->
    <div class="domain-filter">
      <button
        class="domain-chip" :class="{ active: filterDomain === '' }"
        @click="filterDomain = ''"
      >全部职能域</button>
      <button
        v-for="d in DOMAINS" :key="d.id"
        class="domain-chip"
        :class="{ active: filterDomain === d.id }"
        :style="filterDomain === d.id ? { background: d.color, borderColor: d.color, color: 'white' } : { borderColor: d.border, color: d.color, background: d.bg }"
        @click="filterDomain = filterDomain === d.id ? '' : d.id"
      >{{ d.label }}</button>
    </div>

    <!-- 大类分组 Tab -->
    <div class="cat-tabs">
      <button
        v-for="cat in categories" :key="cat.value"
        class="cat-tab" :class="{ active: filterCat === cat.value }"
        @click="filterCat = cat.value"
      >
        {{ cat.label }}
        <span class="cat-count">{{ cat.count }}</span>
      </button>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <!-- 综合搜索框 -->
      <div class="filter-search">
        <input
          v-model="q"
          type="text"
          placeholder="搜索事项名称、发起部门、涉及部门…"
          @keydown.esc="q = ''"
        />
        <button v-if="q" class="search-clear-btn" @click="q = ''">×</button>
      </div>

      <!-- 审批层级快筛 -->
      <div class="chips-group">
        <span class="chips-label">审批层级</span>
        <button
          v-for="chip in approvalChips" :key="chip.value"
          class="filter-chip" :class="{ active: filterApproval === chip.value }"
          @click="filterApproval = filterApproval === chip.value ? '' : chip.value"
        >{{ chip.label }}</button>
      </div>
    </div>

    <!-- 结果数 -->
    <p v-if="q || filterApproval" style="font-size:11.5px;color:var(--muted);margin-bottom:10px">
      筛选结果：{{ filtered.length }} 条
      <span v-if="q" style="margin-left:6px;color:var(--navy)">「{{ q }}」</span>
    </p>

    <!-- 卡片列表 -->
    <div class="auth-cards">
      <div v-for="item in filtered" :key="item.key" :id="`auth-${item.key}`" class="auth-card" :class="{ 'auth-highlight': highlight === item.key }">
        <div class="auth-card-header">
          <span class="key-badge">{{ item.key }}</span>
          <span v-if="item.is_authorized" class="tag tag-warn" style="font-size:10px;flex-shrink:0">授权事项</span>
          <!-- 事项名称，有搜索词则高亮 -->
          <span class="auth-card-title" v-html="hl(item.name)"></span>
          <span v-if="item.system"
            class="tag tag-navy auth-card-src" :title="item.system">{{ item.system }}</span>
          <span v-else style="font-size:11px;color:var(--subtle);margin-left:auto;flex-shrink:0">线下流程</span>
        </div>

        <!-- 发起部门 -->
        <div v-if="item.initiator" class="initiator-bar">
          <span class="initiator-icon">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/>
            </svg>
          </span>
          <span class="initiator-label">发起部门</span>
          <span class="initiator-value" v-html="hl(item.initiator)"></span>
          <span v-if="item.frequency" style="margin-left:auto;font-size:10px;color:var(--muted);flex-shrink:0">{{ item.frequency }}</span>
        </div>

        <!-- 审批流程 -->
        <FlowSteps :flow="item.flow || []" :highlight-query="q" />

        <!-- 备注 -->
        <p v-if="item.remark && item.remark !== 'nan'"
          style="margin-top:10px;padding-top:8px;border-top:1px solid var(--border);font-size:11px;color:var(--warn)">
          {{ item.remark }}
        </p>
      </div>
    </div>

    <p v-if="!filtered.length" style="text-align:center;color:var(--muted);font-size:13px;padding:48px 0">无匹配结果</p>
  </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { getAuthority } from '../data/api.js'
import FlowSteps from '../components/FlowSteps.vue'
import { DOMAINS, getDomainByKey } from '../utils/authorityCategories.js'

const route = useRoute()
const items = ref([])
const q = ref('')
const filterCat = ref('')
const filterApproval = ref('')
const filterDomain = ref('')
const highlight = ref('')

const approvalChips = [
  { label: '项目公司审批', value: '项目公司' },
  { label: '西北投资审批', value: '西北投资' },
  { label: '决策机构审批', value: '决策' },
  { label: '总部及以上', value: '总部' },
]

onMounted(() => {
  if (route.query.q)      q.value          = String(route.query.q)
  if (route.query.cat)    filterCat.value  = String(route.query.cat)
  if (route.query.domain) filterDomain.value = String(route.query.domain)
  items.value = getAuthority()

  if (route.query.id) {
    highlight.value = String(route.query.id)
    nextTick(() => {
      setTimeout(() => {
        const el = document.getElementById(`auth-${route.query.id}`)
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }, 300)
    })
  }
})

const realItems = computed(() => items.value.filter(i => i.name && i.flow && i.flow.length > 0))

// 判断是否有项目公司参与（非报备步骤）
function hasProjectCo(item) {
  return item.flow?.some(s => s.org === '项目公司' && s.type !== 'report')
}

// 最终审批步骤的 org
function finalOrg(item) {
  return item.flow?.find(s => s.is_final)?.org || ''
}

// 大类分组
const categories = computed(() => {
  const all = realItems.value
  const pc = all.filter(i => hasProjectCo(i))
  const nw = all.filter(i => !hasProjectCo(i))
  return [
    { label: '全部', value: '', count: all.length },
    { label: '项目公司事项', value: 'pc', count: pc.length },
    { label: '西北投资事项', value: 'nw', count: nw.length },
  ]
})

// 搜索：名称、编号、发起部门、系统，以及流程中所有角色名
function matchSearch(item, kw) {
  if ((item.name || '').toLowerCase().includes(kw)) return true
  if ((item.key || '').toLowerCase().includes(kw)) return true
  if ((item.initiator || '').toLowerCase().includes(kw)) return true
  if ((item.system || '').toLowerCase().includes(kw)) return true
  if (item.flow?.some(s => (s.role || '').toLowerCase().includes(kw))) return true
  return false
}

const filtered = computed(() => {
  let list = realItems.value

  // 职能域筛选
  if (filterDomain.value) {
    list = list.filter(i => getDomainByKey(i.key)?.id === filterDomain.value)
  }

  // 大类筛选
  if (filterCat.value === 'pc') list = list.filter(i => hasProjectCo(i))
  else if (filterCat.value === 'nw') list = list.filter(i => !hasProjectCo(i))

  // 文字搜索
  if (q.value.trim()) {
    const kw = q.value.toLowerCase()
    list = list.filter(i => matchSearch(i, kw))
  }

  // 审批层级
  if (filterApproval.value === '项目公司') {
    list = list.filter(i => finalOrg(i) === '项目公司')
  } else if (filterApproval.value === '西北投资') {
    list = list.filter(i => finalOrg(i).includes('西北投资'))
  } else if (filterApproval.value === '决策') {
    list = list.filter(i => finalOrg(i).includes('决策'))
  } else if (filterApproval.value === '总部') {
    list = list.filter(i => ['中交投资总部', '中国交建'].includes(finalOrg(i)))
  }

  return list
})

// 高亮搜索词
function hl(text) {
  if (!q.value.trim() || !text) return text || ''
  const kw = q.value.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return text.replace(new RegExp(`(${kw})`, 'gi'), '<mark>$1</mark>')
}
</script>

<style scoped>
/* ── 页面头 ── */
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

/* ── 职能域筛选 ── */
.domain-filter {
  display: flex; flex-wrap: wrap; gap: 6px;
  margin-bottom: 12px;
}
.domain-chip {
  padding: 4px 12px;
  border: 1.5px solid var(--border); border-radius: 100px;
  font-size: 12px; font-family: var(--font);
  cursor: pointer; background: var(--surface); color: var(--muted);
  transition: all 0.13s;
}
.domain-chip:hover:not(.active) { border-color: var(--navy); color: var(--navy); }
.domain-chip.active { background: var(--navy); color: white; border-color: var(--navy); }

/* ── 大类 Tab ── */
.cat-tabs {
  display: flex; gap: 4px;
  margin-bottom: 12px;
}
.cat-tab {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 14px;
  border: 1px solid var(--border); border-radius: 6px;
  font-size: 12.5px; font-family: var(--font);
  cursor: pointer; background: var(--surface); color: var(--muted);
  transition: all 0.15s;
}
.cat-tab:hover:not(.active) { border-color: var(--navy); color: var(--navy); }
.cat-tab.active {
  background: var(--navy); color: white; border-color: var(--navy);
  font-weight: 500;
}
.cat-count {
  font-size: 10.5px;
  background: rgba(255,255,255,0.18);
  border-radius: 10px;
  padding: 1px 6px;
  font-weight: 400;
}
.cat-tab:not(.active) .cat-count {
  background: var(--bg);
  color: var(--subtle);
}

/* ── 筛选栏 ── */
.filter-bar {
  background: var(--surface);
  border: 1px solid var(--border); border-radius: 8px;
  padding: 12px 15px; margin-bottom: 12px;
  display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
}

.filter-search {
  flex: 1; min-width: 220px;
  position: relative;
}
.filter-search input {
  width: 100%;
  border: 1px solid var(--border); border-radius: 6px;
  padding: 7px 28px 7px 30px;
  font-size: 13px; font-family: var(--font); outline: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='13' height='13' viewBox='0 0 24 24' fill='none' stroke='%2394A3B8' stroke-width='2'%3E%3Ccircle cx='11' cy='11' r='8'/%3E%3Cpath d='m21 21-4.35-4.35'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: 9px center;
  background-size: 13px;
  color: var(--fg);
  transition: border-color 0.13s;
}
.filter-search input:focus { border-color: var(--navy); }

.search-clear-btn {
  position: absolute;
  right: 7px; top: 50%; transform: translateY(-50%);
  background: none; border: none;
  color: var(--subtle); font-size: 15px; cursor: pointer;
  line-height: 1; padding: 0 3px;
  transition: color 0.13s;
}
.search-clear-btn:hover { color: var(--fg); }

.chips-group {
  display: flex; align-items: center; gap: 6px; flex-wrap: wrap;
}
.chips-label {
  font-size: 11px; color: var(--subtle); white-space: nowrap;
}
.filter-chip {
  padding: 4px 11px;
  border: 1px solid var(--border); border-radius: 100px;
  font-size: 12px; font-family: var(--font);
  cursor: pointer; background: transparent; color: var(--muted);
  transition: all 0.13s;
}
.filter-chip.active { background: var(--navy); color: white; border-color: var(--navy); }
.filter-chip:hover:not(.active) { border-color: var(--navy); color: var(--navy); }

/* ── 卡片 ── */
.auth-cards { display: flex; flex-direction: column; gap: 11px; }

.auth-card {
  background: var(--surface);
  border: 1px solid var(--border); border-radius: 10px;
  padding: 14px 18px;
  transition: border-color 0.18s, box-shadow 0.18s, transform 0.15s;
}
.auth-card:hover {
  border-color: #C7D9F0;
  box-shadow: 0 4px 12px rgba(30,58,95,0.09);
  transform: translateY(-1px);
}
.auth-highlight {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 2px rgba(37,99,235,0.15), 0 4px 12px rgba(30,58,95,0.12) !important;
}
.auth-card-header {
  display: flex; align-items: center; gap: 8px; margin-bottom: 8px; flex-wrap: wrap;
}
.key-badge {
  font-family: var(--mono); font-size: 10px;
  background: var(--navy); color: white;
  padding: 2px 7px; border-radius: 4px; flex-shrink: 0;
}
.auth-card-title { font-size: 13px; font-weight: 600; flex: 1; min-width: 0; }
.auth-card-src {
  font-size: 10px; white-space: nowrap; overflow: hidden;
  text-overflow: ellipsis; max-width: 180px; margin-left: auto; flex-shrink: 0;
}

.initiator-bar {
  display: flex; align-items: center; gap: 6px;
  background: var(--accent-soft);
  border-left: 3px solid var(--navy);
  border-radius: 0 4px 4px 0;
  padding: 5px 10px;
  margin-bottom: 10px;
}
.initiator-icon { color: var(--navy); display: flex; align-items: center; flex-shrink: 0; }
.initiator-label {
  font-size: 11px; font-weight: 600; color: var(--navy);
  white-space: nowrap; flex-shrink: 0;
}
.initiator-value { font-size: 12px; color: var(--fg); flex: 1; }

/* ── 搜索高亮 ── */
:deep(mark) {
  background: #FEF08A;
  color: #713F12;
  border-radius: 2px;
  padding: 0 1px;
  font-style: normal;
}
</style>
