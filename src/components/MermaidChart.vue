<template>
  <div class="mermaid-wrap">
    <div class="mermaid-header">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="3" y="3" width="18" height="18" rx="2"/>
        <path d="M3 9h18M9 21V9"/>
      </svg>
      {{ title }}
    </div>
    <div ref="el" class="mermaid-body"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import mermaid from 'mermaid'

mermaid.initialize({
  startOnLoad: false,
  theme: 'base',
  themeVariables: {
    primaryColor:         '#FFFFFF',
    primaryTextColor:     '#1E3A5F',
    primaryBorderColor:   'rgba(37,99,235,0.3)',
    secondaryColor:       '#EFF6FF',
    secondaryTextColor:   '#1d4ed8',
    secondaryBorderColor: 'rgba(37,99,235,0.2)',
    tertiaryColor:        '#F0FDF4',
    tertiaryTextColor:    '#16A34A',
    tertiaryBorderColor:  'rgba(22,163,74,0.3)',
    lineColor:            '#93C5FD',
    clusterBkg:           'rgba(37,99,235,0.04)',
    clusterBorder:        'rgba(37,99,235,0.15)',
    titleColor:           '#1E3A5F',
    edgeLabelBackground:  '#EFF6FF',
    fontFamily: '"PingFang SC","Noto Sans SC","Microsoft YaHei",system-ui,sans-serif',
    fontSize:   '13px',
  },
  flowchart: { htmlLabels: true, curve: 'basis', padding: 20 },
})

const props = defineProps({ title: String, code: String })
const el = ref(null)

async function render() {
  if (!el.value || !props.code) return
  el.value.innerHTML = ''
  try {
    const id = 'mm-' + Math.random().toString(36).slice(2)
    const { svg } = await mermaid.render(id, props.code)
    el.value.innerHTML = svg
  } catch (e) {
    el.value.innerHTML = `<p class="mm-err">图表渲染失败：${e.message}</p>`
  }
}

onMounted(render)
watch(() => props.code, render)
</script>

<style scoped>
.mermaid-wrap {
  background: var(--surface);
  border: 1px solid var(--blue-border);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--blue-glow);
  position: relative;
}
.mermaid-wrap::before {
  content: '';
  display: block;
  height: 3px;
  background: linear-gradient(90deg, var(--blue) 0%, var(--blue-light) 100%);
}

.mermaid-header {
  display: flex; align-items: center; gap: 8px;
  padding: 11px 18px;
  font-size: 13px; font-weight: 600; color: var(--navy);
  border-bottom: 1px solid var(--blue-border);
  background: var(--accent-soft);
}

.mermaid-body {
  padding: 28px 24px;
  display: flex; justify-content: center;
  overflow-x: auto;
  background: var(--surface);
}

.mermaid-body :deep(svg) {
  background: transparent !important;
  max-width: 100%;
  height: auto;
}

.mermaid-body :deep(.node rect),
.mermaid-body :deep(.node circle),
.mermaid-body :deep(.node polygon),
.mermaid-body :deep(.node path) {
  filter: drop-shadow(0 2px 6px rgba(37,99,235,0.1));
}

.mermaid-body :deep(.cluster rect) {
  rx: 8 !important; ry: 8 !important;
}

.mm-err { color: var(--danger); font-size: 12px; padding: 12px 0; }
</style>
