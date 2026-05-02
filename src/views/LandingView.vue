<template>
  <div class="landing-page">

    <!-- NAV -->
    <nav class="nav">
      <div class="nav-brand">
        <div class="nav-icon">制</div>
        制度助理
      </div>
      <ul class="nav-links">
        <li><a @click.prevent="scrollTo('features')" href="#">功能介绍</a></li>
        <li><a @click.prevent="scrollTo('dashboard')" href="#">平台预览</a></li>
        <li><a @click.prevent="scrollTo('footer')" href="#">关于</a></li>
      </ul>
      <button class="nav-cta" @click="$router.push('/home')">进入系统</button>
    </nav>

    <!-- HERO -->
    <section class="hero" id="hero">
      <canvas ref="canvas" id="particles-canvas"></canvas>
      <div class="hero-inner">
        <!-- Left -->
        <div>
          <div class="eyebrow-pill">
            <span class="pulse-dot"></span>
            西北投资产业发展中心 · 数字化平台
          </div>
          <h1 class="hero-title">制度助理</h1>
          <p class="hero-subtitle">西北投资制度管理平台</p>
          <div class="hero-stats">
            <div class="hero-stat">
              <div class="stat-value"><span>{{ heroRegs }}</span><span class="stat-suffix">条</span></div>
              <div class="stat-label">制度总数</div>
            </div>
            <div class="hero-stat">
              <div class="stat-value"><span>{{ heroAuth }}</span><span class="stat-suffix">条</span></div>
              <div class="stat-label">权责事项</div>
            </div>
            <div class="hero-stat">
              <div class="stat-value"><span>7</span><span class="stat-suffix">个</span></div>
              <div class="stat-label">职能域</div>
            </div>
          </div>
          <div class="hero-actions">
            <button class="btn-primary" @click="$router.push('/home')">
              <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.2"><path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14M12 5l7 7-7 7"/></svg>
              进入系统
            </button>
            <a href="#" class="btn-ghost" @click.prevent="scrollTo('features')">
              了解更多
              <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
            </a>
          </div>
        </div>

        <!-- Right: glass cards -->
        <div class="hero-right">
          <div class="glass-card">
            <div class="card-header">
              <span class="card-title">平台核心能力</span>
            </div>
            <div class="activity-list">
              <div class="activity-row">
                <div class="activity-dot" style="background:#34d399;box-shadow:0 0 5px rgba(52,211,153,0.6)"></div>
                <div>
                  <div class="activity-text">{{ totalRegs || '—' }} 条制度完整数字化</div>
                  <div class="activity-meta">涵盖 7 大职能域全业务体系</div>
                </div>
              </div>
              <div class="activity-row">
                <div class="activity-dot" style="background:#60a5fa;box-shadow:0 0 5px rgba(96,165,250,0.6)"></div>
                <div>
                  <div class="activity-text">{{ authTotal || '—' }} 条权责事项精准关联</div>
                  <div class="activity-meta">制度–权责清单全链路映射</div>
                </div>
              </div>
              <div class="activity-row">
                <div class="activity-dot" style="background:#c084fc;box-shadow:0 0 5px rgba(192,132,252,0.6)"></div>
                <div>
                  <div class="activity-text">审批流程可视化图表</div>
                  <div class="activity-meta">关键业务流程结构化呈现</div>
                </div>
              </div>
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header"><span class="card-title">各域制度数量</span></div>
            <div v-for="d in domainCounts" :key="d.id" class="prog-row" style="margin-bottom:6px;gap:3px">
              <div class="prog-head">
                <span class="prog-label">{{ d.label }}</span>
                <span class="prog-pct">{{ d.count }} 条</span>
              </div>
              <div class="prog-track">
                <div class="prog-fill" :style="{ width: (d.pct || 0) + '%', background: d.gradient }"></div>
              </div>
            </div>
          </div>
          <div class="glass-card" style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
            <div v-for="q in quickStats" :key="q.label">
              <div :style="{ fontSize:'22px', fontWeight:800, letterSpacing:'-0.03em', color: q.color }">{{ q.value }}</div>
              <div style="font-size:11px;color:rgba(199,217,240,0.45);margin-top:2px">{{ q.label }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- FEATURES -->
    <section class="features-section" id="features">
      <div class="section-wrap">
        <div class="section-eyebrow fade-in"><span class="tag-pill">核心功能</span></div>
        <h2 class="section-h2 fade-in">一体化制度管理平台</h2>
        <p class="section-desc fade-in">覆盖制度全生命周期——从起草、审批、归档到检索，以数字化手段提升合规管理效率</p>
        <div class="feature-grid">
          <div class="feature-card fade-in" data-delay="1">
            <div class="icon-wrap icon-doc">
              <svg width="38" height="38" viewBox="0 0 38 38" fill="none">
                <defs><linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#93c5fd"/><stop offset="100%" stop-color="#2563EB"/></linearGradient></defs>
                <rect x="6" y="4" width="18" height="26" rx="3" fill="none" stroke="url(#g1)" stroke-width="1.6"/>
                <path d="M10 11h10M10 15.5h10M10 20h6" stroke="url(#g1)" stroke-width="1.5" stroke-linecap="round"/>
                <rect x="19" y="18" width="13" height="15" rx="3" fill="url(#g1)" opacity="0.35"/>
                <path d="M21.5 22.5h8M21.5 26h5" stroke="#93c5fd" stroke-width="1.2" stroke-linecap="round" opacity="0.9"/>
              </svg>
            </div>
            <h3 class="feature-card-title">制度库管理</h3>
            <p class="feature-card-desc">结构化归档全公司制度文档，支持版本历史追踪、在线审批流转、全文语义检索与多维分类浏览，确保每条制度可查、可溯、可执行。</p>
            <div class="feature-tags"><span class="feat-tag">版本管理</span><span class="feat-tag">全文检索</span><span class="feat-tag">审批流转</span><span class="feat-tag">分类归档</span></div>
          </div>
          <div class="feature-card fade-in" data-delay="2">
            <div class="icon-wrap icon-shield">
              <svg width="38" height="38" viewBox="0 0 38 38" fill="none">
                <defs><linearGradient id="g2" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#34d399"/><stop offset="100%" stop-color="#059669"/></linearGradient></defs>
                <path d="M19 5L8 9.5V19c0 5.8 4.6 11.1 11 12.5C26.4 30.1 31 24.8 31 19V9.5L19 5z" fill="none" stroke="url(#g2)" stroke-width="1.6"/>
                <path d="M14 18.5l3.5 3.5 7-7" stroke="url(#g2)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <h3 class="feature-card-title">权责清单</h3>
            <p class="feature-card-desc">精确界定各岗位的权力边界与履职责任，支持权责矩阵可视化呈现、岗位-制度精准关联，让合规追踪有据可查、有章可循。</p>
            <div class="feature-tags"><span class="feat-tag">权责矩阵</span><span class="feat-tag">岗位映射</span><span class="feat-tag">合规追踪</span><span class="feat-tag">200+ 事项</span></div>
          </div>
          <div class="feature-card fade-in" data-delay="3">
            <div class="icon-wrap icon-network">
              <svg width="38" height="38" viewBox="0 0 38 38" fill="none">
                <defs><linearGradient id="g3" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#c084fc"/><stop offset="100%" stop-color="#7c3aed"/></linearGradient></defs>
                <line class="net-line" x1="19" y1="9" x2="10" y2="22" stroke="url(#g3)" stroke-width="1.3"/>
                <line class="net-line" x1="19" y1="9" x2="28" y2="22" stroke="url(#g3)" stroke-width="1.3"/>
                <line class="net-line" x1="10" y1="22" x2="6" y2="31" stroke="url(#g3)" stroke-width="1" opacity="0.65"/>
                <line class="net-line" x1="10" y1="22" x2="14" y2="31" stroke="url(#g3)" stroke-width="1" opacity="0.65"/>
                <line class="net-line" x1="28" y1="22" x2="24" y2="31" stroke="url(#g3)" stroke-width="1" opacity="0.65"/>
                <line class="net-line" x1="28" y1="22" x2="32" y2="31" stroke="url(#g3)" stroke-width="1" opacity="0.65"/>
                <circle cx="19" cy="8" r="4" fill="url(#g3)"/>
                <circle cx="10" cy="22" r="3.2" fill="url(#g3)" opacity="0.85"/>
                <circle cx="28" cy="22" r="3.2" fill="url(#g3)" opacity="0.85"/>
                <circle cx="6" cy="31" r="2.2" fill="url(#g3)" opacity="0.6"/>
                <circle cx="14" cy="31" r="2.2" fill="url(#g3)" opacity="0.6"/>
                <circle cx="24" cy="31" r="2.2" fill="url(#g3)" opacity="0.6"/>
                <circle cx="32" cy="31" r="2.2" fill="url(#g3)" opacity="0.6"/>
              </svg>
            </div>
            <h3 class="feature-card-title">组织架构</h3>
            <p class="feature-card-desc">可视化呈现西北投资完整组织层级，按 7 大职能域浏览部门与岗位，并与制度文档、权责事项形成三维关联图谱。</p>
            <div class="feature-tags"><span class="feat-tag">可视化图谱</span><span class="feat-tag">7 大职能域</span><span class="feat-tag">三维关联</span></div>
          </div>
        </div>
      </div>
    </section>

    <!-- DASHBOARD PREVIEW -->
    <section class="dashboard-section" id="dashboard">
      <div class="section-wrap">
        <div class="section-eyebrow fade-in"><span class="tag-pill">平台预览</span></div>
        <h2 class="section-h2 fade-in">专业级制度管理界面</h2>
        <p class="section-desc fade-in">清晰的信息架构，覆盖 7 个职能域，让日常制度管理简洁高效</p>
        <div class="mockup-outer fade-in">
          <div class="mockup-glow"></div>
          <div class="mockup-frame">
            <div class="titlebar">
              <span class="tb-dot tb-red"></span><span class="tb-dot tb-yellow"></span><span class="tb-dot tb-green"></span>
              <span class="tb-label">制度助理 — 西北投资制度管理平台</span>
            </div>
            <div class="mockup-body">
              <div class="m-sidebar">
                <div class="m-sidebar-logo"><div class="m-logo-text">制度助理</div><div class="m-logo-sub">西北投资（园区运营公司）</div></div>
                <div class="m-section-label">职能域</div>
                <div class="m-nav-item active"><div class="m-nav-dot"></div>综合管理</div>
                <div class="m-nav-item"><div class="m-nav-dot"></div>财务管理</div>
                <div class="m-nav-item"><div class="m-nav-dot"></div>人力资源</div>
                <div class="m-nav-item"><div class="m-nav-dot"></div>招商运营</div>
                <div class="m-nav-item"><div class="m-nav-dot"></div>工程建设</div>
                <div class="m-nav-item"><div class="m-nav-dot"></div>安全管理</div>
                <div class="m-nav-item"><div class="m-nav-dot"></div>法务合规</div>
                <div class="m-section-label" style="margin-top:6px">工具</div>
                <div class="m-nav-item"><div class="m-nav-dot"></div>权责清单</div>
                <div class="m-nav-item"><div class="m-nav-dot"></div>组织架构</div>
              </div>
              <div class="m-main">
                <div class="m-header">
                  <div class="m-title">综合管理 · 制度库</div>
                  <div class="m-search"><svg width="11" height="11" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>搜索制度文件...</div>
                </div>
                <div class="m-stat-row">
                  <div class="m-stat-card"><div class="m-stat-value">8</div><div class="m-stat-label">综合管理制度</div></div>
                  <div class="m-stat-card"><div class="m-stat-value">6</div><div class="m-stat-label">本月更新</div></div>
                  <div class="m-stat-card"><div class="m-stat-value">42</div><div class="m-stat-label">关联权责条目</div></div>
                  <div class="m-stat-card"><div class="m-stat-value" style="color:#34d399">100%</div><div class="m-stat-label">覆盖率</div></div>
                </div>
                <div class="m-table-header"><div>制度名称</div><div>职能域</div><div>版本</div><div>状态</div></div>
                <div class="m-table-row"><div class="m-cell">内部控制管理办法</div><div class="m-cell-dim">综合管理</div><div class="m-cell-dim">v2.1</div><div><span class="m-badge badge-ok">有效</span></div></div>
                <div class="m-table-row"><div class="m-cell">公文管理规定</div><div class="m-cell-dim">综合管理</div><div class="m-cell-dim">v1.3</div><div><span class="m-badge badge-ok">有效</span></div></div>
                <div class="m-table-row"><div class="m-cell">信息化管理制度</div><div class="m-cell-dim">综合管理</div><div class="m-cell-dim">v1.0</div><div><span class="m-badge badge-wip">审核中</span></div></div>
                <div class="m-table-row"><div class="m-cell">档案管理办法</div><div class="m-cell-dim">综合管理</div><div class="m-cell-dim">v1.2</div><div><span class="m-badge badge-ok">有效</span></div></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- FOOTER -->
    <footer id="footer">
      <div class="footer-inner">
        <div class="footer-hierarchy">
          <span>中交投资有限公司</span>
          <span class="footer-sep">›</span>
          <span class="footer-hl">西北投资（园区运营公司）</span>
          <span class="footer-sep">›</span>
          <span style="color:rgba(199,217,240,0.55)">产业发展中心</span>
        </div>
        <div class="footer-copy">© 2025 西北投资产业发展中心 · 制度助理 v1.0</div>
      </div>
    </footer>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { getRegulations, getTree, getAuthority } from '../data/api.js'
import { DOMAINS, getDomainByModuleName } from '../utils/authorityCategories.js'

const canvas = ref(null)
const regs = ref([])
const authItems = ref([])
const tree = ref({})
const heroRegs = ref(0)
const heroAuth = ref(0)

const totalRegs = computed(() => regs.value.length)
const authTotal = computed(() =>
  authItems.value.filter(i => i.name && i.flow && i.flow.length > 0).length
)

const DOMAIN_GRADIENTS = {
  governance: 'linear-gradient(90deg,#1E3A5F,#3b82f6)',
  hr:         'linear-gradient(90deg,#0284C7,#38bdf8)',
  finance:    'linear-gradient(90deg,#16A34A,#34d399)',
  operations: 'linear-gradient(90deg,#7C3AED,#c084fc)',
  tech:       'linear-gradient(90deg,#0891B2,#22d3ee)',
  compliance: 'linear-gradient(90deg,#DC2626,#f87171)',
  party:      'linear-gradient(90deg,#B45309,#fbbf24)',
}

const domainCounts = computed(() => {
  const countMap = {}
  for (const [modName, items] of Object.entries(tree.value)) {
    const domain = getDomainByModuleName(modName)
    if (domain) {
      const cnt = Object.values(items).reduce((s, a) => s + a.length, 0)
      countMap[domain.id] = (countMap[domain.id] || 0) + cnt
    }
  }
  const withCounts = DOMAINS.map(d => ({
    ...d,
    count: countMap[d.id] || 0,
    gradient: DOMAIN_GRADIENTS[d.id],
  }))
  const maxCount = Math.max(...withCounts.map(d => d.count), 1)
  return withCounts
    .map(d => ({ ...d, pct: Math.round(d.count / maxCount * 100) }))
    .filter(d => d.count > 0)
})

const quickStats = computed(() => [
  { value: totalRegs.value || '—', label: '制度总数', color: '#60a5fa' },
  { value: authTotal.value || '—', label: '权责事项', color: '#34d399' },
  { value: '7', label: '职能域', color: '#c084fc' },
  { value: '100%', label: '制度在线化', color: '#fb923c' },
])

function scrollTo(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}

function animateTo(target, setter) {
  const dur = 1600
  const t0 = performance.now()
  function tick(now) {
    const p = Math.min((now - t0) / dur, 1)
    const ease = 1 - Math.pow(1 - p, 3)
    setter(Math.round(ease * target))
    if (p < 1) requestAnimationFrame(tick)
  }
  requestAnimationFrame(tick)
}

let raf = null

function initParticles() {
  const el = canvas.value
  if (!el) return
  const ctx = el.getContext('2d')
  let W, H, pts

  function size() {
    const sec = el.parentElement
    W = el.width = sec.offsetWidth
    H = el.height = sec.offsetHeight
  }

  function make(n) {
    pts = Array.from({ length: n }, () => ({
      x: Math.random() * W, y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.35,
      vy: (Math.random() - 0.5) * 0.35,
      r: Math.random() * 1.4 + 0.5,
      op: Math.random() * 0.45 + 0.15,
    }))
  }

  function draw() {
    ctx.clearRect(0, 0, W, H)
    const n = pts.length
    for (let i = 0; i < n; i++) {
      const p = pts[i]
      p.x += p.vx; p.y += p.vy
      if (p.x < 0) p.x = W; if (p.x > W) p.x = 0
      if (p.y < 0) p.y = H; if (p.y > H) p.y = 0
      ctx.beginPath()
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(199,217,240,${p.op})`
      ctx.fill()
      for (let j = i + 1; j < n; j++) {
        const q = pts[j]
        const dx = p.x - q.x, dy = p.y - q.y
        const d = Math.sqrt(dx * dx + dy * dy)
        if (d < 110) {
          ctx.beginPath()
          ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y)
          ctx.strokeStyle = `rgba(37,99,235,${(1 - d / 110) * 0.14})`
          ctx.lineWidth = 0.8
          ctx.stroke()
        }
      }
    }
    raf = requestAnimationFrame(draw)
  }

  function init() { size(); make(75); draw() }
  window.addEventListener('resize', () => { cancelAnimationFrame(raf); init() })
  init()
}

function initScrollFade() {
  const fadeIO = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible') })
  }, { threshold: 0.13 })
  document.querySelectorAll('.fade-in').forEach(el => fadeIO.observe(el))
}

onMounted(() => {
  initParticles()
  initScrollFade()
  regs.value = getRegulations()
  tree.value = getTree()
  authItems.value = getAuthority()
  animateTo(regs.value.length, v => { heroRegs.value = v })
  animateTo(authTotal.value, v => { heroAuth.value = v })
})

onUnmounted(() => {
  if (raf) cancelAnimationFrame(raf)
})
</script>

<style scoped>
.landing-page {
  background: #0a1222;
  color: #fff;
  font-family: 'PingFang SC','Noto Sans SC','Microsoft YaHei UI','Microsoft YaHei',-apple-system,system-ui,sans-serif;
  min-height: 100vh;
  overflow-x: hidden;
  line-height: 1.6;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0d1f35; }
::-webkit-scrollbar-thumb { background: rgba(37,99,235,0.4); border-radius: 3px; }

/* NAV */
.nav {
  position: fixed; top:0; left:0; right:0; z-index:200;
  height: 60px;
  display: flex; align-items:center; justify-content:space-between;
  padding: 0 48px;
  background: rgba(8,15,29,0.75);
  backdrop-filter: blur(24px);
  border-bottom: 1px solid rgba(199,217,240,0.10);
}
.nav-brand { display:flex; align-items:center; gap:10px; font-size:16px; font-weight:700; letter-spacing:-0.02em; }
.nav-icon {
  width:32px; height:32px; border-radius:8px;
  background: linear-gradient(135deg, #2563EB, #60a5fa);
  display:flex; align-items:center; justify-content:center;
  font-size:13px; font-weight:800; color:#fff;
  box-shadow: 0 0 16px rgba(37,99,235,0.35); flex-shrink:0;
}
.nav-links { display:flex; gap:28px; list-style:none; }
.nav-links a { font-size:14px; color:rgba(255,255,255,0.70); text-decoration:none; transition:color 0.2s; }
.nav-links a:hover { color:#fff; }
.nav-cta {
  background: #2563EB; color:#fff;
  border:none; padding:8px 20px; border-radius:8px;
  font-size:14px; font-weight:500; cursor:pointer;
  box-shadow: 0 0 24px rgba(37,99,235,0.45);
  transition: all 0.2s; font-family:inherit;
}
.nav-cta:hover { box-shadow: 0 0 36px rgba(37,99,235,0.55); transform:translateY(-1px); }

/* HERO */
.hero {
  position:relative; min-height:100vh;
  display:flex; align-items:center; overflow:hidden;
  background:
    radial-gradient(ellipse 70% 60% at 20% 50%, rgba(37,99,235,0.14) 0%, transparent 70%),
    radial-gradient(ellipse 50% 70% at 85% 30%, rgba(30,58,95,0.35) 0%, transparent 60%),
    linear-gradient(180deg, #080f1d 0%, #0a1628 100%);
  padding: 100px 0 80px;
}
#particles-canvas { position:absolute; inset:0; pointer-events:none; }
.hero-inner {
  position:relative; z-index:2;
  max-width:1240px; margin:0 auto; padding:0 48px;
  display:grid; grid-template-columns:1fr 360px; gap:64px; align-items:center;
}

.eyebrow-pill {
  display:inline-flex; align-items:center; gap:8px;
  padding:5px 14px;
  background: rgba(37,99,235,0.12);
  border: 1px solid rgba(37,99,235,0.28);
  border-radius:100px; font-size:12px; color:#C7D9F0;
  margin-bottom:24px; letter-spacing:0.04em;
}
.pulse-dot {
  width:7px; height:7px; border-radius:50%; background:#2563EB;
  animation: pulse-dot 2s ease-in-out infinite;
  box-shadow: 0 0 6px #2563EB;
}
@keyframes pulse-dot {
  0%,100%{ opacity:1; transform:scale(1); }
  50%{ opacity:0.55; transform:scale(0.75); }
}

.hero-title {
  font-size: clamp(60px, 8.5vw, 104px);
  font-weight:800; line-height:1.0; letter-spacing:-0.05em;
  background: linear-gradient(135deg, #ffffff 0%, #c7d9f0 55%, #93c5fd 100%);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
  margin-bottom:14px;
}
.hero-subtitle { font-size:clamp(16px,2.2vw,22px); color:#C7D9F0; font-weight:400; letter-spacing:0.1em; opacity:0.8; margin-bottom:40px; }

.hero-stats { display:flex; gap:0; margin-bottom:44px; }
.hero-stat { display:flex; flex-direction:column; padding-right:32px; }
.hero-stat + .hero-stat { padding-left:32px; border-left:1px solid rgba(199,217,240,0.14); }
.hero-stat:last-child { padding-right:0; }
.stat-value { font-size:38px; font-weight:800; letter-spacing:-0.03em; line-height:1; color:#fff; }
.stat-suffix { font-size:20px; font-weight:500; color:#C7D9F0; margin-left:2px; }
.stat-label { font-size:12px; color:rgba(199,217,240,0.55); margin-top:5px; letter-spacing:0.02em; }

.hero-actions { display:flex; gap:14px; flex-wrap:wrap; }
.btn-primary {
  display:inline-flex; align-items:center; gap:8px;
  background:#2563EB; color:#fff;
  padding:13px 28px; border-radius:10px;
  font-size:15px; font-weight:500; font-family:inherit;
  border: 1px solid rgba(96,165,250,0.3);
  box-shadow: 0 0 0 1px rgba(37,99,235,0.4), 0 4px 28px rgba(37,99,235,0.45);
  animation: btn-glow 3s ease-in-out infinite;
  transition: all 0.25s; cursor:pointer;
}
@keyframes btn-glow {
  0%,100%{ box-shadow:0 0 0 1px rgba(37,99,235,0.4), 0 4px 28px rgba(37,99,235,0.45); }
  50%{ box-shadow:0 0 0 1px rgba(37,99,235,0.6), 0 4px 44px rgba(37,99,235,0.65); }
}
.btn-primary:hover { transform:translateY(-2px); }
.btn-ghost {
  display:inline-flex; align-items:center; gap:8px;
  background:transparent; color:#C7D9F0;
  padding:13px 28px; border-radius:10px;
  font-size:15px; font-weight:500; font-family:inherit;
  border: 1px solid rgba(199,217,240,0.22);
  backdrop-filter:blur(8px); transition:all 0.25s; text-decoration:none;
}
.btn-ghost:hover { border-color:rgba(199,217,240,0.45); background:rgba(199,217,240,0.07); transform:translateY(-2px); }

/* GLASS CARDS */
.hero-right { display:flex; flex-direction:column; gap:14px; }
.glass-card {
  background: rgba(255,255,255,0.055); backdrop-filter:blur(20px);
  border: 1px solid rgba(199,217,240,0.13); border-radius:16px; padding:18px 20px;
}
.glass-card:nth-child(1){ animation:float-a 7s ease-in-out infinite; }
.glass-card:nth-child(2){ animation:float-b 8s ease-in-out infinite; }
.glass-card:nth-child(3){ animation:float-c 6.5s ease-in-out infinite; }
@keyframes float-a { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-7px)} }
@keyframes float-b { 0%,100%{transform:translateY(-4px)} 50%{transform:translateY(4px)} }
@keyframes float-c { 0%,100%{transform:translateY(2px)} 50%{transform:translateY(-5px)} }

.card-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; }
.card-title { font-size:12px; font-weight:600; color:#C7D9F0; letter-spacing:0.05em; }
.card-badge { font-size:10px; padding:2px 8px; background:rgba(37,99,235,0.18); border:1px solid rgba(37,99,235,0.3); border-radius:100px; color:#93c5fd; }
.activity-list { display:flex; flex-direction:column; gap:9px; }
.activity-row { display:flex; align-items:flex-start; gap:9px; }
.activity-dot { width:5px; height:5px; border-radius:50%; background:#2563EB; margin-top:6px; flex-shrink:0; box-shadow:0 0 5px rgba(37,99,235,0.7); }
.activity-text { font-size:12px; color:rgba(255,255,255,0.75); line-height:1.4; }
.activity-meta { font-size:10px; color:rgba(199,217,240,0.38); margin-top:2px; }

.prog-row { display:flex; flex-direction:column; gap:5px; margin-bottom:10px; }
.prog-row:last-child{ margin-bottom:0; }
.prog-head { display:flex; justify-content:space-between; align-items:center; }
.prog-label { font-size:12px; color:rgba(255,255,255,0.75); }
.prog-pct { font-size:12px; color:#C7D9F0; font-weight:600; }
.prog-track { height:3px; background:rgba(255,255,255,0.07); border-radius:99px; overflow:hidden; }
.prog-fill { height:100%; border-radius:99px; background:linear-gradient(90deg, #2563EB, #60a5fa); }

/* SECTIONS */
.section-wrap { max-width:1240px; margin:0 auto; padding:0 48px; }
.section-eyebrow { text-align:center; margin-bottom:14px; }
.tag-pill { display:inline-flex; align-items:center; gap:5px; padding:4px 14px; background:rgba(37,99,235,0.09); border:1px solid rgba(37,99,235,0.22); border-radius:100px; font-size:12px; color:#93c5fd; letter-spacing:0.04em; }
.section-h2 { text-align:center; font-size:clamp(26px,3.8vw,42px); font-weight:700; letter-spacing:-0.03em; background:linear-gradient(135deg,#ffffff 0%,#c7d9f0 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; margin-bottom:10px; }
.section-desc { text-align:center; font-size:15px; color:rgba(199,217,240,0.6); max-width:480px; margin:0 auto 56px; }

/* FEATURES */
.features-section { padding:100px 0; background:linear-gradient(180deg,#0a1628 0%,#0d1f35 100%); }
.feature-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:22px; }
.feature-card {
  background:rgba(30,58,95,0.3); border:1px solid rgba(199,217,240,0.09);
  border-radius:20px; padding:32px 26px; position:relative; overflow:hidden;
  transition:all 0.3s cubic-bezier(0.25,0.8,0.25,1);
}
.feature-card::before { content:''; position:absolute; inset:0; border-radius:20px; background:radial-gradient(ellipse at 0% 0%, rgba(37,99,235,0.07) 0%, transparent 55%); pointer-events:none; }
.feature-card:hover { border-color:rgba(37,99,235,0.28); transform:translateY(-5px); box-shadow:0 24px 64px rgba(0,0,0,0.45),0 0 48px rgba(37,99,235,0.09); }

.icon-wrap { width:68px; height:68px; border-radius:16px; display:flex; align-items:center; justify-content:center; margin-bottom:22px; position:relative; }
.icon-doc { background:linear-gradient(135deg,rgba(37,99,235,0.28) 0%,rgba(96,165,250,0.12) 100%); box-shadow:0 0 0 1px rgba(37,99,235,0.3); animation:glow-doc 3.5s ease-in-out infinite; }
@keyframes glow-doc { 0%,100%{ box-shadow:0 0 0 1px rgba(37,99,235,0.3),0 0 20px rgba(37,99,235,0.18); } 50%{ box-shadow:0 0 0 1px rgba(37,99,235,0.5),0 0 38px rgba(37,99,235,0.35); } }
.icon-shield { background:linear-gradient(135deg,rgba(16,185,129,0.22) 0%,rgba(37,99,235,0.12) 100%); box-shadow:0 0 0 1px rgba(16,185,129,0.28); }
.icon-shield::after { content:''; position:absolute; inset:-10px; border-radius:26px; border:1.5px solid rgba(16,185,129,0.28); animation:pulse-ring 2.2s ease-out infinite; }
.icon-shield::before { content:''; position:absolute; inset:-20px; border-radius:36px; border:1px solid rgba(16,185,129,0.12); animation:pulse-ring 2.2s ease-out 0.5s infinite; }
@keyframes pulse-ring { 0%{ opacity:0.9; transform:scale(1); } 100%{ opacity:0; transform:scale(1.35); } }
.icon-network { background:linear-gradient(135deg,rgba(168,85,247,0.22) 0%,rgba(37,99,235,0.12) 100%); box-shadow:0 0 0 1px rgba(168,85,247,0.28); }
.feature-card-title { font-size:19px; font-weight:700; letter-spacing:-0.01em; margin-bottom:10px; color:#fff; }
.feature-card-desc { font-size:13px; color:rgba(199,217,240,0.58); line-height:1.65; }
.feature-tags { display:flex; flex-wrap:wrap; gap:6px; margin-top:18px; }
.feat-tag { font-size:11px; padding:3px 10px; background:rgba(37,99,235,0.1); border:1px solid rgba(37,99,235,0.2); border-radius:100px; color:#93c5fd; }
.net-line { stroke-dasharray:40; stroke-dashoffset:40; animation:draw-net 2s ease-in-out infinite alternate; }
.net-line:nth-child(2){ animation-delay:0.4s; }
@keyframes draw-net { to{ stroke-dashoffset:0; } }

/* DASHBOARD MOCKUP */
.dashboard-section { padding:100px 0; background:linear-gradient(180deg,#0d1f35 0%,#080f1d 100%); overflow:hidden; }
.mockup-outer { margin-top:52px; position:relative; animation:float-mockup 9s ease-in-out infinite; perspective:1200px; }
@keyframes float-mockup { 0%,100%{transform:translateY(0) rotateX(1.5deg);} 50%{transform:translateY(-14px) rotateX(0deg);} }
.mockup-glow { position:absolute; inset:-40px; z-index:0; pointer-events:none; background:radial-gradient(ellipse at 50% 60%,rgba(37,99,235,0.22) 0%,transparent 65%); }
.mockup-frame { position:relative; z-index:1; background:rgba(10,18,34,0.95); border:1px solid rgba(199,217,240,0.13); border-radius:16px; overflow:hidden; box-shadow:0 0 0 1px rgba(37,99,235,0.14),0 32px 100px rgba(0,0,0,0.65),0 0 60px rgba(37,99,235,0.1); }
.titlebar { display:flex; align-items:center; gap:8px; padding:11px 16px; background:rgba(6,12,24,0.9); border-bottom:1px solid rgba(199,217,240,0.07); }
.tb-dot { width:12px; height:12px; border-radius:50%; }
.tb-red { background:#ff5f57; } .tb-yellow { background:#febc2e; } .tb-green { background:#28c840; }
.tb-label { margin-left:8px; font-size:12px; color:rgba(199,217,240,0.35); }
.mockup-body { display:flex; height:380px; }
.m-sidebar { width:188px; flex-shrink:0; background:rgba(8,15,29,0.8); border-right:1px solid rgba(199,217,240,0.06); display:flex; flex-direction:column; }
.m-sidebar-logo { padding:14px 16px 12px; border-bottom:1px solid rgba(199,217,240,0.06); margin-bottom:6px; }
.m-logo-text { font-size:13px; font-weight:700; color:#C7D9F0; }
.m-logo-sub { font-size:10px; color:rgba(199,217,240,0.35); margin-top:1px; }
.m-section-label { padding:10px 16px 4px; font-size:10px; color:rgba(199,217,240,0.28); letter-spacing:0.08em; text-transform:uppercase; }
.m-nav-item { display:flex; align-items:center; gap:7px; padding:7px 16px; font-size:12px; color:rgba(199,217,240,0.5); border-left:2px solid transparent; }
.m-nav-item.active { color:#fff; background:rgba(37,99,235,0.13); border-left-color:#2563EB; }
.m-nav-dot { width:4px; height:4px; border-radius:50%; background:currentColor; opacity:0.65; flex-shrink:0; }
.m-main { flex:1; padding:18px; overflow:hidden; }
.m-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; }
.m-title { font-size:14px; font-weight:600; color:#fff; }
.m-search { display:flex; align-items:center; gap:6px; padding:5px 10px; background:rgba(255,255,255,0.04); border:1px solid rgba(199,217,240,0.09); border-radius:6px; font-size:11px; color:rgba(199,217,240,0.35); }
.m-stat-row { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:16px; }
.m-stat-card { background:rgba(255,255,255,0.038); border:1px solid rgba(199,217,240,0.07); border-radius:9px; padding:10px 12px; }
.m-stat-value { font-size:19px; font-weight:700; color:#fff; letter-spacing:-0.02em; }
.m-stat-label { font-size:10px; color:rgba(199,217,240,0.4); margin-top:2px; }
.m-table-header { display:grid; grid-template-columns:1fr 90px 70px 72px; gap:6px; padding:6px 0; font-size:10px; color:rgba(199,217,240,0.32); letter-spacing:0.04em; border-bottom:1px solid rgba(199,217,240,0.07); margin-bottom:4px; }
.m-table-row { display:grid; grid-template-columns:1fr 90px 70px 72px; gap:6px; padding:8px 0; border-bottom:1px solid rgba(199,217,240,0.05); align-items:center; }
.m-cell { font-size:11px; color:rgba(255,255,255,0.72); }
.m-cell-dim { font-size:11px; color:rgba(199,217,240,0.38); }
.m-badge { display:inline-block; font-size:10px; padding:2px 7px; border-radius:100px; }
.badge-ok { background:rgba(16,185,129,0.15); color:#34d399; }
.badge-wip { background:rgba(251,191,36,0.15); color:#fbbf24; }

/* FOOTER */
footer { padding:36px 0; background:#080f1d; border-top:1px solid rgba(199,217,240,0.06); }
.footer-inner { max-width:1240px; margin:0 auto; padding:0 48px; display:flex; align-items:center; justify-content:space-between; }
.footer-hierarchy { display:flex; align-items:center; gap:10px; font-size:13px; color:rgba(199,217,240,0.38); }
.footer-sep { color:rgba(199,217,240,0.18); font-size:16px; }
.footer-hl { color:rgba(199,217,240,0.62); }
.footer-copy { font-size:12px; color:rgba(199,217,240,0.22); }

/* SCROLL FADE */
.fade-in { opacity:0; transform:translateY(22px); transition:opacity 0.65s ease,transform 0.65s ease; }
.fade-in.visible { opacity:1; transform:none; }
.fade-in[data-delay="1"]{ transition-delay:0.1s; }
.fade-in[data-delay="2"]{ transition-delay:0.2s; }
.fade-in[data-delay="3"]{ transition-delay:0.3s; }

/* RESPONSIVE */
@media(max-width:900px){
  .nav{ padding:0 24px; } .nav-links{ display:none; }
  .hero-inner{ grid-template-columns:1fr; padding:0 24px; gap:36px; }
  .hero-right{ display:none; }
  .hero-stats{ flex-wrap:wrap; }
  .section-wrap{ padding:0 24px; }
  .features-section,.dashboard-section{ padding:64px 0; }
  .feature-grid{ grid-template-columns:1fr; }
  .footer-inner{ flex-direction:column; gap:10px; padding:0 24px; text-align:center; }
}
</style>
