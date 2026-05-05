# API 契约 (v1)

> 前后端约定的 HTTP 接口规格。**修改此文档需前后端同步更新**。
>
> 所有路径均以 `/api` 开头，前端通过 Vite 代理转发到 `http://localhost:8000`。
> 所有响应都是 JSON，编码 UTF-8。

## 通用约定

- 时间戳：ISO 8601 字符串（如 `"2026-05-05T12:34:56Z"`）
- 错误响应：HTTP 4xx/5xx + `{"detail": "错误描述"}`
- 上传：`multipart/form-data`，字段名 `file`

---

## 1. 健康检查

### `GET /api/health`

**Response 200**:
```json
{ "status": "ok", "version": "1.0.0" }
```

---

## 2. 制度管理

### `GET /api/regulations`

返回所有制度索引（不含原文，体积小，可一次加载）。

**Response 200**:
```json
[
  {
    "id": "5-2-1",
    "name": "采购管理办法",
    "module": "5 业务管理类",
    "item": "5.2 采购管理",
    "dept": "采购管理部",
    "doc_no": "示例-2024-002"
  }
]
```

### `GET /api/regulations/{id}`

返回单条制度的元数据。

**Response 200**: 同上单条对象。
**Response 404**: 找不到。

### `GET /api/regulations/{id}/text`

返回制度原文（结构化）。

**Response 200**:
```json
{
  "id": "5-2-1",
  "text": "全文文本...",
  "blocks": [
    { "type": "chapter",  "text": "第一章 总则" },
    { "type": "article",  "text": "第一条 ..." },
    { "type": "para",     "text": "段落内容..." },
    { "type": "table",    "rows": [["列1","列2"], ["..."]] }
  ]
}
```

**Response 404**: 该制度尚未上传原文。

### `GET /api/regulations/{id}/diagrams`

返回该制度对应的 Mermaid 流程图。

**Response 200**:
```json
{
  "id": "5-2-1",
  "charts": [
    { "title": "采购审批流程", "mermaid": "flowchart TD\n  A-->B\n  ..." }
  ]
}
```

**Response 404**: 没有流程图。

### `GET /api/regulations/authority-mapping`

返回制度 ID → 流程 key 列表的映射（用于详情页展示相关流程）。

**Response 200**:
```json
{ "5-2-1": ["K001", "K002"], "...": [] }
```

---

## 3. 流程管理（原"权责清单"）

### `GET /api/authority`

返回所有流程事项。

**Response 200**:
```json
[
  {
    "key": "K001",
    "name": "采购合同审批",
    "category": "业务管理",
    "system": "5 业务管理类",
    "initiator": "业务部门",
    "final_approver": "总经理",
    "flow": [
      { "role": "业务部门", "step": "发起申请" },
      { "role": "采购管理部", "step": "审核合同条款" }
    ]
  }
]
```

---

## 4. 搜索

### `GET /api/search?q=<query>&limit=<n>`

混合检索（关键词 + 向量）。

**Response 200**:
```json
{
  "regulations": [
    { "id": "5-2-1", "name": "...", "score": 0.92, "snippet": "..." }
  ],
  "authority": [
    { "key": "K001", "name": "...", "score": 0.88 }
  ]
}
```

---

## 5. 文件上传

### `POST /api/upload/regulations-excel`

上传制度框架清单 Excel，返回解析预览（不直接保存）。

**Request**: `multipart/form-data`, field `file` = `.xlsx` / `.csv`

**Response 200**:
```json
{
  "preview": [
    { "id": "1-1-1", "name": "公司章程", "module": "...", "item": "...", "dept": "..." }
  ],
  "total_rows": 258,
  "preview_count": 5,
  "warnings": []
}
```

### `POST /api/upload/authority-excel`

上传流程清单 Excel，返回解析预览。

**Response 200**: 同上结构，`preview` 元素是 `authority` 对象。

### `POST /api/upload/regulation-pdf?reg_id=<id>`

上传制度原文 PDF/DOCX，提取文本预览。

**Request**: `multipart/form-data`, field `file` = `.pdf` / `.docx`

**Response 200**:
```json
{
  "reg_id": "5-2-1",
  "text_preview": "前 1000 字...",
  "text_length": 25430,
  "warnings": []
}
```

### `POST /api/upload/confirm-regulations`

确认导入制度索引（覆盖现有 `regulations.json`）。

**Request body**:
```json
{ "data": [ ...制度对象数组... ] }
```

**Response 200**: `{ "saved": true, "count": 258 }`

### `POST /api/upload/confirm-authority`

同上，针对流程数据。

### `POST /api/upload/confirm-pdf`

确认导入制度原文（写入 `data/texts/{id}.json`）。

**Request body**:
```json
{ "reg_id": "5-2-1", "text": "完整文本", "blocks": [...] }
```

---

## 6. AI 解析（异步任务）

### `POST /api/parse/start`

启动 AI 解析任务，后端在后台处理。

**Request body**:
```json
{
  "scope": "all",
  "tasks": ["structure", "diagrams"],
  "llm_config": {
    "base_url": "https://...",
    "api_key": "sk-...",
    "model": "..."
  }
}
```

`scope`: `"all"` 或 `["reg-id-1", "reg-id-2"]`

**Response 200**:
```json
{ "task_id": "uuid-xxx", "total": 200, "status": "running" }
```

### `GET /api/parse/progress/{task_id}`

**Response 200**:
```json
{
  "task_id": "uuid-xxx",
  "status": "running|completed|failed",
  "progress": 45,
  "total": 200,
  "current_item": "5-2-1",
  "error": null,
  "started_at": "...",
  "elapsed_seconds": 120
}
```

### `GET /api/parse/result/{task_id}`

**Response 200**: 任务完成后返回解析结果（结构化制度 + 流程图）。

### `POST /api/parse/save/{task_id}`

确认保存解析结果到 `data/texts/` 和 `data/diagrams/`。

**Response 200**: `{ "saved": true }`

---

## 7. 设置（可选，主要在前端 localStorage）

### `GET /api/config`

返回服务端配置（数据目录路径、当前数据量等只读信息）。

**Response 200**:
```json
{
  "data_dir": "/path/to/data",
  "regulations_count": 258,
  "authority_count": 145,
  "texts_count": 230,
  "diagrams_count": 200,
  "last_modified": "2026-05-05T12:34:56Z"
}
```

---

## 8. LLM 代理（仅供前端代理调用，避免 CORS）

### `POST /api/llm-proxy/chat/completions`
### `POST /api/llm-proxy/embeddings`

**透明转发**到前端在请求头 `X-Api-Base` 指定的目标 URL。

**Request Headers**:
- `X-Api-Base: https://c4ai.ccccltd.cn/api/compatible/v1`
- `Authorization: Bearer <user-api-key>`
- `Content-Type: application/json`

**Response**: 原样转发上游响应。

---

## 错误码

| HTTP | 含义 | 示例 |
|------|------|------|
| 400 | 请求参数错误 | 上传文件格式不对 |
| 404 | 资源不存在 | 制度 ID 找不到 |
| 413 | 文件过大 | PDF > 50 MB |
| 422 | 数据格式错误 | Excel 列名不匹配 |
| 500 | 服务器错误 | AI 解析失败 |

---

## 前端调用约定

- 所有 fetch 路径用相对路径 `/api/*`，由 Vite 代理转发
- LLM 调用通过 `/api/llm-proxy/*` 转发，凭 `X-Api-Base` Header 决定上游
- 数据加载支持缓存：列表数据缓存到内存，详情按需加载
- 上传带进度（`onUploadProgress`），AI 解析用轮询（2 秒/次）

## 后端实现约定

- 数据存储：`data/*.json` 文件，纯 JSON，UTF-8
- 后台任务：FastAPI `BackgroundTasks` + 内存 dict 存进度
- AI 解析使用前端传来的 `llm_config`，不在后端硬编码 API Key
- 文件上传使用 `python-multipart`，单文件最大 50 MB
- Excel 解析：`openpyxl`，PDF 解析：`pdfplumber`
