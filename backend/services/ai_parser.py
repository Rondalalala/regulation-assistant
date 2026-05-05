import httpx
import json
import os

DEFAULT_TIMEOUT = 120.0


def _client(base_url: str, api_key: str):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    return httpx.AsyncClient(
        base_url=base_url.rstrip("/"),
        headers=headers,
        timeout=DEFAULT_TIMEOUT,
    )


async def _chat_completion(
    messages: list,
    llm_config: dict,
    model: str | None = None,
    temperature: float = 0.2,
    response_format: dict | None = None,
):
    base_url = llm_config.get("base_url", os.getenv("LLM_BASE_URL", ""))
    api_key = llm_config.get("api_key", os.getenv("LLM_API_KEY", ""))
    m = model or llm_config.get("model", os.getenv("LLM_MODEL", "jiaorong-deepseek-v4-flash"))

    if not base_url or not api_key:
        raise RuntimeError("LLM base_url 或 api_key 未配置")

    payload = {
        "model": m,
        "messages": messages,
        "temperature": temperature,
    }
    if response_format:
        payload["response_format"] = response_format

    async with _client(base_url, api_key) as c:
        r = await c.post("/chat/completions", json=payload)
        r.raise_for_status()
        data = r.json()

    content = data["choices"][0]["message"]["content"]
    return content.strip()


STRUCTURE_PROMPT = """你是一个企业制度文档结构化专家。
请将以下制度原文解析为结构化 JSON，识别章节、条款、段落和表格。

要求：
1. 章节标记为 {"type": "chapter", "text": "第X章 ..."}
2. 条款标记为 {"type": "article", "text": "第X条 ..."}
3. 普通段落标记为 {"type": "para", "text": "..."}
4. 表格标记为 {"type": "table", "rows": [["..."], ...]}
5. 只输出纯 JSON 数组，不要 markdown 代码块，不要其他解释文字

制度原文：
"""


async def parse_structure(text: str, llm_config: dict):
    """调用 AI 解析制度原文为结构化 blocks"""
    if not text or len(text.strip()) < 20:
        return [{"type": "para", "text": text.strip() or "（原文为空）"}]

    # 截断过长文本，避免 token 超限
    truncated = text[:12000]
    messages = [
        {"role": "system", "content": "你是一个企业制度文档结构化专家，只输出 JSON。"},
        {"role": "user", "content": STRUCTURE_PROMPT + truncated},
    ]

    try:
        raw = await _chat_completion(messages, llm_config, temperature=0.1)
        # 清理可能的 markdown 代码块
        if raw.startswith("```"):
            raw = raw.strip("`").strip()
            if raw.lower().startswith("json"):
                raw = raw[4:].strip()
        blocks = json.loads(raw)
        if not isinstance(blocks, list):
            blocks = [blocks]
        # 校验并规范化
        valid = []
        for b in blocks:
            if isinstance(b, dict) and "type" in b and "text" in b:
                valid.append(b)
            elif isinstance(b, dict) and "type" in b and "rows" in b:
                valid.append(b)
        return valid if valid else [{"type": "para", "text": text[:500]}]
    except Exception:
        # 降级：按段落拆分
        return [{"type": "para", "text": p} for p in text.split("\n") if p.strip()]


DIAGRAM_PROMPT = """你是一个企业流程可视化专家。请根据以下制度内容，识别其中的审批流程，并生成 Mermaid flowchart TD 代码。

要求：
1. 使用 flowchart TD 语法
2. 用 subgraph 区分不同组织层级
3. 审批步骤用圆角矩形，会签用圆形，报备用三角形
4. 只输出 Mermaid 代码，不要解释

制度内容：
"""


async def generate_diagram(text: str, llm_config: dict):
    """调用 AI 生成 Mermaid 流程图"""
    if not text or len(text.strip()) < 50:
        return None

    truncated = text[:8000]
    messages = [
        {"role": "system", "content": "你是一个企业流程可视化专家，只输出 Mermaid 代码。"},
        {"role": "user", "content": DIAGRAM_PROMPT + truncated},
    ]

    try:
        raw = await _chat_completion(messages, llm_config, temperature=0.3)
        # 清理可能的 markdown 代码块
        if raw.startswith("```"):
            raw = raw.strip("`").strip()
            if raw.lower().startswith("mermaid"):
                raw = raw[7:].strip()
        if not raw.startswith("flowchart") and not raw.startswith("graph"):
            return None
        return raw
    except Exception:
        return None
