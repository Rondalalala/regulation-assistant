import { reactive } from 'vue'

const STORAGE_KEY = 'enterprise-settings'

const defaults = {
  appName: '制度助手',
  regModuleName: '制度管理',
  flowModuleName: '流程管理',
  companyName: '',
}

function load() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? { ...defaults, ...JSON.parse(raw) } : { ...defaults }
  } catch { return { ...defaults } }
}

const state = reactive(load())

function save() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
}

export function useEnterprise() {
  return {
    settings: state,
    setAppName(v) { state.appName = v; save() },
    setRegModuleName(v) { state.regModuleName = v; save() },
    setFlowModuleName(v) { state.flowModuleName = v; save() },
    setCompanyName(v) { state.companyName = v; save() },
  }
}
