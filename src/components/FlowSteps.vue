<template>
  <div class="flow-steps">
    <template v-for="(seg, si) in segments" :key="si">
      <!-- 段间箭头 -->
      <div v-if="si > 0" class="flow-arr"></div>

      <!-- 并行会签组 -->
      <div v-if="seg.type === 'parallel'" class="flow-parallel">
        <div class="flow-parallel-label">并行会签</div>
        <div class="flow-parallel-body">
          <div v-for="(s, i) in seg.steps" :key="i" class="flow-node">
            <div class="flow-circle fc-countersign">○</div>
            <div class="flow-name" v-html="hl(s.role) || '—'"></div>
            <div class="flow-org">{{ s.org }}</div>
          </div>
        </div>
      </div>

      <!-- 报备组 -->
      <div v-else-if="seg.type === 'report_group'" class="flow-parallel flow-report-group">
        <div class="flow-parallel-label" style="color:var(--muted);border-color:var(--border)">报备</div>
        <div class="flow-parallel-body">
          <div v-for="(s, i) in seg.steps" :key="i" class="flow-node">
            <div class="flow-circle fc-report">△</div>
            <div class="flow-name" v-html="hl(s.role) || '—'"></div>
            <div class="flow-org">{{ s.org }}</div>
          </div>
        </div>
      </div>

      <!-- 单步：审核或最终审批 -->
      <div v-else class="flow-node">
        <div class="flow-circle" :class="seg.step.is_final ? 'fc-final' : 'fc-review'">
          <span :class="{ 'final-mark': seg.step.is_final }">{{ seg.step.step }}</span>
        </div>
        <div class="flow-name" v-html="hl(seg.step.role) || '—'"></div>
        <div class="flow-org">{{ seg.step.org }}</div>
      </div>
    </template>

    <div v-if="!segments.length" class="flow-empty">暂无流程数据</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  flow: { type: Array, default: () => [] },
  highlightQuery: { type: String, default: '' }
})

function hl(text) {
  if (!props.highlightQuery.trim() || !text) return text || ''
  const kw = props.highlightQuery.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return text.replace(new RegExp(`(${kw})`, 'gi'), '<mark>$1</mark>')
}

const segments = computed(() => {
  const result = []
  let i = 0
  while (i < props.flow.length) {
    const s = props.flow[i]
    if (s.type === 'countersign') {
      const group = []
      while (i < props.flow.length && props.flow[i].type === 'countersign') {
        group.push(props.flow[i++])
      }
      result.push({ type: 'parallel', steps: group })
    } else if (s.type === 'report') {
      const group = []
      while (i < props.flow.length && props.flow[i].type === 'report') {
        group.push(props.flow[i++])
      }
      result.push({ type: 'report_group', steps: group })
    } else {
      result.push({ type: 'single', step: props.flow[i++] })
    }
  }
  return result
})
</script>

<style scoped>
.flow-steps {
  display: flex;
  align-items: flex-start;
  overflow-x: auto;
  padding: 6px 0 10px;
  gap: 0;
}

/* 箭头连接 */
.flow-arr {
  width: 28px;
  height: 2px;
  background: #93C5FD;
  position: relative;
  flex-shrink: 0;
  margin-top: 19px; /* 对齐圆圈中心: circle_h/2 = 38/2 */
}
.flow-arr::after {
  content: '';
  position: absolute;
  right: -1px; top: -4px;
  border: 4px solid transparent;
  border-left: 7px solid #93C5FD;
}

/* 单步节点 */
.flow-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  flex-shrink: 0;
  width: 72px;
}

.flow-circle {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  border: 2px solid transparent;
  flex-shrink: 0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

/* 审核步骤：蓝色 */
.fc-review {
  background: #EFF6FF;
  color: #1d4ed8;
  border-color: var(--blue);
  box-shadow: 0 0 0 3px rgba(37,99,235,0.1);
}

/* 最终审批：绿色，数字加下划线 */
.fc-final {
  background: var(--success-bg);
  color: var(--success);
  border-color: var(--success);
  box-shadow: 0 0 0 3px rgba(22,163,74,0.1);
}
.final-mark {
  text-decoration: underline;
  font-weight: 800;
}

/* 会签：橙色 */
.fc-countersign {
  background: #FFF7ED;
  color: #C2410C;
  border-color: rgba(251,146,60,0.4);
  font-size: 14px;
}

/* 报备：灰色 */
.fc-report {
  background: var(--bg);
  color: var(--muted);
  border-color: var(--subtle);
  font-size: 13px;
}

.flow-name {
  font-size: 11px;
  color: var(--fg);
  text-align: center;
  line-height: 1.3;
  max-width: 72px;
  word-break: break-all;
}
.flow-org {
  font-size: 10px;
  color: var(--muted);
  text-align: center;
  max-width: 72px;
  line-height: 1.2;
}

/* 并行会签 / 报备 组 */
.flow-parallel {
  border: 1.5px dashed rgba(251,146,60,0.4);
  border-radius: 10px;
  padding: 6px 10px 8px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.flow-report-group {
  border-color: var(--subtle);
}

.flow-parallel-label {
  font-size: 9px;
  font-weight: 600;
  color: #C2410C;
  letter-spacing: 0.05em;
  border-bottom: 1px solid rgba(251,146,60,0.4);
  padding-bottom: 4px;
  width: 100%;
  text-align: center;
}

.flow-parallel-body {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.flow-empty {
  font-size: 12px;
  color: var(--subtle);
  font-style: italic;
}

:deep(mark) {
  background: #FEF08A;
  color: #713F12;
  border-radius: 2px;
  padding: 0;
  font-style: normal;
}
</style>
