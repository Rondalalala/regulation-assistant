# 制度助手 (Regulation Assistant)

> 企业制度与流程管理智能助手 — 私有化部署 (Self-Hosted)

把企业的规章制度、审批流程、权责矩阵集中起来，员工通过自然语言提问，AI 助手基于内部制度回答业务问题、推荐流程、跳转原文。

## 特性

- **制度管理** — 上传制度文档（Excel + PDF/Word），自动解析为结构化数据
- **流程管理** — 上传流程清单，按发起人/部门/类别筛选
- **AI 问答** — 基于 RAG（关键词 + 向量混合检索）回答员工提问
- **AI 解析** — 自动识别制度章节、生成 Mermaid 流程图
- **品牌可配置** — 软件名、模块名、企业名都可自定义
- **私有化部署** — 数据完全本地存储，API Key 用户自配，不依赖任何 SaaS

## 快速开始

### 环境要求

- Node.js 18+
- Python 3.10+
- 一份 LLM API Key（兼容 OpenAI 协议即可，如交融、阿里、智谱、火山、自部署 vLLM 等）

### 安装与启动

```bash
# 1. 克隆仓库
git clone https://github.com/Rondalalala/regulation-assistant.git
cd regulation-assistant

# 2. 启动后端（终端 1）
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000

# 3. 启动前端（终端 2）
cd frontend
npm install
npm run dev
```

打开浏览器访问 http://localhost:3000

### 首次配置

1. 进入 **设置页**，填写 LLM API 配置（Base URL、API Key、模型名）
2. 进入 **数据管理页**，上传企业的制度框架清单（Excel）和流程清单（Excel）
3. 点击"AI 解析"自动结构化制度原文 + 生成流程图（约 10-20 分钟，按数据量）
4. 完成后即可在制度管理、流程管理、AI 助手页面使用

## 目录结构

```
regulation-assistant/
├── frontend/         # Vue 3 + Vite SPA
├── backend/          # FastAPI 服务
├── scripts/          # Python 数据处理脚本
├── data/             # 用户数据（不进 Git）
├── docs/             # 模板和文档
├── CLAUDE.md         # 开发规范
└── README.md
```

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | Vue 3 + Vite + Tailwind + Mermaid |
| 后端 | FastAPI + Uvicorn |
| 数据 | JSON 文件存储（无数据库） |
| AI | OpenAI 兼容 API（自带 Key） |
| 检索 | bi-gram 模糊 + 向量语义混合 |

## 数据隐私

- 所有数据存储在本地 `data/` 目录
- API Key 仅保存在浏览器 localStorage
- 不发送数据到任何第三方服务（除你配置的 LLM 服务商）

## License

MIT
