// 临时占位文件 — Phase 3 将替换为 API 异步加载
// 这里只导出 demo 数据，保证项目能编译运行

import regulations from '../../../data/regulations.json'
import authority from '../../../data/authority.json'
import authorityMapping from '../../../data/authority_mapping.json'

const texts = {}
const diagrams = {}
const embeddings = []

export { regulations, authority, authorityMapping, texts, diagrams, embeddings }
