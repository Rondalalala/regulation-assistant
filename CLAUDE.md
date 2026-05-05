# 制度助手 (通用版) — CLAUDE.md

## 项目定位
企业制度与流程管理智能助手的**通用版**（私有化部署），从内部版"西北投资制度助理"演化而来。**禁止**写入任何"西北投资"特定的品牌文案、内部数据、PDF/Excel 原始文件。所有品牌文案通过 `useEnterprise.js` 配置化。

## 与内部版的差异
| 维度 | 内部版（制度助理） | 通用版（regulation-assistant） |
|------|------------------|------------------------------|
| 部署 | Electron 打包 + 数据预编译 | 本地起 FastAPI + Vite，浏览器访问 |
| 数据 | bundle.js 静态导入 | API 异步加载 |
| 品牌 | 硬编码"西北投资"等 | 配置化（appName / regModuleName / flowModuleName / companyName）|
| 数据来源 | 内部 Excel/PDF 预处理 | 用户上传 Excel/PDF，后端解析 |
| AI 解析 | 离线脚本 | 后台任务 + 进度轮询 |

## 目录结构（生效后）
```
regulation-assistant/
├── frontend/         # Vue 3 + Vite SPA
│   ├── src/
│   │   ├── composables/   # 包括 useEnterprise.js (新增)
│   │   ├── views/         # 包括 DataManagerView.vue (新增)
│   │   └── data/api.js    # 改为 fetch /api/*
│   └── vite.config.js     # 配 /api 代理到 :8000
├── backend/          # FastAPI
│   ├── app.py
│   ├── routers/      # regulations / search / upload / parse
│   └── services/     # data_store / ai_parser / task_manager
├── scripts/          # Python 解析（保留）
├── data/             # 用户数据（不进 Git）
└── docs/             # 模板 + 安装指南
```

## 命名约定（默认值，全部可在前端设置页修改）
- `appName` = "制度助手"
- `regModuleName` = "制度管理"（不要再叫"制度库""规章制度"）
- `flowModuleName` = "流程管理"（不要再叫"权责清单"）
- `companyName` = ""（用户自填）

## 开发纪律
- 前端任何字符串里出现"西北投资""中交"立即视为 bug
- system prompt 用模板拼接 `companyName`，不写死
- 数据接口不直接读 bundle.js，统一走 fetch `/api/*`
- API Key 留在浏览器 localStorage，**绝不**写到后端 / 不进日志
- 前端发请求时通过 `X-Api-Base` Header 告诉后端代理目标，避免后端硬编码 LLM 地址

## 验证命令
```bash
# 后端
cd backend && uvicorn app:app --reload --port 8000

# 前端
cd frontend && npm run dev
# → http://localhost:3000

# 健康检查
curl http://localhost:8000/api/health
```

## 红线
- 删除 `data/` 必须先问用户
- 修改 `.env`、API Key 必须先问用户
- `git push` / `gh repo` 操作必须先问用户
- 安装新的全局依赖必须先问用户
