<template>
  <div class="reg-list-page">
    <!-- 面包屑 -->
    <nav class="breadcrumb">
      <router-link to="/home" class="bc-link">首页</router-link>
      <span class="bc-sep">›</span>
      <router-link v-if="domainId || moduleName" to="/regulations" class="bc-link">制度库</router-link>
      <span v-else class="bc-current">制度库</span>

      <template v-if="domainId && currentDomain">
        <span class="bc-sep">›</span>
        <router-link v-if="moduleName" :to="`/regulations?domain=${domainId}`" class="bc-link">
          {{ currentDomain.label }}
        </router-link>
        <span v-else class="bc-current">{{ currentDomain.label }}</span>
      </template>

      <template v-if="moduleName">
        <span class="bc-sep">›</span>
        <span class="bc-current">{{ moduleName }}</span>
      </template>
    </nav>

    <!-- ── 模式3：制度详情列表（module 已选）── -->
    <template v-if="moduleName && moduleItems">
      <div class="page-header">
        <div>
          <h2 class="page-title">{{ moduleName }}</h2>
          <p class="page-sub">共 {{ moduleRegCount }} 条制度</p>
        </div>
      </div>

      <div class="subcat-list">
        <div v-for="(regs, subcat) in moduleItems" :key="subcat" class="subcat-section">
          <div class="subcat-label">{{ subcat }}</div>
          <div class="reg-list">
            <router-link
              v-for="reg in regs" :key="reg.id"
              :to="`/regulation/${reg.id}`"
              class="reg-item"
            >
              <span class="reg-item-id">{{ reg.id }}</span>
              <div class="reg-item-body">
                <span class="reg-item-name">{{ reg.name }}</span>
                <span v-if="reg.dept" class="reg-item-dept">{{ reg.dept }}</span>
              </div>
              <span
                class="tag"
                :class="reg.status === '施行' ? 'tag-success' : 'tag-warn'"
                style="font-size:10.5px;flex-shrink:0"
              >{{ reg.status || '施行' }}</span>
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="reg-arrow">
                <path d="M9 18l6-6-6-6"/>
              </svg>
            </router-link>
          </div>
        </div>
      </div>
    </template>

    <!-- ── 模式2：大类模块列表（domain 已选）── -->
    <template v-else-if="domainId && currentDomain">
      <div class="page-header">
        <div>
          <h2 class="page-title" :style="{ color: currentDomain.color }">{{ currentDomain.label }}</h2>
          <p class="page-sub">{{ currentDomain.desc }} · {{ domainModules.length }} 个大类 · {{ domainTotalCount }} 条制度</p>
        </div>
      </div>

      <div class="module-grid">
        <router-link
          v-for="mod in domainModules" :key="mod.name"
          :to="`/regulations?domain=${domainId}&module=${encodeURIComponent(mod.name)}`"
          class="module-card"
          :style="{ '--d-color': currentDomain.color, '--d-bg': currentDomain.bg, '--d-border': currentDomain.border }"
        >
          <div class="mc-header">
            <div class="mc-dot"></div>
            <div class="mc-name">{{ mod.name }}</div>
          </div>
          <div class="mc-meta">{{ mod.subcats }} 个子类</div>
          <div class="mc-count">
            <span class="mc-num">{{ mod.count }}</span>
            <span class="mc-unit">条</span>
          </div>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="mc-arrow">
            <path d="M9 18l6-6-6-6"/>
          </svg>
        </router-link>
      </div>
    </template>

    <!-- ── 模式1：职能域总览 ── -->
    <template v-else>
      <div class="page-header">
        <div>
          <h2 class="page-title">制度库</h2>
          <p class="page-sub">共 {{ totalCount }} 条制度 · 7 个职能域</p>
        </div>
      </div>

      <div class="domain-overview">
        <router-link
          v-for="domain in domainsWithCount" :key="domain.id"
          :to="`/regulations?domain=${domain.id}`"
          class="domain-card"
          :style="{ '--d-color': domain.color, '--d-bg': domain.bg, '--d-border': domain.border }"
        >
          <div class="dc-top">
            <span class="dc-dot"></span>
            <span class="dc-label">{{ domain.label }}</span>
            <span class="dc-count">{{ domain.count }}</span>
          </div>
          <div class="dc-desc">{{ domain.desc }}</div>
          <div class="dc-modules">{{ domain.moduleCount }} 个大类</div>
        </router-link>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getTree, getRegulations } from '../data/api.js'
import { DOMAINS, getDomainByModuleName, MODULE_NAME_TO_CAT } from '../utils/authorityCategories.js'

const route = useRoute()
const tree = ref({})
const allRegs = ref([])

onMounted(() => {
  tree.value = getTree()
  allRegs.value = getRegulations()
})

const domainId = computed(() => route.query.domain ? String(route.query.domain) : '')
const moduleName = computed(() => route.query.module ? decodeURIComponent(String(route.query.module)) : '')

const currentDomain = computed(() => DOMAINS.find(d => d.id === domainId.value) || null)

// 模式3: 当前模块的制度（sub-cat → [regs]）
const moduleItems = computed(() => {
  if (!moduleName.value) return null
  return tree.value[moduleName.value] || null
})

const moduleRegCount = computed(() => {
  if (!moduleItems.value) return 0
  return Object.values(moduleItems.value).reduce((s, a) => s + a.length, 0)
})

// 模式2: 选定域内的所有大类模块
const domainModules = computed(() => {
  if (!domainId.value) return []
  return Object.entries(tree.value)
    .filter(([name]) => getDomainByModuleName(name)?.id === domainId.value)
    .map(([name, items]) => ({
      name,
      subcats: Object.keys(items).length,
      count: Object.values(items).reduce((s, a) => s + a.length, 0),
    }))
    .sort((a, b) => {
      const ca = MODULE_NAME_TO_CAT[a.name] || ''
      const cb = MODULE_NAME_TO_CAT[b.name] || ''
      return ca < cb ? -1 : ca > cb ? 1 : 0
    })
})

const domainTotalCount = computed(() => domainModules.value.reduce((s, m) => s + m.count, 0))

// 模式1: 全部职能域
const domainsWithCount = computed(() => {
  const countMap = {}
  const moduleCountMap = {}
  for (const [modName, items] of Object.entries(tree.value)) {
    const domain = getDomainByModuleName(modName)
    if (domain) {
      const count = Object.values(items).reduce((s, a) => s + a.length, 0)
      countMap[domain.id] = (countMap[domain.id] || 0) + count
      moduleCountMap[domain.id] = (moduleCountMap[domain.id] || 0) + 1
    }
  }
  return DOMAINS
    .map(d => ({ ...d, count: countMap[d.id] || 0, moduleCount: moduleCountMap[d.id] || 0 }))
    .filter(d => d.count > 0)
})

const totalCount = computed(() => domainsWithCount.value.reduce((s, d) => s + d.count, 0))

// 用 allRegs 获取状态和部门信息（tree 里的 reg 对象可能不全）
const regMap = computed(() => {
  const m = {}
  for (const r of allRegs.value) m[r.id] = r
  return m
})
</script>

<style scoped>
.reg-list-page { padding-bottom: 24px; }

/* ── 面包屑 ── */
.breadcrumb {
  display: flex; align-items: center; gap: 6px;
  margin-bottom: 18px;
  font-size: 12px; color: var(--muted);
  padding: 22px 24px 0;
}
.bc-link { color: var(--muted); text-decoration: none; transition: color 0.13s; }
.bc-link:hover { color: var(--blue); }
.bc-sep { color: var(--subtle); font-size: 11px; }
.bc-current { color: var(--fg); font-weight: 500; }

/* ── 页面标题 ── */
.page-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  margin-bottom: 20px; padding: 0 24px;
}
.page-title { font-size: 17px; font-weight: 700; color: var(--fg); }
.page-sub { font-size: 12px; color: var(--muted); margin-top: 4px; }

/* ── 模式1: 域总览 ── */
.domain-overview {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px;
  padding: 0 24px;
}

.domain-card {
  background: var(--surface);
  border: 1px solid var(--blue-border);
  border-top: 3px solid var(--d-color, var(--blue));
  border-radius: 12px;
  padding: 18px;
  text-decoration: none; color: inherit;
  display: flex; flex-direction: column; gap: 8px;
  box-shadow: var(--blue-glow);
  transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
  cursor: pointer;
}
.domain-card:hover {
  border-color: rgba(37,99,235,0.3);
  box-shadow: 0 8px 24px rgba(37,99,235,0.12);
  transform: translateY(-2px);
}

.dc-top { display: flex; align-items: center; gap: 8px; }
.dc-dot {
  width: 9px; height: 9px; border-radius: 50%;
  background: var(--d-color, var(--blue)); flex-shrink: 0;
  box-shadow: 0 0 6px var(--d-color, rgba(37,99,235,0.5));
}
.dc-label { font-size: 13.5px; font-weight: 700; color: var(--d-color, var(--blue)); flex: 1; }
.dc-count { font-size: 20px; font-weight: 700; color: var(--d-color, var(--blue)); }
.dc-desc { font-size: 11px; color: var(--muted); }
.dc-modules { font-size: 11px; color: var(--subtle); margin-top: auto; padding-top: 8px; border-top: 1px solid var(--blue-border); }

/* ── 模式2: 大类模块列表 ── */
.module-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px;
  padding: 0 24px;
}

.module-card {
  background: var(--surface);
  border: 1px solid var(--blue-border);
  border-top: 3px solid var(--d-color, var(--blue));
  border-radius: 12px;
  padding: 16px 18px;
  text-decoration: none; color: inherit;
  display: flex; flex-direction: column; gap: 8px;
  box-shadow: var(--blue-glow);
  transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
  cursor: pointer; min-height: 100px;
}
.module-card:hover {
  border-color: rgba(37,99,235,0.3);
  box-shadow: 0 8px 24px rgba(37,99,235,0.12);
  transform: translateY(-2px);
}

.mc-header { display: flex; align-items: center; gap: 9px; }
.mc-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--d-color, var(--blue)); flex-shrink: 0;
  box-shadow: 0 0 5px var(--d-color, rgba(37,99,235,0.4));
}
.mc-name { font-size: 14px; font-weight: 600; color: var(--fg); }
.mc-meta { font-size: 11px; color: var(--subtle); }
.mc-count { display: flex; align-items: baseline; gap: 3px; margin-top: 4px; }
.mc-num { font-size: 22px; font-weight: 700; color: var(--d-color, var(--blue)); }
.mc-unit { font-size: 12px; color: var(--muted); }
.mc-arrow { color: var(--d-color, var(--blue)); margin-top: auto; align-self: flex-end; opacity: 0.6; }
.module-card:hover .mc-arrow { opacity: 1; }

/* ── 模式3: 制度列表 ── */
.subcat-list { display: flex; flex-direction: column; gap: 24px; padding: 0 24px; }

.subcat-label {
  font-size: 11px; font-weight: 700;
  color: var(--blue);
  letter-spacing: 0.06em; text-transform: uppercase;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 2px solid rgba(37,99,235,0.15);
  display: flex; align-items: center; gap: 8px;
}
.subcat-label::before {
  content: '';
  width: 5px; height: 5px; border-radius: 50%;
  background: var(--blue); display: inline-block;
  box-shadow: 0 0 5px rgba(37,99,235,0.4);
}

.reg-list { display: flex; flex-direction: column; gap: 6px; }

.reg-item {
  display: flex; align-items: center; gap: 12px;
  padding: 11px 16px;
  background: var(--surface);
  border: 1px solid var(--blue-border); border-radius: 10px;
  text-decoration: none; color: inherit;
  box-shadow: var(--blue-glow);
  transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
}
.reg-item:hover {
  border-color: rgba(37,99,235,0.3);
  box-shadow: 0 8px 24px rgba(37,99,235,0.12);
  transform: translateY(-2px);
}

.reg-item-id {
  font-family: var(--mono); font-size: 10px;
  background: var(--blue); color: white;
  padding: 2px 8px; border-radius: 4px; flex-shrink: 0;
}
.reg-item-body { flex: 1; min-width: 0; }
.reg-item-name { font-size: 13px; font-weight: 500; color: var(--fg); display: block; }
.reg-item-dept { font-size: 11px; color: var(--muted); margin-top: 2px; display: block; }
.reg-arrow { color: var(--blue-light); flex-shrink: 0; transition: transform 0.2s; }
.reg-item:hover .reg-arrow { transform: translateX(3px); }
</style>
