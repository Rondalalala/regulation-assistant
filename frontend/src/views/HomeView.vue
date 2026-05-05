<template>
  <div class="dark-home">
    <!-- 页面头 -->
    <div class="page-header">
      <div>
        <h1 class="ph-title">系统概览</h1>
        <p class="ph-sub">西北投资（园区运营公司）制度管理平台</p>
      </div>
      <span class="ph-date">{{ today }}</span>
    </div>

    <div style="padding: 0 24px 24px">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <router-link to="/regulations" class="stat-card stat-card-link sc-blue">
        <div class="stat-icon si-blue">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
          </svg>
        </div>
        <div>
          <div class="stat-label">制度总数</div>
          <div class="stat-value">{{ totalRegs }}</div>
          <div class="stat-delta" style="color:#60a5fa">查看制度库 →</div>
        </div>
      </router-link>

      <router-link to="/authority" class="stat-card stat-card-link sc-green">
        <div class="stat-icon si-green">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
        </div>
        <div>
          <div class="stat-label">权责事项</div>
          <div class="stat-value">{{ authTotal }}</div>
          <div class="stat-delta" style="color:#4ade80">查看清单 →</div>
        </div>
      </router-link>

      <div class="stat-card sc-sky">
        <div class="stat-icon si-sky">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
        </div>
        <div>
          <div class="stat-label">正式发布</div>
          <div class="stat-value">{{ activeRegs }}</div>
          <div class="stat-delta" style="color:#38bdf8">占比 {{ activePct }}%</div>
        </div>
      </div>

      <div class="stat-card sc-amber">
        <div class="stat-icon si-amber">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
        </div>
        <div>
          <div class="stat-label">试运行</div>
          <div class="stat-value">{{ pendingRegs }}</div>
          <div class="stat-delta" style="color:#fbbf24">待转正式</div>
        </div>
      </div>
    </div>

    <!-- 双看板 -->
    <div class="board-grid">
      <!-- 制度看板 -->
      <div class="board-card">
        <div class="board-header">
          <span class="board-title">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="rgba(199,217,240,0.65)" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
            制度库看板
          </span>
          <span class="board-meta">7 个职能域 · {{ totalRegs }} 条制度</span>
        </div>
        <div class="domain-list">
          <router-link
            v-for="domain in domainsWithRegCount" :key="domain.id"
            :to="`/regulations?domain=${domain.id}`"
            class="domain-row"
            :style="{ '--d-color': domain.color, '--d-bg': domain.bg, '--d-border': domain.border }"
          >
            <span class="dr-dot"></span>
            <span class="dr-label">{{ domain.label }}</span>
            <span class="dr-desc">{{ domain.desc }}</span>
            <span class="dr-count">{{ domain.regCount }}</span>
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="dr-arrow">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </router-link>
          <div v-if="!domainsWithRegCount.length" class="board-empty">加载中…</div>
        </div>
      </div>

      <!-- 权责看板 -->
      <div class="board-card">
        <div class="board-header">
          <span class="board-title">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="rgba(199,217,240,0.65)" stroke-width="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
            权责清单看板
          </span>
          <span class="board-meta">
            合计 {{ authTotal }} 条 · 项目公司 {{ authPcCount }} · 西北投资 {{ authNwCount }}
          </span>
        </div>
        <div class="domain-list">
          <router-link
            v-for="domain in domainsWithCount" :key="domain.id"
            :to="`/authority?domain=${domain.id}`"
            class="domain-row"
            :style="{ '--d-color': domain.color, '--d-bg': domain.bg, '--d-border': domain.border }"
          >
            <span class="dr-dot"></span>
            <span class="dr-label">{{ domain.label }}</span>
            <span class="dr-desc">{{ domain.desc }}</span>
            <span class="dr-count">{{ domain.count }}</span>
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="dr-arrow">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </router-link>
        </div>
      </div>
    </div>

    <!-- 组织架构通栏 -->
    <div class="org-section">
      <div class="board-title" style="margin-bottom:16px">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="rgba(199,217,240,0.65)" stroke-width="2">
          <rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/>
          <rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>
        </svg>
        西北投资（园区运营公司）组织架构
      </div>
      <div class="org-chart">
        <!-- 上级 -->
        <div class="oc-tier"><div class="oc-node oc-parent">中交投资有限公司</div></div>
        <div class="oc-v-line"></div>
        <!-- 本体 -->
        <div class="oc-tier"><div class="oc-node oc-root">西北投资（园区运营公司）</div></div>
        <div class="oc-v-line"></div>
        <!-- 职能部门 -->
        <div class="oc-dept-section">
          <div class="oc-section-label">职能部门</div>
          <div class="oc-dept-grid">
            <router-link
              v-for="d in orgDepts" :key="d.short"
              :to="`/authority?q=${encodeURIComponent(d.short)}`"
              class="oc-dept-node"
            >
              <div class="oc-dept-name">{{ d.short }}</div>
              <div v-if="d.sub" class="oc-dept-sub">{{ d.sub }}</div>
            </router-link>
          </div>
        </div>
        <div class="oc-v-line"></div>
        <!-- 下属单位 -->
        <div class="oc-proj-section">
          <div class="oc-section-label">下属单位（产业园区项目公司）</div>
          <div class="oc-park-cats">
            <router-link
              v-for="cat in parkCategories" :key="cat.brand"
              to="/authority?cat=pc"
              class="oc-park-cat"
            >
              <div class="oc-park-brand">{{ cat.brand }}</div>
              <div class="oc-park-type-lbl">{{ cat.type }}</div>
              <div class="oc-park-companies">
                <span v-for="co in cat.companies" :key="co" class="oc-co-chip">{{ co }}</span>
              </div>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getRegulations, getTree, getAuthority } from '../data/api.js'
import { DOMAINS, getDomainByKey, getDomainByModuleName } from '../utils/authorityCategories.js'

const regs = ref([])
const tree = ref({})
const authItems = ref([])

const today = computed(() => {
  const d = new Date()
  return `${d.getFullYear()} 年 ${d.getMonth() + 1} 月 ${d.getDate()} 日`
})

const orgDepts = [
  { short: '综合办公室', sub: '党委办公室 · 董事会办公室' },
  { short: '人力资源部', sub: '党委组织部' },
  { short: '财务资金部', sub: null },
  { short: '法律风控部', sub: '纪委 · 审计' },
  { short: '经营管理中心', sub: null },
  { short: 'QHSE部', sub: '安全监督 · 应急管理' },
  { short: '投资拓展部', sub: null },
  { short: '产业发展中心', sub: '投拓 · 项管 · 招商 · 运营' },
]

const parkCategories = [
  {
    brand: '中交科技城', type: '研发制造',
    companies: ['杭州智慧港', '济南科创', '济南投资', '怡和中源', '南京产投', '浙江智慧交通', '郑州数科', '中交高科', '西安数字交通'],
  },
  {
    brand: '中交物流港', type: '冷链物流',
    companies: ['岳阳物流'],
  },
  {
    brand: '中交智数谷', type: '数据算力',
    companies: ['中卫大数据'],
  },
]

onMounted(() => {
  regs.value = getRegulations()
  tree.value = getTree()
  authItems.value = getAuthority()
})

const totalRegs = computed(() => regs.value.length)
const activeRegs = computed(() => regs.value.filter(r => r.status === '施行').length)
const pendingRegs = computed(() => regs.value.filter(r => r.status && r.status !== '施行').length)
const activePct = computed(() => totalRegs.value ? Math.round(activeRegs.value / totalRegs.value * 100) : 0)

function hasProjectCo(item) {
  return item.flow?.some(s => s.org === '项目公司' && s.type !== 'report')
}
const realAuthItems = computed(() => authItems.value.filter(i => i.name && i.flow && i.flow.length > 0))
const authTotal = computed(() => realAuthItems.value.length)
const authPcCount = computed(() => realAuthItems.value.filter(i => hasProjectCo(i)).length)
const authNwCount = computed(() => realAuthItems.value.filter(i => !hasProjectCo(i)).length)

const domainsWithCount = computed(() => {
  const countMap = {}
  for (const item of realAuthItems.value) {
    const domain = getDomainByKey(item.key)
    if (domain) countMap[domain.id] = (countMap[domain.id] || 0) + 1
  }
  return DOMAINS.map(d => ({
    ...d,
    color: d.darkColor, bg: d.darkBg, border: d.darkBorder,
    count: countMap[d.id] || 0,
  }))
})

const domainsWithRegCount = computed(() => {
  const countMap = {}
  for (const [modName, items] of Object.entries(tree.value)) {
    const domain = getDomainByModuleName(modName)
    if (domain) {
      const count = Object.values(items).reduce((s, a) => s + a.length, 0)
      countMap[domain.id] = (countMap[domain.id] || 0) + count
    }
  }
  return DOMAINS.map(d => ({
    ...d,
    color: d.darkColor, bg: d.darkBg, border: d.darkBorder,
    regCount: countMap[d.id] || 0,
  })).filter(d => d.regCount > 0)
})

const topModules = computed(() => {
  return Object.entries(tree.value)
    .map(([name, items]) => ({
      name,
      count: Object.values(items).reduce((s, a) => s + a.length, 0),
    }))
    .sort((a, b) => b.count - a.count)
})

function moduleLink(modName) {
  const items = tree.value[modName]
  if (!items) return '/'
  for (const regs of Object.values(items)) {
    if (regs.length) return `/regulation/${regs[0].id}`
  }
  return '/'
}
</script>

<style scoped>
/* ── 深色主页 wrapper ── */
.dark-home {
  min-height: 100%;
  background: linear-gradient(160deg, #080f1d 0%, #0a1628 55%, #0d1a2e 100%);
  color: #e2eeff;
}

/* ── 页面头（磨砂玻璃 sticky） ── */
.page-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 18px 24px 14px;
  border-bottom: 1px solid rgba(199,217,240,0.1);
  margin-bottom: 20px;
  background: rgba(13, 21, 37, 0.88);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  position: sticky; top: 0; z-index: 5;
}
.ph-title { font-size: 17px; font-weight: 700; color: #e2eeff; line-height: 1.2; }
.ph-sub { font-size: 11.5px; color: #7faad4; margin-top: 2px; }
.ph-date { font-size: 12px; color: #4a6c8e; font-variant-numeric: tabular-nums; }

/* ── 统计卡片 ── */
.stats-grid {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 14px; margin-bottom: 16px;
}
.stat-card {
  background: rgba(255,255,255,0.055);
  border: 1px solid rgba(199,217,240,0.12);
  border-radius: 12px; padding: 18px 20px;
  display: flex; align-items: flex-start; gap: 14px;
  border-top-width: 3px;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
  position: relative; overflow: hidden;
}
.stat-card::before {
  content: ''; position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(135deg, rgba(255,255,255,0.03) 0%, transparent 60%);
}
.stat-card-link {
  text-decoration: none; color: inherit; cursor: pointer;
}
.stat-card-link:hover { transform: translateY(-3px); }
.sc-blue  { border-top-color: #60a5fa; }
.sc-blue.stat-card-link:hover  { box-shadow: 0 8px 32px rgba(96,165,250,0.3), 0 0 0 1px rgba(96,165,250,0.25); border-color: rgba(96,165,250,0.45); }
.sc-green { border-top-color: #34d399; }
.sc-green.stat-card-link:hover { box-shadow: 0 8px 32px rgba(52,211,153,0.3),  0 0 0 1px rgba(52,211,153,0.25);  border-color: rgba(52,211,153,0.45); }
.sc-sky   { border-top-color: #38bdf8; }
.sc-sky.stat-card-link:hover   { box-shadow: 0 8px 32px rgba(56,189,248,0.3),  0 0 0 1px rgba(56,189,248,0.25);  border-color: rgba(56,189,248,0.45); }
.sc-amber { border-top-color: #fbbf24; }
.sc-amber.stat-card-link:hover { box-shadow: 0 8px 32px rgba(251,191,36,0.28), 0 0 0 1px rgba(251,191,36,0.25); border-color: rgba(251,191,36,0.4); }

.stat-icon {
  width: 42px; height: 42px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.si-blue  { background: rgba(96,165,250,0.15);  box-shadow: 0 0 12px rgba(96,165,250,0.2); }
.si-green { background: rgba(52,211,153,0.15);  box-shadow: 0 0 12px rgba(52,211,153,0.2); }
.si-sky   { background: rgba(56,189,248,0.15);  box-shadow: 0 0 12px rgba(56,189,248,0.2); }
.si-amber { background: rgba(251,191,36,0.15);  box-shadow: 0 0 12px rgba(251,191,36,0.2); }
.stat-label { font-size: 11.5px; color: rgba(199,217,240,0.5); margin-bottom: 4px; }
.stat-value { font-size: 32px; font-weight: 800; color: #fff; line-height: 1; letter-spacing: -0.02em; }
.stat-delta { font-size: 11px; margin-top: 4px; }

/* ── 双看板 ── */
.board-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 14px;
}
.board-card {
  display: flex; flex-direction: column;
  background: rgba(255,255,255,0.045);
  border: 1px solid rgba(199,217,240,0.11);
  border-radius: 12px; padding: 18px 20px;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}
.board-card:hover { border-color: rgba(199,217,240,0.18); }
.board-header {
  display: flex; align-items: baseline; justify-content: space-between;
  margin-bottom: 12px; gap: 10px;
}
.board-title {
  font-size: 13.5px; font-weight: 600; color: #C7D9F0;
  display: flex; align-items: center; gap: 7px; flex-shrink: 0;
}
.board-meta { font-size: 11px; color: rgba(199,217,240,0.32); white-space: nowrap; }
.board-empty { text-align: center; color: rgba(199,217,240,0.3); font-size: 12px; padding: 20px 0; }

/* ── 职能域列表 ── */
.domain-list { display: flex; flex-direction: column; gap: 5px; }
.domain-row {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 12px;
  background: var(--d-bg, rgba(96,165,250,0.06));
  border: 1px solid var(--d-border, rgba(199,217,240,0.15));
  border-left: 3px solid var(--d-color, #60a5fa);
  border-radius: 8px;
  text-decoration: none; color: inherit;
  transition: transform 0.18s, border-color 0.18s;
  cursor: pointer; position: relative;
}
.domain-row::after {
  content: ''; position: absolute; inset: -1px; border-radius: 8px;
  border: 1px solid transparent;
  pointer-events: none;
  transition: border-color 0.18s, box-shadow 0.18s;
}
.domain-row:hover { transform: translateX(3px); }
.domain-row:hover::after {
  border-color: var(--d-color, #60a5fa);
  box-shadow: 0 0 14px -2px var(--d-color, rgba(96,165,250,0.4));
}
.dr-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--d-color, #60a5fa); flex-shrink: 0;
  box-shadow: 0 0 6px var(--d-color, #60a5fa);
}
.dr-label {
  font-size: 13px; font-weight: 600;
  color: var(--d-color, #60a5fa);
  width: 64px; flex-shrink: 0;
}
.dr-desc { font-size: 11px; color: rgba(199,217,240,0.45); flex: 1; }
.dr-count {
  font-size: 14px; font-weight: 700;
  color: var(--d-color, #60a5fa);
  flex-shrink: 0; min-width: 28px; text-align: right;
}
.dr-arrow { color: rgba(199,217,240,0.25); flex-shrink: 0; }

/* ── 组织架构通栏 ── */
.org-section {
  margin-top: 14px;
  background: rgba(255,255,255,0.045);
  border: 1px solid rgba(199,217,240,0.11);
  border-radius: 12px; padding: 18px 20px;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}
.org-chart { display: flex; flex-direction: column; align-items: center; }
.oc-tier { display: flex; justify-content: center; width: 100%; }
.oc-node {
  padding: 5px 20px; border-radius: 6px;
  font-size: 12px; font-weight: 500; text-align: center;
}
.oc-parent {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(199,217,240,0.12);
  color: #7faad4; font-size: 11px;
}
.oc-root {
  background: linear-gradient(135deg, #2563EB 0%, #1a3254 100%);
  border: 1px solid rgba(96,165,250,0.42);
  color: white; font-size: 13px; font-weight: 700; padding: 8px 30px;
  box-shadow: 0 0 22px rgba(37,99,235,0.42), 0 2px 8px rgba(0,0,0,0.32);
}
.oc-v-line { width: 1px; height: 14px; background: rgba(199,217,240,0.18); }

.oc-dept-section, .oc-proj-section {
  width: 100%;
  border: 1px dashed rgba(199,217,240,0.13);
  border-radius: 10px; padding: 10px 12px;
}
.oc-proj-section { border-color: rgba(96,165,250,0.24); margin-top: 0; }
.oc-section-label {
  font-size: 9.5px; font-weight: 600; color: #4a6c8e;
  letter-spacing: 0.06em; text-transform: uppercase;
  margin-bottom: 7px; text-align: center;
}
.oc-dept-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; }
.oc-dept-node {
  padding: 8px 10px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(199,217,240,0.1);
  border-radius: 7px; text-decoration: none; color: inherit;
  transition: border-color 0.15s, background 0.15s, box-shadow 0.15s;
  cursor: pointer;
}
.oc-dept-node:hover {
  border-color: rgba(96,165,250,0.34);
  background: rgba(37,99,235,0.1);
  box-shadow: 0 0 10px rgba(37,99,235,0.22);
}
.oc-dept-name { font-size: 11.5px; font-weight: 500; color: #C7D9F0; }
.oc-dept-sub { font-size: 9px; color: #4a6c8e; margin-top: 2px; line-height: 1.3; }

.oc-park-cats { display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 8px; }
.oc-park-cat {
  padding: 10px;
  background: rgba(37,99,235,0.08);
  border: 1px solid rgba(96,165,250,0.20);
  border-radius: 8px; text-decoration: none; color: inherit;
  transition: border-color 0.15s, background 0.15s, box-shadow 0.15s;
  cursor: pointer; display: block;
}
.oc-park-cat:hover {
  border-color: rgba(96,165,250,0.40);
  background: rgba(37,99,235,0.15);
  box-shadow: 0 0 16px rgba(37,99,235,0.22);
}
.oc-park-brand { font-size: 12px; font-weight: 700; color: #60a5fa; margin-bottom: 1px; }
.oc-park-type-lbl { font-size: 9px; color: #7faad4; margin-bottom: 6px; }
.oc-park-companies { display: flex; flex-wrap: wrap; gap: 4px; }
.oc-co-chip {
  font-size: 10px; color: #C7D9F0;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(199,217,240,0.1);
  border-radius: 4px; padding: 1px 6px; white-space: nowrap;
}
</style>
