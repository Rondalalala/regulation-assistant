import httpx
import json
import os
import re

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


def _strip_markdown_fence(raw: str) -> str:
    """去掉 ```json ... ``` 之类的 markdown 代码块包裹"""
    raw = raw.strip()
    if raw.startswith("```"):
        # 移除前面的 ``` 或 ```json
        raw = re.sub(r"^```[a-zA-Z]*\n?", "", raw)
        raw = re.sub(r"\n?```\s*$", "", raw)
    return raw.strip()


# ─────────────────────────────────────────────────────────────
# 制度结构化（保留原有功能）
# ─────────────────────────────────────────────────────────────

STRUCTURE_PROMPT = """你是一个企业制度文档结构化专家。
请将以下制度原文解析为结构化 JSON,识别章节、条款、段落和表格。

要求:
1. 章节标记为 {"type": "chapter", "text": "第X章 ..."}
2. 条款标记为 {"type": "article", "text": "第X条 ..."}
3. 普通段落标记为 {"type": "para", "text": "..."}
4. 表格标记为 {"type": "table", "rows": [["..."], ...]}
5. 只输出纯 JSON 数组,不要 markdown 代码块,不要其他解释文字

制度原文:
"""


async def parse_structure(text: str, llm_config: dict):
    """调用 AI 解析制度原文为结构化 blocks"""
    if not text or len(text.strip()) < 20:
        return [{"type": "para", "text": text.strip() or "(原文为空)"}]

    truncated = text[:12000]
    messages = [
        {"role": "system", "content": "你是一个企业制度文档结构化专家,只输出 JSON。"},
        {"role": "user", "content": STRUCTURE_PROMPT + truncated},
    ]

    try:
        raw = await _chat_completion(messages, llm_config, temperature=0.1)
        raw = _strip_markdown_fence(raw)
        blocks = json.loads(raw)
        if not isinstance(blocks, list):
            blocks = [blocks]
        valid = []
        for b in blocks:
            if isinstance(b, dict) and "type" in b and "text" in b:
                valid.append(b)
            elif isinstance(b, dict) and "type" in b and "rows" in b:
                valid.append(b)
        return valid if valid else [{"type": "para", "text": text[:500]}]
    except Exception:
        return [{"type": "para", "text": p} for p in text.split("\n") if p.strip()]


DIAGRAM_PROMPT = """你是一个企业流程可视化专家。请根据以下制度内容,识别其中的审批流程,并生成 Mermaid flowchart TD 代码。

要求:
1. 使用 flowchart TD 语法
2. 用 subgraph 区分不同组织层级
3. 审批步骤用圆角矩形,会签用圆形,报备用三角形
4. 只输出 Mermaid 代码,不要解释

制度内容:
"""


async def generate_diagram(text: str, llm_config: dict):
    """调用 AI 生成 Mermaid 流程图"""
    if not text or len(text.strip()) < 50:
        return None

    truncated = text[:8000]
    messages = [
        {"role": "system", "content": "你是一个企业流程可视化专家,只输出 Mermaid 代码。"},
        {"role": "user", "content": DIAGRAM_PROMPT + truncated},
    ]

    try:
        raw = await _chat_completion(messages, llm_config, temperature=0.3)
        raw = _strip_markdown_fence(raw)
        if raw.lower().startswith("mermaid"):
            raw = raw[7:].strip()
        if not raw.startswith("flowchart") and not raw.startswith("graph"):
            return None
        return raw
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────
# 表格列名/内容静默标准化（用户上传任意格式 → 系统标准格式）
# ─────────────────────────────────────────────────────────────

# 系统标准的"职能大类"参考列表（来自 frontend authorityCategories.js MAJOR_CAT_NAMES）
STANDARD_CATEGORIES = [
    "公司治理", "战略管理", "机构管理", "股权管理", "管理体系", "改革管理",
    "干部管理", "薪酬分配管理", "人才配置与评价管理", "人才培养与发展管理",
    "财务管理", "资产管理", "资金管理", "证券事务管理",
    "科技管理", "供应链与采购管理", "数字化管理",
    "投资业务管理", "生产运营管理", "产品设计管理",
    "招商管理", "产业园运营管理", "项目建设管理", "项目成本管理",
    "安全质量环保监督", "法治建设", "全面风险管理", "审计监督",
    "党建工作", "文化建设", "工会工作", "纪委工作",
    "行政办公", "综合保障",
]


REG_NORMALIZE_PROMPT = """你是企业制度数据治理专家。
我会给你一份用户上传的制度清单(JSON 数组,字段名可能是任意中文/英文),请把它转换成系统标准格式。

【系统标准字段】(必须严格用这些英文 key)
- id: 制度 ID,格式 "{大类序号}-{子项序号}-{制度序号}",例如 "1-1-1"。如用户原文件已有标准 ID 则保留;否则按 module+item 分组后自动生成。
- name: 制度名称
- module: 一级分类(标准值见下方"参考职能大类",优先精确匹配,匹配不上时再用用户原文里的类别词)。返回格式 "{序号} {标准类名}",例如 "1 公司治理"
- item: 二级分类。返回格式 "{大类序号}.{子项序号} {子类名}",例如 "1.1 法人治理"
- dept: 主责部门
- doc_no: 文号 / 制度编号
- status: 状态(默认"施行")

【参考职能大类】(优先映射到这里面的某一个,语义相近就行,不必字面相同)
{categories}

【硬性要求】
1. 输出必须是纯 JSON 数组,不要 markdown 代码块,不要解释文字
2. 数组顺序按 module → item → 制度序号 排序
3. 同一 module 共用同一序号;同一 module 内的不同 item 共用 module 序号但 item 序号递增
4. id 严格遵守 "{a}-{b}-{c}" 格式,a/b/c 都是阿拉伯数字
5. 用户字段缺失时,字段值用空字符串 "",不要写 null

【用户上传的原始数据】
"""


def _clean_module_item(value: str) -> str:
    """去掉 AI 可能加的前缀序号,如 '1 公司治理' → '公司治理', '1.1 法人治理' → '法人治理'"""
    value = str(value or "").strip()
    # module: "1 公司治理" → "公司治理"
    value = re.sub(r"^\d+\s+", "", value)
    # item: "1.1 法人治理" → "法人治理"
    value = re.sub(r"^\d+\.\d+\s+", "", value)
    return value


def _ensure_reg_id_format(rows: list[dict]) -> list[dict]:
    """如果 AI 返回的 id 格式不对(没有 a-b-c),按 module/item 分组重新生成;同时清理 module/item 前缀序号"""
    # 先统一清理 module/item
    cleaned = []
    for r in rows:
        cleaned.append({
            **r,
            "module": _clean_module_item(r.get("module")),
            "item": _clean_module_item(r.get("item")),
        })
    rows = cleaned

    valid = []
    bad = []
    for r in rows:
        rid = str(r.get("id", "")).strip()
        if re.match(r"^\d+-\d+-\d+$", rid):
            valid.append(r)
        else:
            bad.append(r)
    if not bad:
        return rows

    # 按 module → item 重新编号
    module_seq: dict[str, int] = {}
    item_seq: dict[tuple[str, str], int] = {}
    inner_seq: dict[tuple[str, str], int] = {}

    fixed = []
    for r in rows:
        mod = str(r.get("module") or "").strip() or "未分类"
        itm = str(r.get("item") or "").strip() or "未分类"
        if mod not in module_seq:
            module_seq[mod] = len(module_seq) + 1
        a = module_seq[mod]
        if (mod, itm) not in item_seq:
            existing = [k for k in item_seq if k[0] == mod]
            item_seq[(mod, itm)] = len(existing) + 1
        b = item_seq[(mod, itm)]
        inner_seq[(mod, itm)] = inner_seq.get((mod, itm), 0) + 1
        c = inner_seq[(mod, itm)]
        new_id = f"{a}-{b}-{c}"
        fixed.append({**r, "id": new_id})
    return fixed


async def normalize_regulations(rows: list[dict], llm_config: dict) -> list[dict]:
    """
    把用户上传的任意格式制度行,转成系统标准 schema。
    rows: 原始 Excel 解析出来的行(字段名可能是中文/英文,字段集合任意)
    返回:[{"id","name","module","item","dept","doc_no","status"}, ...]
    """
    if not rows:
        return []

    sample = json.dumps(rows, ensure_ascii=False, indent=2)
    if len(sample) > 12000:
        sample = json.dumps(rows[:60], ensure_ascii=False, indent=2)

    cats = "、".join(STANDARD_CATEGORIES)
    prompt = REG_NORMALIZE_PROMPT.replace("{categories}", cats)

    messages = [
        {"role": "system", "content": "你是企业制度数据治理专家,只输出 JSON。"},
        {"role": "user", "content": prompt + sample},
    ]

    raw = await _chat_completion(messages, llm_config, temperature=0.1)
    raw = _strip_markdown_fence(raw)
    parsed = json.loads(raw)
    if not isinstance(parsed, list):
        parsed = [parsed] if isinstance(parsed, dict) else []

    fields = ("id", "name", "module", "item", "dept", "doc_no", "status")
    cleaned = []
    for r in parsed:
        if not isinstance(r, dict):
            continue
        out = {f: ("" if r.get(f) is None else str(r.get(f, "")).strip()) for f in fields}
        if not out["name"]:
            continue
        if not out["status"]:
            out["status"] = "施行"
        cleaned.append(out)

    return _ensure_reg_id_format(cleaned)


AUTH_NORMALIZE_PROMPT = """你是企业流程数据治理专家。
我会给你一份用户上传的"业务流程 / 审批清单"(JSON 数组,字段名可能是任意中文/英文),请把它转换成系统标准格式。

【系统标准字段】(必须严格用这些英文 key)
- key: 流程编号,例如 "A001"。用户原编号若是字母+数字格式则保留;若不是,按 category 给字母前缀(治理类→A、人力→B、财务→C、采购→D、合规→E、监督→F、信息→G、行政→H 等),后接三位序号
- name: 流程名称
- category: 业务大类(用户原文里的中文类别,例如"人力资源""财务管理")
- system: 关联制度(用户提供的"关联制度"字段,或留空)
- initiator: 发起人
- final_approver: 最终审批人
- flow: 审批流程数组,把"A→B→C"这类文本拆成对象数组,每个对象含:
   - role: 该步骤的岗位/部门(取最具体的描述)
   - org: 所在组织(部门或公司层级,可与 role 相同)
   - step: 该步骤的动作描述。第一个用"发起申请",最后一个用"终审批准",中间用"审核审批"或"会签审核";如果原文里写"会签",把那一步的 step 设为"会签"且 type 设为"countersign";如果原文里写"报备",step 设为"报备"且 type 设为"report"
   - is_final: 布尔,只有最后一步为 true,其余 false
   - type: 可选,值为 "countersign" / "report",其它情况不要这个字段

【硬性要求】
1. 输出必须是纯 JSON 数组,不要 markdown 代码块,不要解释文字
2. flow 数组的 step 顺序必须和用户原文 "A→B→C" 顺序一致
3. 用户字段缺失时,字符串字段用空字符串 "",flow 用空数组 []
4. 同一 category 内的 key 序号递增;不同 category 之间字母前缀不同

【用户上传的原始数据】
"""


def _normalize_flow_steps(steps_in) -> list[dict]:
    """容错:即便 AI 给了不规范的 flow,也强制每步都有 role/org/step/is_final"""
    if not isinstance(steps_in, list) or not steps_in:
        return []
    out = []
    for i, s in enumerate(steps_in):
        if not isinstance(s, dict):
            s = {"role": str(s), "org": str(s)}
        role = str(s.get("role") or s.get("org") or "").strip()
        org = str(s.get("org") or s.get("role") or "").strip()
        step = str(s.get("step") or "").strip()
        if not step:
            if i == 0:
                step = "发起申请"
            elif i == len(steps_in) - 1:
                step = "终审批准"
            else:
                step = "审核审批"
        item = {
            "role": role,
            "org": org,
            "step": step,
            "is_final": bool(s.get("is_final") or i == len(steps_in) - 1),
        }
        t = s.get("type")
        if t in ("countersign", "report"):
            item["type"] = t
        out.append(item)
    # 只保留最后一个 is_final=true,其余强制 false
    last_idx = len(out) - 1
    for i, st in enumerate(out):
        st["is_final"] = (i == last_idx)
    return out


async def normalize_authority(rows: list[dict], llm_config: dict) -> list[dict]:
    """
    把用户上传的任意格式流程行,转成系统标准 schema。
    rows: 原始 Excel 解析出来的行
    返回:[{"key","name","category","system","initiator","final_approver","flow":[...]}, ...]
    """
    if not rows:
        return []

    sample = json.dumps(rows, ensure_ascii=False, indent=2)
    if len(sample) > 12000:
        sample = json.dumps(rows[:60], ensure_ascii=False, indent=2)

    messages = [
        {"role": "system", "content": "你是企业流程数据治理专家,只输出 JSON。"},
        {"role": "user", "content": AUTH_NORMALIZE_PROMPT + sample},
    ]

    raw = await _chat_completion(messages, llm_config, temperature=0.1)
    raw = _strip_markdown_fence(raw)
    parsed = json.loads(raw)
    if not isinstance(parsed, list):
        parsed = [parsed] if isinstance(parsed, dict) else []

    cleaned = []
    for r in parsed:
        if not isinstance(r, dict):
            continue
        out = {
            "key": str(r.get("key", "")).strip(),
            "name": str(r.get("name", "")).strip(),
            "category": str(r.get("category", "")).strip(),
            "system": str(r.get("system", "")).strip(),
            "initiator": str(r.get("initiator", "")).strip(),
            "final_approver": str(r.get("final_approver", "")).strip(),
            "flow": _normalize_flow_steps(r.get("flow")),
        }
        if not out["name"]:
            continue
        cleaned.append(out)

    # 确保 key 不重复且非空
    seen_keys = set()
    counter = 1
    for r in cleaned:
        k = r["key"]
        if not k or k in seen_keys:
            r["key"] = f"X{counter:03d}"
            counter += 1
        seen_keys.add(r["key"])

    return cleaned
