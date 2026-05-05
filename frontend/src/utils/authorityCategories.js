// 权责大类代码 → 中文名称
export const MAJOR_CAT_NAMES = {
  A: '公司治理', B: '战略管理', C: '机构管理', D: '股权管理', E: '管理体系', F: '改革管理',
  G: '干部管理', H: '薪酬分配管理', I: '人才配置与评价管理', J: '人才培养与发展管理',
  K: '财务管理', L: '资产管理', M: '资金管理', N: '证券事务管理',
  O: '科技管理', P: '供应链与采购管理', Q: '数字化管理',
  R: '投资业务管理', S: '生产运营管理', T: '产品设计管理',
  U: '招商管理', V: '产业园运营管理', W: '项目建设管理', X: '项目成本管理',
  Y: '安全质量环保监督', Z: '法治建设', AA: '全面风险管理', AB: '审计监督',
  AC: '党建工作', AD: '文化建设', AE: '工会工作', AF: '纪委工作',
  AG: '行政办公', AH: '综合保障',
}

// 7个职能域分组
export const DOMAINS = [
  {
    id: 'governance', label: '公司治理', desc: '治理·战略·机构·股权',
    color: '#1E3A5F', bg: '#EBF2FF', border: '#C7D9F0',
    darkColor: '#60a5fa', darkBg: 'rgba(96,165,250,0.07)', darkBorder: 'rgba(96,165,250,0.17)',
    cats: ['A', 'B', 'C', 'D', 'E', 'F'],
  },
  {
    id: 'hr', label: '人力薪酬', desc: '干部·薪酬·人才培养',
    color: '#0284C7', bg: '#F0F9FF', border: '#BAE6FD',
    darkColor: '#38bdf8', darkBg: 'rgba(56,189,248,0.07)', darkBorder: 'rgba(56,189,248,0.17)',
    cats: ['G', 'H', 'I', 'J'],
  },
  {
    id: 'finance', label: '财务资产', desc: '财务·资产·资金·证券',
    color: '#16A34A', bg: '#F0FDF4', border: '#BBF7D0',
    darkColor: '#34d399', darkBg: 'rgba(52,211,153,0.07)', darkBorder: 'rgba(52,211,153,0.17)',
    cats: ['K', 'L', 'M', 'N'],
  },
  {
    id: 'operations', label: '业务运营', desc: '投资·生产·招商·运营',
    color: '#7C3AED', bg: '#F5F3FF', border: '#DDD6FE',
    darkColor: '#a78bfa', darkBg: 'rgba(167,139,250,0.07)', darkBorder: 'rgba(167,139,250,0.17)',
    cats: ['R', 'S', 'T', 'U', 'V', 'W', 'X'],
  },
  {
    id: 'tech', label: '科技采购', desc: '科技·供应链·数字化',
    color: '#0891B2', bg: '#ECFEFF', border: '#A5F3FC',
    darkColor: '#22d3ee', darkBg: 'rgba(34,211,238,0.07)', darkBorder: 'rgba(34,211,238,0.17)',
    cats: ['O', 'P', 'Q'],
  },
  {
    id: 'compliance', label: '合规监督', desc: '安全·法治·风险·审计',
    color: '#DC2626', bg: '#FEF2F2', border: '#FECACA',
    darkColor: '#f87171', darkBg: 'rgba(248,113,113,0.07)', darkBorder: 'rgba(248,113,113,0.17)',
    cats: ['Y', 'Z', 'AA', 'AB'],
  },
  {
    id: 'party', label: '党建行政', desc: '党建·文化·工会·行政',
    color: '#B45309', bg: '#FFFBEB', border: '#FDE68A',
    darkColor: '#fbbf24', darkBg: 'rgba(251,191,36,0.07)', darkBorder: 'rgba(251,191,36,0.17)',
    cats: ['AC', 'AD', 'AE', 'AF', 'AG', 'AH'],
  },
]

// 从 key 字段提取大类代码（如 *A101 → 'A'，AB201 → 'AB'）
export function getMajorCat(key) {
  const clean = String(key || '').replace(/^\*/, '')
  const match = clean.match(/^([A-Z]+)\d+/)
  return match ? match[1] : ''
}

// 根据 key 找到所属职能域
export function getDomainByKey(key) {
  const cat = getMajorCat(key)
  return DOMAINS.find(d => d.cats.includes(cat)) || null
}

// 模块中文名 → 大类字母（反向映射）
export const MODULE_NAME_TO_CAT = Object.fromEntries(
  Object.entries(MAJOR_CAT_NAMES).map(([k, v]) => [v, k])
)

// 根据模块中文名称找到所属职能域
export function getDomainByModuleName(name) {
  const cat = MODULE_NAME_TO_CAT[name]
  return cat ? DOMAINS.find(d => d.cats.includes(cat)) : null
}
