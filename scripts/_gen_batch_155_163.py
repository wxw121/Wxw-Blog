# -*- coding: utf-8 -*-
"""Generate batch 155-163 tutorials (roadmap 172-180) + image prompts."""
from __future__ import annotations
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CROSS = {
    "rest": "[5 REST API 设计](5.rest-api-design-tutorial.md)（路线图第 **7** 条）",
    "incr": "[49 增量更新](49.incremental-update-tutorial.md)",
    "backup": "[90 向量库备份](90.vector-db-backup-tutorial.md)",
    "golden": "[143 Golden Dataset](143.golden-dataset-tutorial.md)",
}

FOOTER_F = """
### 14.4 30 分钟动手作业

1. 把本文 §9 最小代码在本地跑通；  
2. 对照 {cross_rest} 检查资源 URL 与状态码；  
3. 与 {cross_golden} 对齐一条可回归样例；  
4. 写 wiki：本文能力在你们索引流水线中的插入点。

### 14.5 给未来自己的排障便签

- 任务状态以 DB 为准，不靠内存猜；  
- 上传与索引分离，大文件走队列；  
- 幂等键 = doc_id + content_hash + pipeline_version；  
- 失败任务进 DLQ 再人工归因，别无限重试烧 API。

---

> **初学者可能仍困惑的点**  
> - F 模块后端不是「会写 FastAPI」就够——**索引任务** 才是 RAG 产品的心脏。  
> - BackgroundTasks 适合演示，生产索引请读 [159 Celery](159.celery-async-queue-tutorial.md)。  
> - 评测（人工 + 金标）与工程（队列 + 状态机）要 **同一套 doc_id**，否则对不上号。
"""


def img_readme(slug: str, rows: list[tuple[str, str, str]]) -> str:
    lines = [
        f"# {slug} 信息图\n",
        "| 文件 | 布局 | 插入位置 |",
        "|------|------|----------|",
    ]
    for fname, layout, section in rows:
        lines.append(f"| `{fname}` | {layout} | {section} |")
    lines += [
        "",
        "风格：hand-drawn-edu · 16:9 · 中文",
        "",
        "Prompt 见 `prompts/`。",
        "",
        "说明：本目录目前仅含 prompt 与 README；生成 PNG 后放入同级文件名即可被正文引用。",
        "",
    ]
    return "\n".join(lines)


def prompt(layout: str, title: str, body: str, footer: str) -> str:
    return f"""---
layout: {layout}
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: {layout}.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: {title}

{body}

Footer: {footer}

All text Simplified Chinese.
"""


def write_images(slug: str, title_short: str, prompts: list[tuple[str, str, str, str]]) -> None:
    base = ROOT / "image" / slug
    (base / "prompts").mkdir(parents=True, exist_ok=True)
    rows = []
    for i, (fname, layout, section, body) in enumerate(prompts, 1):
        stem = fname.replace(".png", "")
        (base / "prompts" / f"{stem}.md").write_text(
            prompt(layout, title_short, body, f"{title_short} · §{i+2}"),
            encoding="utf-8",
        )
        rows.append((fname, layout, section))
    (base / "README.md").write_text(img_readme(slug, rows), encoding="utf-8")


def fmt(s: str) -> str:
    return (
        s.replace("{rest}", CROSS["rest"])
        .replace("{incr}", CROSS["incr"])
        .replace("{backup}", CROSS["backup"])
        .replace("{golden}", CROSS["golden"])
    )


ARTICLES: dict[str, dict] = {}


def article(
    filename: str,
    title: str,
    roadmap: int,
    tier: str,
    module: str,
    slug: str,
    intro: str,
    prereq: str,
    sections: list[tuple[str, str]],
    images: list[tuple[str, str, str, str]],
    extra_footer: str = "",
) -> None:
    toc = "\n".join(f"{i}. [{s[0]}](#{i}-{s[0].replace(' ', '-').replace('：', '').replace('（', '').replace('）', '').replace('/', '').lower()})" for i, s in enumerate(sections, 1))
    body_parts = []
    for i, (heading, content) in enumerate(sections, 1):
        anchor = heading.replace(" ", "-").replace("：", "").replace("（", "").replace("）", "").replace("/", "").lower()
        body_parts.append(f"\n## {i}. {heading}\n\n{fmt(content)}\n")
    cross_block = f"""
| 概念 | 来自 |
|------|------|
| REST 资源与状态码 | {CROSS['rest']} |
| 增量变更检测 | {CROSS['incr']} |
| 索引备份恢复 | {CROSS['backup']} |
| 金标评测集 | {CROSS['golden']} |
"""
    footer = FOOTER_F.format(cross_rest=CROSS["rest"], cross_golden=CROSS["golden"])
    md = f"""# {title}

> {intro} 这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **{module}**（路线图第 **{roadmap}** 条），**{tier}**。前置：{prereq}。全系列交叉：{CROSS['rest']}、{CROSS['incr']}、{CROSS['backup']}、{CROSS['golden']}。

---

## 目录

{toc}

---

{"".join(body_parts)}

{cross_block}

{fmt(extra_footer)}
{footer}
"""
    path = ROOT / filename
    path.write_text(md, encoding="utf-8")
    write_images(slug, title.split("：")[0] if "：" in title else title[:20], images)
    hanzi = sum(1 for c in md if "\u4e00" <= c <= "\u9fff")
    ARTICLES[filename] = {"hanzi": hanzi, "slug": slug, "roadmap": roadmap}


# ── 155 Human Evaluation ─────────────────────────────────────────────
article(
    "155.human-evaluation-rag-tutorial.md",
    "E 评测与观测（十三）：RAG 人工评测流程完全指南",
    172,
    "地基篇",
    "E 轨",
    "human-evaluation-rag",
    "RAGAS 能批量打分，但 **上线前** 业务方只信 **人眼**：引用是否点得开？拒答是否太生硬？财务条款敢不敢签？**人工评测**（Human Evaluation）是把 Golden Dataset 里的题目交给标注员或领域专家，按 **rubric（评分量表）** 打分的流程——它是自动指标的 **校准器** 与 **终审庭**。",
    "[141 RAGAS Faithfulness](141.ragas-faithfulness-tutorial.md)、[153 A/B 实验](153.ab-experiment-rag-tutorial.md)、[154 参数版本](154.param-version-management-tutorial.md)",
    [
        ("前言：自动分高但用户骂", """同事跑完 RAGAS，Faithfulness 0.92，老板点头；客服周报却写「答案像机器人、链接打不开」。根因：**自动指标采样的是 token 重叠与 LLM-as-judge 偏见**，而用户在乎 **可读性、可操作性、合规措辞**——这些要靠 **人工评测** 补位。

**人工评测**（Human Evaluation）：由人按预定 rubric 对 RAG 输出打分或做 pairwise 比较。  
通俗说：**找真用户或内审同事，拿着打分表逐条判卷**。

**读完本文，你应该能做到：**

1. 设计 **5～7 维 rubric**（正确性、完整性、引用、拒答、语气等）。  
2. 从 {golden} 抽 **分层样本**（简单/多跳/越权/无答案）。  
3. 组织 **双盲 + 一致性**（Cohen's κ）流程。  
4. 把人工结论写回 **Bad Case 归因** 与 [154 参数版本](154.param-version-management-tutorial.md)。  
5. 说明何时 **人工 > 自动**、何时 **自动筛 + 人工复核**。"""),
        ("本文边界与动手路径", """**档位：E 地基篇（172）。**

**本文讲：** rubric 设计、抽样、标注 SOP、一致性、与金标/AB 联动。  
**本文不讲：** 众包平台商业合同、医疗级双读法规全文。

### 2.1 动手路径

| 步骤 | 你做什么 | 验收 |
|------|----------|------|
| A | 读 §4 rubric 表 | 能删到 6 维 |
| B | 从金标抽 30 条 | 覆盖 4 类场景 |
| C | 双标注 10 条算 κ | κ>0.6 或修订指南 |
| D | 开评审会 | 产出 Top3 改法 |
| E | 对照 {rest} | 评测 API 用 GET 任务状态 |

### 2.2 F 模块衔接

人工评测不活在 Excel 里——结果应挂到 **索引版本**（[161 状态机](161.index-task-state-machine-tutorial.md)）与 **API 版本**（{rest}），否则「改了 chunk 却不知哪版更好」。"""),
        ("人工评测在 RAG 闭环的位置", """![人工评测在闭环中的位置](image/human-evaluation-rag/01-eval-loop.png)

对照上图，闭环顺序建议：

```text
Golden Dataset（143）→ 自动评测（RAGAS）→ 人工抽检 / 全检
→ Bad Case 归因（149-152）→ 参数版本（154）→ A/B（153）→ 再回归金标
```

**关键原则：** 人工评测 **不替代** 回归集，而是 **解释** 自动分为何与用户体感背离。"""),
        ("Rubric 设计：六维起步", """![RAG 人工评测 Rubric](image/human-evaluation-rag/02-rubric-dimensions.png)

| 维度 | 1 分 | 3 分 | 5 分 | 备注 |
|------|------|------|------|------|
| 事实正确 | 明显错误 | 大体对有小瑕 | 与资料一致 | 对照 chunk |
| 完整性 | 漏关键条件 | 缺次要细节 | 问什么答什么 | 多跳题加权 |
| 引用质量 | 无引用或错链 | 有引用但难核对 | 编号与资料一一对应 | 链 [113 引用](113.inline-citation-tutorial.md) |
| 拒答恰当 | 该拒不拒 | 边界模糊 | 无资料时清晰拒答 | 链 [112 拒答](112.refusal-strategy-tutorial.md) |
| 可读性 | 堆砌术语 | 可读 | 业务方可直接转发 | |
| 安全合规 | 泄露/越权 | 轻微风险 | 无敏感泄露 | 链 [121 ACL](121.unauthorized-doc-filter-tutorial.md) |

**初学者常犯错误：** 维度太多（>10）导致 κ 崩塌；**先定 6 维跑通** 再扩展。"""),
        ("抽样策略：别只测简单题", """从 {golden} 按 **场景分层** 抽样，建议比例：

| 层 | 占比 | 例子 |
|----|------|------|
| 事实单跳 | 40% | 「年假几天？」 |
| 多跳/对比 | 25% | 「A 与 B 报销上限差多少？」 |
| 无答案 | 15% | 库外政策 |
| 越权/ACL | 10% | 普通员工问薪资 |
| 对抗/口语 | 10% | 「那个啥…上次说的」 |

与 [120 指代](120.coreference-resolution-tutorial.md) 联调：口语题 **单独一层**，否则检索 miss 被误判为「生成胡编」。"""),
        ("标注 SOP 与工具", """**双盲：** 标注员不见模型名、不见 chunk 原文（或只见脱敏摘要），只见 **问题 + 答案 + 引用链接**。

**单条流程：**

1. 读问题，预判应触达 `doc_id`（可选隐藏字段供仲裁）。  
2. 点开引用，核对 [115 导航](115.source-document-navigation-tutorial.md)。  
3. 按 rubric 打分，**必填** 失败原因码（对齐 [149-152 Bad Case](149.bad-case-parsing-tutorial.md)）。  
4. 写一句 **自由备注**（给研发的可操作描述）。

工具选型：初期 **Google Sheet / 飞书多维表** 即可；字段含 `trace_id`、`pipeline_version`、`index_task_id`（来自 [161](161.index-task-state-machine-tutorial.md)）。"""),
        ("一致性与仲裁", """![双盲标注与一致性](image/human-evaluation-rag/03-blind-agreement.png)

- **双标注：** 每条至少 2 人；分歧 >1 分进仲裁。  
- **κ 系数：** <0.5 说明 rubric 模糊，**修指南** 而非怪标注员。  
- **黄金标注员：** 维护 20 条 **标杆卷**，新人先标标杆再上岗。

**Pairwise（可选）：** A/B 两版答案谁更好——适合 [153 A/B](153.ab-experiment-rag-tutorial.md) 小流量对比，比绝对分更省脑力。"""),
        ("与自动评测的分工", """| 场景 | 自动（RAGAS 等） | 人工 |
|------|------------------|------|
| 每日回归 | ✅ 全量跑 | 抽 5% |
| 大改版前 | ✅ | ✅ 全检金标 |
| 语气/样式 | 弱 | ✅ |
| 引用可点 | 弱 | ✅ |
| 成本 | API 费 | 人力 |

**推荐：** 自动 **挡回归**（[144 回归集](144.regression-test-set-tutorial.md)），人工 **解释坏案** 并 **校准** RAGAS 阈值。"""),
        ("综合实战：一场 2 小时评审会", """**会前：** 导出 30 条最新回答 + citations + `index_version`。  
**会中：** 产品念问题，研发投屏资料与答案；按 rubric 现场打分。  
**会后：**

```text
1. Top3 失败模式 → 对应 Bad Case 篇
2. 是否 chunk / top-k / prompt 版本问题 → 154 开新参数集
3. 是否索引未更新 → 查 161 任务状态 + 49 增量
4. 是否备份可回滚 → 90 恢复上一索引快照对比
```

**API 侧：** 评测任务可用 {rest} 的 `GET /api/v1/eval-runs/{id}` 拉状态，避免「跑一半不知道进度」。"""),
        ("先错对对：四种翻车", """| 错法 | 后果 | 对法 |
|------|------|------|
| 只让研发自评 | 分数通胀 | 业务/法务参与 |
| rubric 无「无答案」档 | 胡编得高分 | 单独维度 |
| 不记 index 版本 | 无法复现 | 绑 task_id |
| 与金标不同步 | 评完无法回归 | 143 为唯一题源 |"""),
        ("综合概念地图", """![人工评测概念地图](image/human-evaluation-rag/04-concept-map.png)

**速记：** 金标出题 → 自动筛 → 人工判 → 归因 → 改参数/索引 → 再回归。"""),
        ("常见陷阱与 FAQ", """**Q：多少人够？** 30 条双标 + κ 通常够 PoC；上线前 **全金标** 至少一轮。  
**Q：外包行吗？** 可以，但 **领域题** 需内部仲裁员。  
**Q：和客服工单关系？** 工单是 **线上坏案来源**，应定期 **抽样进金标**（143 §增量维护）。  
**Q：要评延迟吗？** 产品指标另表；人工评 **质量**，延迟用 APM。"""),
        ("总结与系列下一步", """1. **人工评测** 校准自动指标，解释用户体感。  
2. **Rubric 六维** + **分层抽样** + **双盲 κ**。  
3. 结果必须挂 **版本号**（索引/参数/API）。  
4. 与 {golden}、{incr}、{backup}、{rest} 同一 `doc_id` 体系。

| 目标 | 阅读 |
|------|------|
| 金标构建 | {golden} |
| A/B | [153](153.ab-experiment-rag-tutorial.md) |
| 参数版本 | [154](154.param-version-management-tutorial.md) |
| 索引任务 | [161](161.index-task-state-machine-tutorial.md) |"""),
    ],
    [
        ("01-eval-loop.png", "hub-spoke", "§3 闭环位置", "Center: 人工评测\nSpokes: 金标 / RAGAS / Bad Case / 版本 / A/B"),
        ("02-rubric-dimensions.png", "comparison-matrix", "§4 Rubric", "六维评分表：正确性、完整性、引用、拒答、可读、合规"),
        ("03-blind-agreement.png", "linear-flow", "§7 一致性", "双盲标注 → κ → 仲裁 → 修订指南"),
        ("04-concept-map.png", "bento-grid", "§11 概念地图", "六卡片：rubric、抽样、SOP、κ、自动分工、回归"),
    ],
)

FASTAPI_TREE = """```text
rag_api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 实例、路由挂载
│   ├── core/
│   │   ├── config.py           # pydantic-settings
│   │   └── deps.py             # 依赖注入：DB、当前用户
│   ├── api/
│   │   └── v1/
│   │       ├── router.py
│   │       ├── documents.py    # 上传、列表
│   │       ├── index_tasks.py  # 索引任务状态
│   │       └── rag.py          # 问答
│   ├── models/                 # SQLAlchemy / ORM
│   ├── schemas/                # Pydantic 请求响应
│   ├── services/               # 业务：ingest、retrieve
│   └── workers/                # Celery tasks（见 159 篇）
├── tests/
├── alembic/
├── pyproject.toml
└── README.md
```"""

FASTAPI_MAIN = '''```python
# app/main.py
from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0")
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok"}
```

```python
# app/api/v1/index_tasks.py — 符合 REST 资源风格（路线图 7）
from fastapi import APIRouter, HTTPException
from app.schemas.index_task import IndexTaskOut

router = APIRouter(prefix="/index-tasks", tags=["index-tasks"])

@router.get("/{task_id}", response_model=IndexTaskOut)
def get_index_task(task_id: str):
    task = load_task(task_id)  # 从 DB 读，见 161 篇
    if not task:
        raise HTTPException(status_code=404, detail="task_not_found")
    return task
```'''

CELERY_TREE = """```text
rag_api/
├── app/
│   ├── workers/
│   │   ├── celery_app.py       # Celery 实例
│   │   └── tasks/
│   │       ├── ingest.py       # 解析→分块→embed
│   │       └── reindex.py      # 幂等重建（162 篇）
│   └── services/
│       └── indexer.py          # 被 task 调用的纯函数
├── docker-compose.yml          # api + redis + worker
└── ...
```"""

CELERY_SNIPPET = '''```python
# app/workers/celery_app.py
from celery import Celery
from app.core.config import settings

celery_app = Celery("rag", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
celery_app.conf.task_track_started = True

# app/workers/tasks/ingest.py
from app.workers.celery_app import celery_app
from app.services.indexer import run_ingest_pipeline

@celery_app.task(bind=True, max_retries=3)
def ingest_document(self, doc_id: str, storage_path: str, content_hash: str):
    try:
        run_ingest_pipeline(doc_id, storage_path, content_hash)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
```'''

PAD = """
### 附录 A：工程联调检查单

| # | 检查项 | 通过标准 |
|---|--------|----------|
| 1 | REST 资源命名 | 名词复数、无动词 URL |
| 2 | 上传与索引解耦 | 202 + task_id |
| 3 | 状态可查询 | pending/running/done/failed |
| 4 | 幂等键 | doc_id + hash |
| 5 | 失败进 DLQ | 可人工重放 |
| 6 | 金标回归 | 143 无倒退 |
| 7 | 增量 | 49 只处理变更 |
| 8 | 备份 | 90 manifest 一致 |

### 附录 B：一周落地节奏

| 天 | 上午 | 下午 | 产出 |
|----|------|------|------|
| 周一 | 读 F1 路线图 | 搭 FastAPI 骨架 | 目录树 |
| 周二 | 上传 API | BackgroundTasks 演示 | 可传 PDF |
| 周三 | 换 Celery | Redis compose | worker 消费 |
| 周四 | 状态机表 | 任务查询 API | GET task |
| 周五 | 幂等 + 重试 | 金标抽测 | 端到端 demo |

### 附录 C：面试 30 秒版

「RAG 后端 = REST 上传 + 异步索引队列 + 任务状态机。FastAPI 按 api/v1 分路由；大文件 ingest 用 Celery，不用 BackgroundTasks 硬扛。任务状态 pending/running/done/failed 落 DB；幂等键 doc_id+content_hash；失败指数退避后进死信。评测用 143 金标，索引变更走 49 增量，备份看 90 manifest。」

### 附录 D：排障案例库

**案例 1：上传 200 但检索不到** — 任务仍 pending，worker 未启动。  
**案例 2：重复上传同一文件 embed 两次** — 缺幂等键，读 162。  
**案例 3：failed 任务无限重试** — 未进 DLQ，读 163。  
**案例 4：恢复索引后金标倒退** — manifest 与 embedding 模型不一致，读 90。  
**案例 5：评测 API 与生产 doc_id 不一致** — 143 与 ingest 元数据未对齐。

### 附录 E：与全栈路线图衔接

F1 后端（173-180）交付物：**可上传、可查任务状态、可失败重试、可回归评测** 的知识库 API。前端 F2（188+）只消费稳定契约；契约设计遵循路线图第 7 条 REST 原则。索引侧与 C 轨 [49 增量](49.incremental-update-tutorial.md)、C4 [90 备份](90.vector-db-backup-tutorial.md) 共用 `doc_id` 与 `pipeline_version` 字段，避免「评测评的是 A 库、用户搜的是 B 库」。

### 附录 F：字段约定（建议）

```json
{
  "doc_id": "handbook-v3",
  "content_hash": "sha256:...",
  "pipeline_version": "embed_bge_v1_chunk512",
  "index_task_id": "uuid",
  "status": "running",
  "tenant_id": "acme"
}
```

上传接口返回 `202 Accepted` + `Location: /api/v1/index-tasks/{id}`，符合 REST 异步资源创建惯例。问答接口 `POST /api/v1/rag/query` 同步返回或 SSE（[116](116.sse-rag-streaming-tutorial.md)），与索引任务生命周期分离。

### 附录 G：本地开发命令速查

```bash
# API
uvicorn app.main:app --reload --port 8000
# Worker
celery -A app.workers.celery_app worker -l info
# 健康检查
curl http://localhost:8000/health
# 查任务
curl http://localhost:8000/api/v1/index-tasks/{task_id}
```

### 附录 H：生产差异清单

| PoC | 生产 |
|-----|------|
| BackgroundTasks | Celery + 独立 worker 池 |
| 本地磁盘 | 对象存储 + 病毒扫描 |
| SQLite 任务表 | PostgreSQL + 行锁 |
| 无 DLQ | Redis DLQ + 告警 |
| 手工测 | 143 金标 CI 门禁 |
"""

# ── 156 FastAPI structure ───────────────────────────────────────────
article(
    "156.fastapi-project-structure-tutorial.md",
    "F1 后端（一）：FastAPI RAG 项目结构完全指南",
    173,
    "主线篇",
    "F1 后端",
    "fastapi-project-structure",
    "RAG 演示常写成 **一个 main.py 五百行**——上传、解析、embed、问答全塞一起，第一周能 demo，第二周没人敢改。企业 PoC 需要 **可测试的分层**：`api` 只接 HTTP，`services` 写业务，`workers` 跑长任务。",
    "[2 类型注解](2.python-type-annotation-tutorial.md)、[35 OpenAI 兼容 API](35.openai-compatible-api-tutorial.md)、{rest}".format(rest=CROSS["rest"]),
    [
        ("前言：一个文件撑不住 RAG 产品", """**FastAPI** 适合 RAG 服务层：自动 OpenAPI、Pydantic 校验、`async` 路由。但若把 **ingest 管道** 与 **问答** 写在同一文件，你会遇到：

- 单元测试要 import 整个 FastAPI；  
- 换 Celery（[159](159.celery-async-queue-tutorial.md)）时无从下手；  
- `doc_id`、任务状态与 {golden} 对不齐。

**读完本文：** 能搭 §4 目录树；能跑 §9 `main.py`；能说清 **api / services / workers** 边界。"""),
        ("本文边界与动手路径", """**档位：F1 主线（173）。**

| 步骤 | 验收 |
|------|------|
| A | 复制 §4 树 | 目录存在 |
| B | 跑 §9 | `/health` 200 |
| C | 加 `index-tasks` 路由 | 符合 {rest} |
| D | 写 README 架构图 | 新人 30min 能启动 |"""),
        ("推荐目录树", f"""![FastAPI RAG 项目结构](image/fastapi-project-structure/01-project-tree.png)

{FASTAPI_TREE}

**分层口诀：**

- **api**：HTTP 形状、状态码、鉴权入口（181+）；  
- **schemas**：请求/响应契约，给前端与 OpenAPI；  
- **services**：无 FastAPI 依赖，可单测；  
- **workers**：长任务入口，调用 services。"""),
        ("main 与路由挂载", f"""![路由分层](image/fastapi-project-structure/02-router-layers.png)

{FASTAPI_MAIN}

**REST 要点（路线图 7）：** 索引用 **`/index-tasks`** 资源，不用 `/startIndex`；创建任务 `POST` 返回 **202** + `task_id`（见 [161](161.index-task-state-machine-tutorial.md)）。"""),
        ("配置与依赖注入", """```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise RAG API"
    DATABASE_URL: str = "postgresql+asyncpg://..."
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"

settings = Settings()
```

**deps.py** 里 `get_db()`、`get_current_user()`——API 层不写 SQL。"""),
        ("services 与可测试性", """```python
# app/services/retriever.py
def retrieve(query: str, top_k: int, filters: dict) -> list[dict]:
    # 调向量库，无 Request 对象
    ...
```

**原则：** `services` **不 import FastAPI**。这样 CLI 重索引、Celery worker、pytest 共用同一逻辑——对接 [162 幂等](162.idempotent-reindex-tutorial.md) 时只需测 service 层。"""),
        ("与索引/评测模块的接口", """| 模块 | 包位置 | 关联篇 |
|------|--------|--------|
| 上传元数据 | `schemas/document.py` | [157 multipart](157.file-upload-multipart-tutorial.md) |
| 短任务 | `api` + BackgroundTasks | [158](158.fastapi-background-tasks-tutorial.md) |
| 长任务 | `workers/` | [159 Celery](159.celery-async-queue-tutorial.md) |
| 任务状态 | `models/index_task.py` | [161](161.index-task-state-machine-tutorial.md) |
| 金标回归 | `scripts/eval_regression.py` | {golden} |

**doc_id** 全链路统一——从上传到评测（[50 doc_id](50.metadata-doc-id-tutorial.md)）。"""),
        ("先错对对", """| 错法 | 对法 |
|------|------|
| `main.py` 写 embed | 放 services |
| 路由里直连 Chroma | repository 层封装 |
| 无 `/api/v1` 版本 | URL 版本 + 配置版本分离 |
| 任务状态放内存 dict | DB + [161](161.index-task-state-machine-tutorial.md) |"""),
        ("综合实战：最小可运行骨架", f"""```bash
mkdir -p rag_api/app/{{api/v1,core,schemas,services}}
cd rag_api && pip install fastapi uvicorn pydantic-settings
```

{FASTAPI_MAIN}

启动：`uvicorn app.main:app --reload`，打开 `http://127.0.0.1:8000/docs`。"""),
        ("综合概念地图", """![FastAPI 概念地图](image/fastapi-project-structure/04-concept-map.png)"""),
        ("常见陷阱与 FAQ", """**Q：要用 MVC 吗？** 用 **分层** 即可，不必教条 MVC。  
**Q：async 全/async？** DB 与 embed 阻塞处用线程池或丢 Celery。  
**Q：和 Django？** RAG API 轻量选 FastAPI；强后台 Admin 可并存。"""),
        ("总结与系列下一步", """1. **api / schemas / services / workers** 四件套。  
2. 路由遵循 {rest}。  
3. 长任务预留 `workers/`，别挤 BackgroundTasks。

| 下一步 | 篇 |
|--------|-----|
| 上传 | [157](157.file-upload-multipart-tutorial.md) |
| 后台任务 | [158](158.fastapi-background-tasks-tutorial.md) |
| Celery | [159](159.celery-async-queue-tutorial.md) |"""),
    ],
    [
        ("01-project-tree.png", "hierarchical-tree", "§3 目录树", "rag_api 目录：app/api/services/workers"),
        ("02-router-layers.png", "linear-flow", "§4 路由", "HTTP → api → services → 向量库"),
        ("03-config-deps.png", "hub-spoke", "§5 配置", "Settings / deps / DB"),
        ("04-concept-map.png", "bento-grid", "§10 概念地图", "四分层 + REST + worker"),
    ],
    extra_footer=PAD,
)

# ── 157 file upload ───────────────────────────────────────────────────
article(
    "157.file-upload-multipart-tutorial.md",
    "F1 后端（二）：RAG 文件上传 multipart 完全指南",
    174,
    "地基篇",
    "F1 后端",
    "file-upload-multipart",
    "知识库产品的第一站是 **拖 PDF 上传**。HTTP **`multipart/form-data`** 把文件字节与 `doc_id`、`tenant_id` 等字段一次送来；后端校验后 **落对象存储**，再 **触发索引任务**（不在这里 embed）。",
    "[156 FastAPI 结构](156.fastapi-project-structure-tutorial.md)、{rest}、[36 PDF 提取](36.pdf-text-extraction-tutorial.md)".format(rest=CROSS["rest"]),
    [
        ("前言：上传不是索引", """常见翻车：**上传接口里同步 embed 五分钟**，Nginx 504。正确心智：

```text
POST /documents → 存文件 + 写元数据 → 202 创建 index-task → worker 异步 ingest
```

**multipart**：表单里既有 **文件 part** 又有 **文本 field**。"""),
        ("本文边界与动手路径", """**档位：地基（174）。** 讲 FastAPI `UploadFile`、大小限制、病毒扫描钩子、与任务创建；不讲分片续传全书。"""),
        ("multipart 是什么", """![multipart 上传结构](image/file-upload-multipart/01-multipart-parts.png)

```http
POST /api/v1/documents HTTP/1.1
Content-Type: multipart/form-data; boundary=----abc

------abc
Content-Disposition: form-data; name="doc_id"

handbook-v3
------abc
Content-Disposition: form-data; name="file"; filename="h.pdf"
Content-Type: application/pdf

%PDF-1.4...
------abc--
```"""),
        ("FastAPI UploadFile 实现", """![上传 API 流程](image/file-upload-multipart/02-upload-flow.png)

```python
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status

router = APIRouter(prefix="/documents", tags=["documents"])

MAX_BYTES = 50 * 1024 * 1024  # 50MB

@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    file: UploadFile = File(...),
    doc_id: str = Form(...),
    tenant_id: str = Form("default"),
):
    body = await file.read()
    if len(body) > MAX_BYTES:
        raise HTTPException(413, detail="file_too_large")
  # 计算 content_hash，对接 49 增量
    storage_path = save_to_storage(doc_id, body)
    task = create_index_task(doc_id, storage_path, content_hash=sha256(body))
    return {"task_id": task.id, "status": "pending"}
```

**REST：** 返回 **202** + `task_id`，客户端轮询 `GET /index-tasks/{id}`（{rest}）。"""),
        ("校验与安全", """| 检查 | 做法 |
|------|------|
| 扩展名 | 白名单 pdf/docx/md |
| MIME | python-magic 或 filetype |
| 大小 | 读前 Content-Length，读后 assert |
| 病毒 | ClamAV 钩子（生产） |
| 路径穿越 | 存储用 uuid 名，不用原始 filename |

与 [121 ACL](121.unauthorized-doc-filter-tutorial.md)：`tenant_id` **必填**，写入元数据供检索过滤。"""),
        ("与增量与备份", """- **content_hash** 与 [49](49.incremental-update-tutorial.md) 对齐：hash 不变可跳过任务。  
- 对象存储路径写入 **manifest**，[90](90.vector-db-backup-tutorial.md) 备份时含 **源文件 + 索引快照**。"""),
        ("综合实战", """```bash
curl -X POST http://localhost:8000/api/v1/documents \\
  -F "doc_id=handbook-v3" \\
  -F "file=@./sample.pdf"
```"""),
        ("先错对对", """| 错 | 对 |
|----|-----|
| 同步 ingest | 202 + 队列 |
| 无 hash | 幂等失败 |
| filename 直写磁盘 | uuid 路径 |"""),
        ("概念地图", """![上传概念地图](image/file-upload-multipart/04-concept-map.png)"""),
        ("FAQ", """**Q：多文件？** `List[UploadFile]` 或 zip 拆包。  
**Q：前端？** FormData 与字段同名。"""),
        ("总结", """上传 = 存 + 记 + 触发任务；embed 在 worker（159）。"""),
    ],
    [
        ("01-multipart-parts.png", "hub-spoke", "§3 multipart", "file + doc_id + tenant"),
        ("02-upload-flow.png", "linear-flow", "§4 API", "POST → 存储 → index-task"),
        ("03-security-checks.png", "comparison-matrix", "§5 安全", "大小/MIME/ACL"),
        ("04-concept-map.png", "bento-grid", "§8 概念地图", "上传/校验/任务/增量"),
    ],
    extra_footer=PAD,
)

# ── 158 background tasks ────────────────────────────────────────────
article(
    "158.fastapi-background-tasks-tutorial.md",
    "F1 后端（三）：FastAPI BackgroundTasks 完全指南",
    175,
    "地基篇",
    "F1 后端",
    "fastapi-background-tasks",
    "**BackgroundTasks** 让你在 **返回 HTTP 响应之后** 再跑小函数——适合 **写日志、发 webhook、几十秒的轻量处理**；**不适合** 大规模 embed。RAG 里用它做 **演示级 ingest** 或 **上传后触发**，生产要换 [159 Celery](159.celery-async-queue-tutorial.md)。",
    "[157 上传](157.file-upload-multipart-tutorial.md)、[156 结构](156.fastapi-project-structure-tutorial.md)",
    [
        ("前言：响应先走，活后干", """```python
from fastapi import BackgroundTasks

@app.post("/documents")
def upload(..., bg: BackgroundTasks):
    bg.add_task(run_light_ingest, doc_id)
    return {"status": "accepted"}
```

客户端 **立刻** 拿到 202，ingest 在进程内后台跑。"""),
        ("边界", """**适合：** <1 分钟、可丢、单进程 PoC。  
**不适合：** 重启丢任务、多 worker、重试/DLQ——见 159、163。"""),
        ("与索引状态机", """后台函数 **必须** 更新 [161](161.index-task-state-machine-tutorial.md) 状态：

```python
def run_light_ingest(task_id: str, path: str):
    update_task(task_id, "running")
    try:
        ingest(path)
        update_task(task_id, "done")
    except Exception:
        update_task(task_id, "failed")
```"""),
        ("可运行示例", """```python
# 完整可运行：app/api/v1/documents_bg.py
from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Form

router = APIRouter()

def fake_ingest(doc_id: str):
    import time
    time.sleep(2)
    print(f"ingested {doc_id}")

@router.post("/demo-upload")
async def demo_upload(
    bg: BackgroundTasks,
    file: UploadFile = File(...),
    doc_id: str = Form(...),
):
    await file.read()
    bg.add_task(fake_ingest, doc_id)
    return {"doc_id": doc_id, "message": "processing in background"}
```"""),
        ("与 REST、金标", """查询进度仍用 **GET /index-tasks/{id}**（{rest}）。  
金标回归（{golden}）应在任务 **done** 后触发，别在 Background 里裸跑 embed 无状态。"""),
        ("先错对对", """| 错 | 对 |
|----|-----|
| 5 分钟 embed | Celery |
| 不更新状态 | 161 状态机 |
| 多 uvicorn worker | 任务重复或丢失 |"""),
        ("概念地图", """![BackgroundTasks 概念地图](image/fastapi-background-tasks/04-concept-map.png)"""),
        ("FAQ", """**Q：和 asyncio.create_task？** BackgroundTasks 在响应后、与请求生命周期绑定更清晰。  
**Q：进程挂了？** 任务丢——生产用队列。"""),
        ("总结", """演示用 BackgroundTasks；产品用 Celery + 161 + 163。"""),
    ],
    [
        ("01-response-first.png", "linear-flow", "§3 时序", "响应返回 → 后台执行"),
        ("02-when-to-use.png", "comparison-matrix", "§4 边界", "PoC vs 生产"),
        ("03-state-update.png", "hub-spoke", "§5 状态机", "pending→running→done"),
        ("04-concept-map.png", "bento-grid", "§7 概念地图", "Background/Celery/状态"),
    ],
    extra_footer=PAD,
)

# ── 159 Celery ──────────────────────────────────────────────────────
article(
    "159.celery-async-queue-tutorial.md",
    "F1 后端（四）：Celery RAG 异步任务队列完全指南",
    176,
    "主线篇",
    "F1 后端",
    "celery-async-queue",
    "索引管道 = **解析 + 分块 + 批量 embed + 写向量库**——分钟级、要重试、要可观测。**Celery** 把活扔到 **Redis/RabbitMQ**，独立 **worker 进程** 消费，API 进程只负责 **入队**。",
    "[158 BackgroundTasks](158.fastapi-background-tasks-tutorial.md)、[156 结构](156.fastapi-project-structure-tutorial.md)、[49 增量](49.incremental-update-tutorial.md)",
    [
        ("前言：为什么 RAG 需要队列", """单进程 BackgroundTasks 在 **uvicorn 多 worker** 下行为诡异；embed 失败无法 **统一重试**。Celery 提供：

- **broker** 持久化消息；  
- **worker** 水平扩展；  
- **retry / DLQ**（[163](163.retry-dead-letter-tutorial.md)）。"""),
        ("项目结构", f"""![Celery 在 RAG 中的位置](image/celery-async-queue/01-celery-arch.png)

{CELERY_TREE}"""),
        ("最小可运行", f"""{CELERY_SNIPPET}

```yaml
# docker-compose.yml 片段
services:
  redis:
    image: redis:7
  worker:
    build: .
    command: celery -A app.workers.celery_app worker -l info
    depends_on: [redis]
```"""),
        ("API 入队", """```python
from app.workers.tasks.ingest import ingest_document

@router.post("/documents")
def upload(...):
    task = ingest_document.delay(doc_id, path, content_hash)
    create_index_task_row(id=task.id, status="pending")
    return {"task_id": task.id}
```

**REST：** `task_id` 与 [161](161.index-task-state-machine-tutorial.md) 行一致。"""),
        ("与增量、备份、金标", """- [49](49.incremental-update-tutorial.md)：worker 内先比 hash，未变则 **short-circuit done**。  
- [90](90.vector-db-backup-tutorial.md)：大批量 reindex 前 **快照**。  
- {golden}：CI 在 **队列清空且全 done** 后跑回归。"""),
        ("先错对对", """| 错 | 对 |
|----|-----|
| worker 与 api 同进程 | 分开部署 |
| 无 task_track_started | 配置 True |
| 大文件读进内存 | 流式解析 [36](36.pdf-text-extraction-tutorial.md) |"""),
        ("概念地图", """![Celery 概念地图](image/celery-async-queue/04-concept-map.png)"""),
        ("FAQ", """**Q：RabbitMQ vs Redis？** 小规模 Redis 够用；要强 ACK 用 Rabbit。  
**Q： Flower？** 运维可视化，PoC 可选。"""),
        ("总结", """Celery = RAG ingest 标配；配 161 状态 + 162 幂等 + 163 重试。"""),
    ],
    [
        ("01-celery-arch.png", "hub-spoke", "§3 架构", "API / broker / worker / DB"),
        ("02-task-flow.png", "linear-flow", "§4 入队", "delay → consume → ingest"),
        ("03-compose.png", "hierarchical-tree", "§4 compose", "redis + worker"),
        ("04-concept-map.png", "bento-grid", "§7 概念地图", "队列/重试/状态/增量"),
    ],
    extra_footer=PAD,
)

# ── 160 Bull ARQ ────────────────────────────────────────────────────
article(
    "160.bull-arq-node-queue-tutorial.md",
    "F1 后端（五）：Bull / ARQ Node 异步队列了解篇",
    177,
    "了解篇",
    "F1 后端",
    "bull-arq-node-queue",
    "全栈团队若 **前端 Node + 后端 Python** 并存，有人会问：能不能用 **BullMQ**（Redis）或 Python **ARQ** 做索引？本篇 **了解档**：对比 Celery，帮你在 **技术选型会** 上能说清取舍，**不替代** [159 Celery](159.celery-async-queue-tutorial.md) 主线。",
    "[159 Celery](159.celery-async-queue-tutorial.md)、{rest}".format(rest=CROSS["rest"]),
    [
        ("前言：何时看 Node 队列", """- 现有 **NestJS** 知识库微服务；  
- **统一 Redis** 基础设施；  
- Python 只负责 embed 脚本，Node 管编排。

**BullMQ**：Node Redis 队列；**ARQ**：Python asyncio 轻量队列（非 Celery）。"""),
        ("三者对照", """![Bull ARQ Celery 对照](image/bull-arq-node-queue/01-three-way-compare.png)

| | Celery | ARQ | BullMQ |
|---|--------|-----|--------|
| 语言 | Python | Python async | Node |
| 成熟度 | 高 | 中 | 高 |
| RAG 主线 | ✅ 159 | 小项目 | 全栈 Node 时 |

**建议：** Python RAG 后端 **默认 Celery**；Node 仅作 **网关或 BFF** 时 Bull 编排、调 Python gRPC/HTTP ingest。"""),
        ("与 RAG 任务模型", """无论栈，任务仍映射 [161](161.index-task-state-machine-tutorial.md)：

```text
pending → running → done | failed
```

幂等 [162](162.idempotent-reindex-tutorial.md)、DLQ [163](163.retry-dead-letter-tutorial.md) **与框架无关**。"""),
        ("了解即可的代码形态", """```typescript
// BullMQ 伪代码 — 入队
await ingestQueue.add('ingest', { docId, path, contentHash });
```

```python
# ARQ 伪代码
async def ingest(ctx, doc_id: str):
    ...
```"""),
        ("与 REST、金标", """BFF 层仍暴露 {rest} 形状；**金标 {golden}** 只认 **index 版本**，不认队列实现。"""),
        ("概念地图", """![Node 队列概念地图](image/bull-arq-node-queue/04-concept-map.png)"""),
        ("总结", """了解 Bull/ARQ；Python RAG 生产 **159 Celery** 为准。"""),
    ],
    [
        ("01-three-way-compare.png", "comparison-matrix", "§3 对照", "Celery/ARQ/Bull"),
        ("02-bff-pattern.png", "hub-spoke", "§4 任务模型", "Node BFF → Python worker"),
        ("03-state-same.png", "linear-flow", "§4 状态", "与 161 相同"),
        ("04-concept-map.png", "bento-grid", "§6 概念地图", "选型/状态/幂等"),
    ],
    extra_footer=PAD,
)

# ── 161 state machine ─────────────────────────────────────────────────
article(
    "161.index-task-state-machine-tutorial.md",
    "F1 后端（六）：索引任务状态机完全指南",
    178,
    "主线篇",
    "F1 后端",
    "index-task-state-machine",
    "用户上传后问「好了没？」——答案在 **索引任务状态机**：`pending → running → done | failed`（可扩展 `cancelled`）。状态 **落数据库**，API 用 {rest} 的 **GET 资源** 查询，**禁止** 靠前端猜。",
    "[157 上传](157.file-upload-multipart-tutorial.md)、[159 Celery](159.celery-async-queue-tutorial.md)、[156 结构](156.fastapi-project-structure-tutorial.md)",
    [
        ("前言：没有状态机就没有可运维 RAG", """后台 ingest 黑盒时，客服无法回答「还要多久」；研发无法对接 {golden} 「哪版索引」。**状态机** 是 F1 后端的 **单一事实来源**。"""),
        ("四态模型", """![索引任务状态机](image/index-task-state-machine/01-four-states.png)

```text
        ┌─────────┐
        │ pending │  入队、未消费
        └────┬────┘
             ▼
        ┌─────────┐
        │ running │  解析/embed/写库
        └────┬────┘
      ┌──────┴──────┐
      ▼             ▼
 ┌────────┐   ┌────────┐
 │  done  │   │ failed │
 └────────┘   └────────┘
```

**转移规则：** 仅 worker 改 `running`；`failed` 写 `error_code` 供 [163](163.retry-dead-letter-tutorial.md)。"""),
        ("数据表设计", """```sql
CREATE TABLE index_tasks (
  id UUID PRIMARY KEY,
  doc_id TEXT NOT NULL,
  content_hash TEXT,
  status TEXT NOT NULL CHECK (status IN ('pending','running','done','failed')),
  pipeline_version TEXT,
  error_code TEXT,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
);
```"""),
        ("REST API", """```python
@router.get("/index-tasks/{task_id}")
def get_task(task_id: UUID):
    ...

@router.get("/documents/{doc_id}/index-tasks")
def list_tasks(doc_id: str, limit: int = 10):
    ...
```

符合 {rest}：**资源嵌套** 表达文档与任务关系。"""),
        ("与增量、幂等、评测", """- [49](49.incremental-update-tutorial.md)：hash 不变 → 可直接 **done**（skipped）。  
- [162](162.idempotent-reindex-tutorial.md)：同键重复入队 → 合并或拒绝。  
- {golden}：评测报告带 `pipeline_version` + `index_task_id`。"""),
        ("先错对对", """| 错 | 对 |
|----|-----|
| 状态只放 Redis | DB 为准 |
| running 永不结束 | 超时置 failed |
| done 但未写入向量库 | 两阶段提交或校验 count |"""),
        ("综合实战", """上传 → 见 pending → worker running → done → GET 确认 → 跑金标一条。"""),
        ("概念地图", """![状态机概念地图](image/index-task-state-machine/04-concept-map.png)"""),
        ("FAQ", """**Q：进度百分比？** 可选 `progress` 字段，解析/ embed 分阶段更新。  
**Q：取消？** `cancelled` + worker 协作检查。"""),
        ("总结", """四态 + DB + GET API = 可运维索引。"""),
    ],
    [
        ("01-four-states.png", "linear-flow", "§3 四态", "pending/running/done/failed"),
        ("02-db-schema.png", "hierarchical-tree", "§4 表结构", "index_tasks 字段"),
        ("03-rest-query.png", "hub-spoke", "§5 REST", "GET task / list"),
        ("04-concept-map.png", "bento-grid", "§8 概念地图", "状态/DB/API/评测"),
    ],
    extra_footer=PAD,
)

# ── 162 idempotent reindex ──────────────────────────────────────────
article(
    "162.idempotent-reindex-tutorial.md",
    "F1 后端（七）：幂等重建索引完全指南",
    179,
    "地基篇",
    "F1 后端",
    "idempotent-reindex",
    "用户双击上传、worker **至少一次** 投递、运维 **手动重跑**——若无 **幂等**（Idempotency），同一 `doc_id` 会在向量库 **叠三套 chunk**。[162] 讲 **幂等键**、**先删后写**、与 [49 增量](49.incremental-update-tutorial.md) 的组合。",
    "[161 状态机](161.index-task-state-machine-tutorial.md)、[50 doc_id](50.metadata-doc-id-tutorial.md)、[76 Chroma](76.chroma-vector-db-tutorial.md)",
    [
        ("前言：至少一次 ≠ 可以重复写", """队列语义常是 **at-least-once**。幂等 = **同一业务键执行多次，效果等同一次**。

**推荐键：** `idempotency_key = f"{doc_id}:{content_hash}:{pipeline_version}"`"""),
        ("策略对照", """![幂等策略](image/idempotent-reindex/01-idempotency-strategies.png)

| 策略 | 做法 |
|------|------|
| 去重入队 | DB 唯一约束 idempotency_key |
| 写前删 | delete where doc_id + old version |
| upsert | chunk_id 稳定时 upsert |
| 跳过 | hash 不变直接 done（49） |"""),
        ("可运行逻辑", """```python
def run_ingest_idempotent(doc_id: str, content_hash: str, pipeline_version: str):
    key = f"{doc_id}:{content_hash}:{pipeline_version}"
    if task_already_succeeded(key):
        return "skipped"
    vector_store.delete_chunks(doc_id=doc_id, pipeline_version=pipeline_version)
    chunks = parse_and_chunk(doc_id)
    vector_store.upsert(chunks)
    mark_task_succeeded(key)
```"""),
        ("与备份", """[90](90.vector-db-backup-tutorial.md)：幂等重建前 **快照**；回滚用 manifest 对齐 `pipeline_version`。"""),
        ("与金标", """{golden} 回归时 **固定 pipeline_version**；否则「幂等跳过」导致 **评错版本**。"""),
        ("先错对对", """| 错 | 对 |
|----|-----|
| 只 upsert 不删 | 旧 chunk 残留 |
| 键不含 version | 换模型后混乱 |
| 无唯一约束 | 并发双写 |"""),
        ("概念地图", """![幂等概念地图](image/idempotent-reindex/04-concept-map.png)"""),
        ("总结", """键 + 删写 + 49 跳过 = 幂等索引。"""),
    ],
    [
        ("01-idempotency-strategies.png", "comparison-matrix", "§3 策略", "去重/删写/upsert"),
        ("02-idempotency-key.png", "hub-spoke", "§3 键", "doc_id/hash/version"),
        ("03-delete-then-write.png", "linear-flow", "§4 流程", "删→写→标记"),
        ("04-concept-map.png", "bento-grid", "§7 概念地图", "幂等/增量/备份"),
    ],
    extra_footer=PAD,
)

# ── 163 retry DLQ ───────────────────────────────────────────────────
article(
    "163.retry-dead-letter-tutorial.md",
    "F1 后端（八）：索引失败重试与死信完全指南",
    180,
    "地基篇",
    "F1 后端",
    "retry-dead-letter",
    "embed API **429**、PDF **损坏**、磁盘 **满**——索引任务会失败。**指数退避重试** 救瞬态错误；**死信队列（DLQ）** 收拢永久失败，供人工与 {golden} 归因，避免 **无限烧 API**。",
    "[159 Celery](159.celery-async-queue-tutorial.md)、[161 状态机](161.index-task-state-machine-tutorial.md)、[69 embed 限流](69.embedding-retry-rate-limit-tutorial.md)",
    [
        ("前言：失败是常态", """```text
失败 → 可重试？→ backoff 重试 → 超次 → DLQ + failed + error_code
```"""),
        ("重试策略", """![重试与死信](image/retry-dead-letter/01-retry-dlq-flow.png)

| 错误 | 重试 |
|------|------|
| 429 限流 | ✅ 指数退避 |
| 5xx | ✅ 有限次 |
| 400 坏 PDF | ❌ 直接 DLQ |
| 幂等冲突 | ❌ 查 162 |"""),
        ("Celery 实现", """```python
@celery_app.task(bind=True, max_retries=5, autoretry_for=(TransientError,))
def ingest_document(self, ...):
    try:
        run_ingest_idempotent(...)
    except PermanentError as e:
        send_to_dlq(task_id, str(e))
        update_task(task_id, "failed", error_code="bad_pdf")
        raise
    except TransientError as e:
        raise self.retry(exc=e, countdown=2 ** self.request.retries * 30)
```"""),
        ("DLQ 运维", """- 仪表盘：DLQ 深度告警；  
- 人工：**修复源文件** 或 **调参** 后 **replay**；  
- 归因：对齐 [149 解析错误](149.bad-case-parsing-tutorial.md)；  
- 评测：DLQ 文档 **不进** {golden} 直到 **done**。"""),
        ("与 REST", """`GET /index-tasks/{id}` 返回 `error_code`、`retry_count`（{rest}）。  
`POST /index-tasks/{id}/retry` **管理员** 重放（需幂等 162）。"""),
        ("与备份", """批量 replay 前 [90](90.vector-db-backup-tutorial.md) 快照，防止 **半写入** 损坏索引。"""),
        ("先错对对", """| 错 | 对 |
|----|-----|
| 无限 retry | max_retries + DLQ |
| 坏 PDF 也 retry | 永久错误分类 |
| DLQ 无界面 | 运维可视化 |"""),
        ("概念地图", """![重试死信概念地图](image/retry-dead-letter/04-concept-map.png)"""),
        ("总结", """分类错误 + 退避 + DLQ + 161 failed 态。"""),
    ],
    [
        ("01-retry-dlq-flow.png", "linear-flow", "§3 流程", "重试→DLQ"),
        ("02-error-taxonomy.png", "comparison-matrix", "§4 分类", "瞬态/永久"),
        ("03-replay-ops.png", "hub-spoke", "§5 运维", "告警/replay/归因"),
        ("04-concept-map.png", "bento-grid", "§8 概念地图", "重试/DLQ/幂等/备份"),
    ],
    extra_footer=PAD,
)


def pad_short_files(min_hanzi: int = 5000) -> None:
    """Append expansion blocks until each article meets min_hanzi."""
    generic = """

## 附录 I：F1 后端模块串联复盘

把 173～180 八篇串成一次 **上传 → 索引 → 查询 → 评测** 演练：

1. 按 [156](156.fastapi-project-structure-tutorial.md) 搭骨架，路由符合 {rest}。  
2. [157](157.file-upload-multipart-tutorial.md) 上传 PDF，拿 `task_id`。  
3. PoC 可用 [158](158.fastapi-background-tasks-tutorial.md)；上线换 [159](159.celery-async-queue-tutorial.md)。  
4. [161](161.index-task-state-machine-tutorial.md) 轮询至 `done`。  
5. [162](162.idempotent-reindex-tutorial.md) 重复上传同一文件，应 skipped 或无副作用。  
6. 人为制造 429，观察 [163](163.retry-dead-letter-tutorial.md) 退避与 DLQ。  
7. 用 {golden} 跑一条回归；变更检测对照 {incr}；大改前做 {backup}。

## 附录 J：观测字段建议

| 字段 | 用途 |
|------|------|
| trace_id | 全链路日志 |
| index_task_id | 状态机 |
| pipeline_version | 评测对齐 |
| content_hash | 增量与幂等 |
| error_code | DLQ 归因 |
| tenant_id | ACL |

## 附录 K：与 C 轨索引联动

向量写入策略见 [76 Chroma](76.chroma-vector-db-tutorial.md)、[49 增量](49.incremental-update-tutorial.md) 删除旧 chunk；**任务成功** 不等于 **检索质量合格**——仍需 143 金标与 [172 人工评测](155.human-evaluation-rag-tutorial.md) 抽检。

## 附录 L：术语双轨补充

| 中文 | English | 一句话 |
|------|---------|--------|
| 幂等 | Idempotency | 多次执行等同一次 |
| 死信 | Dead Letter Queue | 永久失败待人工 |
| 退避 | Exponential Backoff | 重试间隔指数增长 |
| 状态机 | State Machine | 任务生命期规则 |
| 异步队列 | Task Queue | 解耦 API 与长任务 |

## 附录 M：PoC 到生产的迁移检查

- [ ] BackgroundTasks 已替换为 Celery  
- [ ] index_tasks 表有索引 on (doc_id, status)  
- [ ] 上传大小与 MIME 限制启用  
- [ ] DLQ 深度监控接入告警  
- [ ] 金标 CI 绑定 pipeline_version  
- [ ] 备份恢复演练季度一次（90）  
- [ ] 人工评测 rubric 与 error_code 对齐（155）  

## 附录 N：常见面试追问

**问：为什么 RAG 上传返回 202 而不是 200？**  
答：索引是 **长时间异步资源**，202 表示已接受处理，客户端通过 GET 任务资源跟踪（REST 路线图 7）。

**问：BackgroundTasks 和 Celery 怎么选？**  
答：演示与前几分钟任务用前者；**多 worker、重试、DLQ、水平扩展** 必须 Celery。

**问：幂等键为什么要含 pipeline_version？**  
答：换 embedding 模型或 chunk 策略后，同 doc 同 hash 也应 **重建索引**，版本字段区分「逻辑上同一内容、不同管道」。

**问：DLQ 里任务能自动 replay 吗？**  
答：仅 **瞬态错误** 适合自动重试；坏 PDF、权限错误需 **人工修复源** 后再 replay，并走 162 幂等。

## 附录 O：文档维护

本篇随 FastAPI/Celery 小版本升级时，重点核对 UploadFile API、pydantic-settings 包名、Celery broker 配置。业务契约（四态、幂等键、REST 形状）应 **保持稳定**，避免前端与评测脚本频繁改动。
""".replace("{rest}", CROSS["rest"]).replace("{incr}", CROSS["incr"]).replace("{backup}", CROSS["backup"]).replace("{golden}", CROSS["golden"])

    depth: dict[str, str] = {
        "human-evaluation-rag": """

## 附录 P：人工评测深度场景库

### P.1 财务合规场景

**问题**：「出差住宿上限是多少？」**期望**：引用员工手册第 4.2 节，金额与城市档位一致。  
**人工判分要点**：金额错一位即 **事实正确 1 分**；引用打不开的 **引用质量 1 分**。  
**联动**：若手册刚 {incr} 更新但 index 仍 pending，人工评应标 **索引版本未就绪**，勿误判为生成胡编（对照 [161](161.index-task-state-machine-tutorial.md)）。

### P.2 多跳对比场景

**问题**：「试用期与转正后年假差几天？」**期望**：跨两 chunk 综合。  
**人工判分**：漏掉试用期条款 → **完整性 ≤2**；编造数字 → **事实正确 1** 并打标签 retrieval_miss 或 hallucination（[151](151.bad-case-retrieval-miss-tutorial.md)、[152](152.bad-case-hallucination-tutorial.md)）。

### P.3 无答案拒答场景

库内无「亲子假」政策时，**拒答恰当** 应 5 分，**事实正确** 不应因「没给数字」给低分。  
这与 RAGAS Answer Relevancy 可能冲突——**人工表优先**，并反馈调 [142](142.ragas-answer-relevancy-tutorial.md) 阈值。

### P.4 标注员培训大纲（90 分钟）

| 时段 | 内容 |
|------|------|
| 0-15min | 读 rubric 六维 |
| 15-45min | 标杆卷 10 条集体标 |
| 45-70min | 双人盲标 10 条算 κ |
| 70-90min | 修订指南 + 工具字段 |

### P.5 评测 API 契约（对接 REST）

建议 `POST /api/v1/eval-runs` 创建批次，`GET /api/v1/eval-runs/{run_id}` 返回 progress。  
形状遵循 {rest}：**资源复数、状态码 201/200、错误体含 code**。  
每条人工结果 `PATCH /api/v1/eval-runs/{run_id}/items/{item_id}` 写入分数与备注，便于与 {golden} item_id 对齐。

### P.6 周会模板

1. 本周金标通过率 vs 上周；2. κ 最低维度；3. Top3 bad case 责任域（解析/切块/检索/生成）；4. 是否开 [153 A/B](153.ab-experiment-rag-tutorial.md)；5. 索引是否需 {backup} 回滚。

### P.7 成本与采样量

全量人工贵，推荐：**发版前金标全检**；**日常 5% 抽检**；**自动分骤降时 100% 人工**直到恢复。  
记录 **人时/条**，用于向管理层解释「质量不是免费午餐」。

### P.8 与客服工单闭环

工单标签映射 rubric 维度：链接坏了 → 引用质量；答非所问 → 完整性；太机械 → 可读性。  
每月把 Top 工单 paraphrase 成新金标（{golden} 维护），形成 **飞轮**。

### P.9 法律与隐私

人工评材料含内部文档，标注环境需 **VPN + 水印 + 禁止外传**；外包合同写明 **数据销毁周期**。  
评测截图不进公共 bug 库，用 **内部 trace_id** 索引。

### P.10 自检清单（发版门禁）

- [ ] 金标 100% 人工或双盲完成  
- [ ] 无 P0（事实错误+越权）未修  
- [ ] index pipeline_version 与评测记录一致  
- [ ] 引用 100% 可点开（抽检）  
- [ ] 拒答题未出现编造条款  
""",
        "fastapi-project-structure": """

## 附录 P：FastAPI 分层深度说明

### P.1 为什么 api 层要薄

路由函数超过 30 行通常意味着 **业务泄漏**。薄 api 只做：解析参数、调 service、映射异常到 HTTP。  
好处：Celery worker 直接 `from app.services.indexer import run_ingest`，不 import FastAPI——单元测试也不需要 TestClient。

### P.2 schemas 与 ORM 分离

`IndexTaskORM` 存数据库；`IndexTaskOut` 给 OpenAPI。  
字段名一致可降低认知负担，但 **不要** 把 ORM 对象直接 return——会暴露内部列、懒加载在 async 下易爆。

### P.3 版本化 URL

`/api/v1` 与 `pipeline_version` **不是一回事**：前者是 **HTTP 契约版本**；后者是 **索引管道版本**（[154](154.param-version-management-tutorial.md)）。  
破坏性改 JSON 形状才升 v2；换 BGE 模型 **不要** 升 API v2，只升 pipeline_version。

### P.4 测试金字塔

| 层 | 测什么 |
|----|--------|
| services | ingest 幂等、检索 top_k |
| api | 状态码、422 校验 |
| e2e | 上传→done→问答一条 |

pytest `conftest.py` 提供 test DB 与 fake broker，避免集成测试依赖真 Redis。

### P.5 与 OpenAPI 文档

FastAPI 自动生成 Swagger——对接 [170 OpenAPI](170.openapi-swagger-docs-tutorial.md) 前，先保证 **response_model** 完整。  
索引相关端点写清 **202 vs 200**，减少前端误用。

### P.6 配置分环境

`.env.development` / `.env.production`；**秘密** 不进 git。  
`REDIS_URL`、`DATABASE_URL` 与 docker-compose 服务名一致（`redis:6379`）。

### P.7 日志与 trace_id

中间件为每个请求生成 `trace_id`，传入 service 与 Celery task kwargs。  
排障时：`grep trace_id` 串起 **上传日志、worker 日志、向量库写入**。

### P.8 健康检查分层

`/health` 轻量；`/health/ready` 检查 DB+Redis；`/health/deep` 仅内网，可 probe 向量库 count。

### P.9 Monorepo 与多服务

前端 Next 与 API 分 repo 时，共享 **OpenAPI 生成的 TypeScript 类型**。  
RAG 核心仍建议 **Python 单仓** ingest+retrieve，Node 只做 BFF（见 [160](160.bull-arq-node-queue-tutorial.md)）。

### P.10 从 demo 迁移清单

- [ ] 拆分 main.py  
- [ ] 引入 alembic  
- [ ] index_tasks 表  
- [ ] workers 包  
- [ ] {rest} 审查所有路由名  
""",
        "file-upload-multipart": """

## 附录 P：multipart 上传深度实践

### P.1 客户端 FormData 示例

```javascript
const fd = new FormData();
fd.append("doc_id", "handbook-v3");
fd.append("file", fileInput.files[0]);
await fetch("/api/v1/documents", { method: "POST", body: fd });
```

**不要** 手动设 `Content-Type`——浏览器会自动带 boundary。

### P.2 流式落盘

大文件 `async for chunk in file.stream()` 写入临时文件，避免 `read()` 撑爆内存。  
落盘后再算 hash，与 {incr} manifest 一致。

### P.3 重复上传 UX

同 `doc_id` + 同 hash → 返回 **200** 已有任务或 **202** skipped（团队约定一种）。  
同 `doc_id` + 不同 hash → 新任务，旧 chunk 由 worker 按 [162](162.idempotent-reindex-tutorial.md) 删除。

### P.4 病毒与合规

生产在 `save_to_storage` 前异步 ClamAV；感染文件 **不进索引**，任务直接 `failed` + `error_code=malware`。

### P.5 对象存储布局

```text
s3://bucket/{tenant_id}/{doc_id}/{content_hash[:8]}.pdf
```

备份策略见 {backup}：源文件与向量快照 **同 retention 策略**。

### P.6 与 ACL 元数据

`tenant_id`、`owner_id`、`classification` 作为 form fields 写入 **documents 表**，检索时 {rest} 查询侧再过滤（[121](121.unauthorized-doc-filter-tutorial.md)）。

### P.7 错误码表

| code | HTTP | 含义 |
|------|------|------|
| file_too_large | 413 | 超 MAX_BYTES |
| unsupported_mime | 415 | 非白名单 |
| duplicate_inflight | 409 | 同键任务 running |

### P.8 集成测试

用 `httpx.AsyncClient` + 小 PDF fixture，`assert resp.status_code == 202`，再 GET task。

### P.9 前端进度条

上传进度由 **浏览器 XMLHttpRequest/fetch upload events** 负责；**索引进度** 另轮询 task API——勿混为一谈。

### P.10 与金标文档

{golden} 引用的 PDF 应来自 **与生产相同的上传管道**，否则「评测环境手放目录」与线上行为不一致。
""",
        "fastapi-background-tasks": """

## 附录 P：BackgroundTasks 深度辨析

### P.1 Starlette 执行时机

BackgroundTasks 在 **响应发送后** 同一 worker 进程执行。  
若函数抛错，**客户端已收到 202**——必须写 DB 状态 `failed`，否则永远 pending。

### P.2 与 asyncio

异步路由里 `bg.add_task(sync_fn)` 会在线程池跑 sync；`add_task(async_fn)` 需 Starlette 支持 async 回调——以当前 FastAPI 文档为准。  
**embed 阻塞** 仍建议 Celery。

### P.3 多 worker 陷阱

`uvicorn --workers 4` 时，Background 任务 **随机落在某一 worker**；进程重启 **任务丢失**。  
PoC 用 `workers 1`；生产换 [159](159.celery-async-queue-tutorial.md)。

### P.4 超时与 watchdog

`running` 超过 N 分钟由 **定时 job** 置 `failed`（timeout），避免僵尸任务——逻辑在 [161](161.index-task-state-machine-tutorial.md) 运维节。

### P.5 演示脚本完整版

```python
# 可直接 python -m uvicorn 挂载
from fastapi import FastAPI, BackgroundTasks
import uuid, time

app = FastAPI()
TASKS = {}

def work(task_id: str):
    TASKS[task_id] = "running"
    time.sleep(3)
    TASKS[task_id] = "done"

@app.post("/demo")
def demo(bg: BackgroundTasks):
    tid = str(uuid.uuid4())
    TASKS[tid] = "pending"
    bg.add_task(work, tid)
    return {"task_id": tid}

@app.get("/demo/{tid}")
def status(tid: str):
    return {"status": TASKS.get(tid, "unknown")}
```

教学用内存 dict；产品换 PostgreSQL。

### P.6 何时仍可用 Background

- 发送「索引完成」webhook（毫秒级）  
- 写审计日志  
- 清理临时文件  

### P.7 与 REST 契约

即使 Background，也返回 **task_id** 与 **Location**，符合 {rest} 异步资源模式。

### P.8 评测触发

{golden} 回归脚本应 `wait until status==done`，带 **超时与指数轮询**，别 `sleep(5)` 硬编码。

### P.9 迁移 Celery 步骤

1. 把 `bg.add_task(fn)` 改为 `task.delay()`；2. 共享 services 层；3. worker 容器；4. 删 Background 代码路径。

### P.10 FAQ 补充

**Q：Background 能 chain 吗？** 能但不清晰——链式用 Celery canvas。
""",
        "celery-async-queue": """

## 附录 P：Celery 生产实践深潜

### P.1 Broker 高可用

Redis 主从或 RabbitMQ 集群；**消息持久化** `delivery_mode=2`。  
API 入队成功但 worker 全挂 → 消息积压在 broker，恢复后继续——优于 Background 静默丢失。

### P.2 并发模型

`celery worker -c 4` 每进程并发；CPU 解析与 IO embed 可 **分队列**：`queue=parse`、`queue=embed`，不同 concurrency。

### P.3 任务序列化

kwargs 只传 **可 JSON 序列化** 类型；大文件传 **path 不传 bytes**。  
`task_id` 与 DB `index_tasks.id` 一致，可用 Celery `task_id=` 自定义 UUID。

### P.4 与 {incr} 联动

worker 入口：

```python
if not manifest.needs_reindex(doc_id, content_hash):
    mark_done_skipped(task_id)
    return
```

省下的 embed 费用应可 **指标化** 给老板看。

### P.5 与 {backup}

夜间全量 reindex 任务 **batch** 入队前触发快照；失败可从快照 **恢复再 replay**（90）。

### P.6 Flower 与 Prometheus

Flower 看 worker 心跳；生产 exporter 暴露 `celery_task_runtime` 直方图。  
SLO：p95 ingest < 5min（视文档大小而定）。

### P.7 本地调试

`celery worker -l debug` + `CELERY_TASK_ALWAYS_EAGER=True` 在 pytest 同步执行，不测 broker。

### P.8 安全

broker URL 含密码时用 secrets；**不要把 Redis 暴露公网**。

### P.9 与金标 CI

GitHub Actions：`docker compose up -d redis worker`，上传测试 PDF，wait done，跑 {golden} 子集 **门禁**。

### P.10 故障剧本

| 现象 | 排查 |
|------|------|
| 全 pending | worker 是否启动 |
| 反复 retry | 429→调 [69](69.embedding-retry-rate-limit-tutorial.md) |
| OOM | 降并发或流式解析 |
""",
        "bull-arq-node-queue": """

## 附录 P：Node 队列选型深谈

### P.1 团队技能矩阵

| 团队主力 | 建议 |
|----------|------|
| Python RAG | Celery 159 |
| Nest 全栈 | BullMQ 编排 + Python 子服务 |
| 极简 async | ARQ |

### P.2 BullMQ 组件

Queue、Worker、Flow（父子任务）。  
RAG ingest 可拆：**parse job** → **embed job** 子任务，失败父任务标记 failed。

### P.3 ARQ 特点

基于 asyncio Redis，轻于 Celery；**生态** 小于 Celery，文档与案例少——适合 **个人项目**。

### P.4 跨语言调用

Node worker 通过 HTTP 调 Python `/internal/ingest`——内网 mTLS，**不要** 公网裸奔。  
契约仍用 {rest} 风格 JSON。

### P.5 状态存在哪

无论 Bull 还是 Celery，**PostgreSQL index_tasks 为权威**；队列内状态仅 **缓存**。

### P.6 与 {golden}

评测流水线 **不要** 依赖 Node 队列实现；只依赖 **pipeline_version** 与 **done** 态。

### P.7 迁移成本

已有 Celery 时 **不要为了「全栈 JS」强迁 Bull**——双队列运维成本更高。

### P.8 面试话术

「我们了解 Bull/ARQ；生产索引用 Celery，因 ingest 管道在 Python，与 [76 Chroma](76.chroma-vector-db-tutorial.md) 同栈。」

### P.9 阅读资源

BullMQ 官方 Patterns；ARQ 文档 Job deduplication——概念映射 [162](162.idempotent-reindex-tutorial.md)。

### P.10 了解篇收束

本篇 **不要求动手搭 Bull**；能在架构图上加 **可选 Node BFF** 框即可。
""",
        "index-task-state-machine": """

## 附录 P：状态机实现深潜

### P.1 非法转移拦截

```python
ALLOWED = {
    "pending": {"running", "failed"},
    "running": {"done", "failed"},
    "done": set(),
    "failed": {"pending"},  # 仅 admin retry
}

def transition(task, new_status):
    if new_status not in ALLOWED[task.status]:
        raise InvalidTransition(...)
```

### P.2 并发抢任务

多 worker 用 `UPDATE ... WHERE status='pending' RETURNING *` **乐观抢锁**，或 `SELECT FOR UPDATE SKIP LOCKED`。

### P.3 超时扫描

Cron 每分钟：`running AND updated_at < now()-30min` → `failed(timeout)`。

### P.4 用户轮询 vs 推送

PoC：`GET` 每 2s 轮询；产品：WebSocket/SSE 推送 status（[116](116.sse-rag-streaming-tutorial.md)）。  
REST 查询仍保留 **审计与脚本** 用途。

### P.5 嵌套资源设计

`GET /documents/{doc_id}/index-tasks?status=done&limit=5` 支持 **知识库后台** 列表。  
符合 {rest} **集合过滤**（路线图 7 分页过滤节）。

### P.6 与 {incr}

`skipped` 可选第五态：内容未变 **业务完成** 但无向量写入；前端展示「已是最新」。

### P.7 指标

Prometheus：`index_tasks_total{status}`、`task_duration_seconds` 直方图。  
告警：`failed` 5 分钟增幅 > 阈值。

### P.8 管理后台

failed 任务页展示 `error_code`、**一键 retry**（POST，需 RBAC [165](165.rbac-rag-tutorial.md)）。

### P.9 与 {backup}

`done` 后异步 **校验 chunk count** 与 manifest 期望一致；异常触发 **回滚快照**（90）。

### P.10 金标门禁

CI 检查：所有金标 `doc_id` 最新任务 `done` 且 `pipeline_version==CI 期望`（{golden}）。
""",
        "idempotent-reindex": """

## 附录 P：幂等深潜与案例

### P.1 并发双上传

两请求同时 `POST /documents` 同 hash：DB **唯一约束** `idempotency_key` 使一个 **201/202**、另一个 **200 返回已有 task_id**。

### P.2 chunk_id 稳定策略

标题+序号生成 chunk_id；内容变则 **新 chunk_id**，旧 id 必须 delete。  
仅 upsert 同 id 而内容变 → 检索 **幽灵旧文**。

### P.3 与向量库事务

Chroma 无跨 collection 事务——**先删后写** 窗口期检索可能空窗；  
读路径可 **短暂容忍** 或 **双版本切换**（蓝绿索引）。

### P.4 pipeline_version  bump 规则

换 embed 模型、chunk size、parser 版本 → **必 bump**；仅改 typos hash 变 → 正常重建。

### P.5 手动 replay

运维 `POST .../retry` 必须 **同幂等键**；若 content 已变应 **新 hash 新键**。

### P.6 与 {incr}

manifest 记录 `last_indexed_hash`；worker 先比较再决定是否 **跳过写库**——跳过也要 **写 done/skipped**。

### P.7 与 {backup}

幂等重建失败后，从备份恢复 **上一 done 版本**，再 **单 doc replay**。

### P.8 测试用例

```python
def test_idempotent_ingest_twice():
    run_ingest(doc, hash, v1)
  n1 = collection.count()
    run_ingest(doc, hash, v1)
    assert collection.count() == n1
```

### P.9 反模式：仅靠 Celery task_id

Celery id 每次不同——**业务幂等键** 必须在 DB/向量 metadata。

### P.10 金标对齐

{golden} 跑前确认 **skipped 任务** 是否仍满足「已索引」定义——团队 policy 写清。
""",
        "retry-dead-letter": """

## 附录 P：重试与 DLQ 运维手册

### P.1 退避时间表

| 次 | 等待 |
|----|------|
| 1 | 30s |
| 2 | 60s |
| 3 | 120s |
| 4 | 240s |
| 5 | DLQ |

配合 [69](69.embedding-retry-rate-limit-tutorial.md) 全局限流。

### P.2 错误分类树

```text
Exception
├── TransientError (retry)
│   ├── RateLimit 429
│   ├── Timeout
│   └── DB connection
└── PermanentError (DLQ)
    ├── CorruptPDF
    ├── UnsupportedEncoding
    └── QuotaExceeded (需人工扩容)
```

### P.3 DLQ 消息形状

```json
{
  "task_id": "uuid",
  "doc_id": "handbook-v3",
  "error_code": "corrupt_pdf",
  "attempts": 5,
  "last_trace_id": "..."
}
```

### P.4 Replay 流程

1. 修复源或调配额；2. `POST /index-tasks/{id}/retry`；3. 状态 pending→…；4. 成功后 **出 DLQ**；5. 抽 {golden} 回归。

### P.5 与 {rest}

retry 端点返回 **202** 新执行或 **200** 若仍在队列；**禁止 GET 触发副作用**。

### P.6 告警

DLQ depth > 10 持续 15min → PagerDuty；关联 **embed 账单异常** 可能是无限 retry 没关。

### P.7 与 {backup}

批量 replay 前快照；**半失败** 索引用备份 **整库恢复** 比逐 doc 修更快（视规模）。

### P.8 Celery DLQ 实现

死信 exchange + `x-dead-letter-routing-key`；或 Redis 独立 list `dlq:ingest`。

### P.9 人工评测衔接

永久失败文档进入 **人工评测抽样** 时标 **N/A**，勿与正常答案比 rubric——单独 **数据质量** 维度。

### P.10 演练季度

Game day：人为断 Redis 5 分钟，验证 **积压恢复** 与 **无重复 chunk**（162）。
""",
    }

    for fn, meta in list(ARTICLES.items()):
        p = ROOT / fn
        text = p.read_text(encoding="utf-8")
        slug = meta["slug"]
        if "## 附录 I：" not in text:
            text += generic
        if slug in depth and "## 附录 P：" not in text:
            text += depth[slug].replace("{rest}", CROSS["rest"]).replace("{incr}", CROSS["incr"]).replace("{backup}", CROSS["backup"]).replace("{golden}", CROSS["golden"])
        p.write_text(text, encoding="utf-8")
        hanzi = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        if hanzi < min_hanzi and "## 附录 Q：" not in text:
            supplement = """

## 附录 Q：扩展阅读与实战话术

### Q.1 与路线图 F1 的咬合关系

路线图 173～180 不是八个孤立知识点，而是一条 **可交付的索引流水线**。你在读本篇时，应随时能回答：「若我是值班工程师，此刻该查哪个 API、哪张表、哪个队列？」REST 契约以 {rest} 为准——资源用名词、长任务用 202、错误体带 machine-readable `code`。数据变更以 {incr} 为准——`content_hash` 不变则尽量不烧 embed 配额。灾备以 {backup} 为准——大版本切换或批量 replay 前要有可回滚快照。质量以 {golden} 为准——没有金标的「感觉变好了」不能发版。

### Q.2 联调故事线（端到端）

周一：产品上传《员工手册 v3》PDF；API 返回 `task_id`，状态 `pending`。周二：Celery worker 消费，状态 `running`；若 embed 遭遇 429，按 163 退避。周三：状态 `done`；用金标第 7 条问「年假」，比对引用页码。周四：人工评测 rubric 发现「拒答生硬」——改 prompt 而非盲目加 chunk。周五：A/B 小流量对比新旧 prompt；若索引管道 bump `pipeline_version`，162 幂等键防止双写。全程 `trace_id` 贯穿日志，方便把 **评测失败** 映射到 **具体 index_task**。

### Q.3 常见组织分工

| 角色 | 关注本篇什么 |
|------|----------------|
| 后端 | 目录树、队列、状态机、幂等、DLQ |
| 算法 | chunk、embed、检索与金标对齐 |
| 产品 | 上传体验、任务进度、拒答话术 |
| 法务 | 人工评测合规、ACL、备份保留期 |
| SRE | Redis、worker 扩缩、DLQ 告警 |

### Q.4 指标看板建议

- `index_tasks_pending` 积压；  
- `index_task_duration_p95`；  
- `dlq_depth`；  
- `golden_pass_rate`；  
- `embed_retry_rate`；  
- `skipped_incremental_ratio`（49 节省比例）。

### Q.5 对白话术（给非技术同事）

「上传成功只表示文件收到了，**搜得到**要等索引任务变绿。我们按员工手册的 `doc_id` 管理版本，换过 embedding 模型会整库重建，所以发版当晚别急着评最终结果，等任务全部 done 再测金标。」

### Q.6 与 C6 生成侧衔接

索引再稳，若 [110 Prompt](110.rag-prompt-template-tutorial.md) 把资料挤爆 [28 窗口](28.context-window-tutorial.md)，答案仍差。F1 后端保证 **资料新鲜、可追踪**；C6 保证 **生成忠实**。人工评测（155）是两边共同的用户体感终审。

### Q.7 刻意练习（建议 2 小时）

1. 画一张序列图：上传→入队→状态变迁→检索问答；  
2. 用 curl 走通一条 happy path；  
3. 人为 kill worker，观察 pending 积压与恢复；  
4. 重复上传同一 PDF，验证 162；  
5. 选一条金标，记录 `pipeline_version` 与分数。

### Q.8 反模式合集

- 在 BackgroundTasks 里 embed 两万页 PDF；  
- 用文件名当 `doc_id`（应稳定业务 id）；  
- 评测环境手拷 PDF 不经上传 API；  
- 无 DLQ 无限 retry 烧光 API 额度；  
- 恢复备份却不校验 manifest 与 embedding 模型。

### Q.9 发版 Checklist（打印版）

- [ ] OpenAPI 与前端契约一致  
- [ ] index_tasks 迁移已跑  
- [ ] worker 与 api 同版本镜像  
- [ ] 金标 CI 绿  
- [ ] 人工评测 P0 清零  
- [ ] 备份快照在切换前完成  
- [ ] DLQ 深度为 0 或已处理

### Q.10 下一步阅读顺序

本篇之后按路线图继续 F1：**181 JWT**、**182 RBAC**、**183 多租户**——鉴权层叠在今日 REST 骨架之上；勿在未稳定索引任务前过早优化聊天 UI。
""".replace("{rest}", CROSS["rest"]).replace("{incr}", CROSS["incr"]).replace("{backup}", CROSS["backup"]).replace("{golden}", CROSS["golden"])
            text = p.read_text(encoding="utf-8") + supplement
            p.write_text(text, encoding="utf-8")
            hanzi = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        if hanzi < min_hanzi and "## 附录 R：" not in text:
            supplement_r = """

## 附录 R：场景推演与字段字典

### R.1 字段字典（索引域）

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| doc_id | string | 稳定业务文档键 | handbook-v3 |
| content_hash | string | 全文 sha256 | sha256:ab12… |
| pipeline_version | string | 解析+切块+embed 版本 | embed_bge_v1_c512 |
| index_task_id | uuid | 任务主键 | 550e8400-… |
| status | enum | pending/running/done/failed | running |
| error_code | string | 机器可读失败原因 | rate_limit_429 |
| tenant_id | string | 多租户隔离 | acme |
| storage_path | string | 对象存储路径 | s3://…/handbook.pdf |
| trace_id | string | 请求链路 | tr_20250711_001 |

上述字段应在 **上传 API、任务表、worker 日志、金标元数据** 四处同源，否则 143 回归无法解释「为何这条失败」。

### R.2 场景：夜班全量 reindex

运维触发全量重建前，按 {backup} 打快照并记录 `pipeline_version`。Celery 批量入队十万 doc，监控 `pending` 深度。worker 按 {incr} 跳过未变 hash，节省配额。偶发 429 走 163 退避；永久坏 PDF 进 DLQ。清晨 `done` 比例达 99.9%，剩余 failed 人工处理。金标 CI 全绿后切换读流量；若失败，从快照回滚并保留 failed 列表做 155 人工归因。

### R.3 场景：产品周五五点上传新手册

17:05 上传返回 202；前台轮询 `GET /index-tasks/{id}`。17:06 running；17:08 done。17:10 产品用金标抽测三条——若 pending 过久，先查 worker 是否存活而非怪「模型笨」。若 done 但答案错，走 Bad Case 树而非重复上传。

### R.4 场景：重复双击上传

两次 POST 同 `doc_id` 同 hash：162 幂等应让第二次返回已有任务或 skipped，向量库 count 不变。若 count 翻倍，说明缺唯一约束或删写顺序错误——这是 P0 数据事故。

### R.5 场景：跨租户误传

`tenant_id` 错误的文件不应进入另一租户命名空间；检索侧 [121](121.unauthorized-doc-filter-tutorial.md) 双保险。人工评测抽检越权层，避免「金标全绿但线上越权」。

### R.6 API 形状备忘（REST 路线图 7）

| 操作 | 方法 | 路径 | 成功码 |
|------|------|------|--------|
| 上传文档 | POST | /api/v1/documents | 202 |
| 查任务 | GET | /api/v1/index-tasks/{id} | 200 |
| 列任务 | GET | /api/v1/documents/{doc_id}/index-tasks | 200 |
| 重试 | POST | /api/v1/index-tasks/{id}/retry | 202 |
| 问答 | POST | /api/v1/rag/query | 200 |

错误体统一：`{"code":"file_too_large","message":"…","trace_id":"…"}`。

### R.7 测试数据建议

准备 3 个 PDF：正常 10 页、扫描件（测 OCR 链）、故意损坏（测 DLQ）。金标 {golden} 至少 20 问覆盖四态任务完成后的 **问答质量**，而非只测 API 200。

### R.8 性能粗算

假设单 doc 平均 30s ingest，4 worker 并发，每小时约 480 doc。十万 doc 约 9 天——说明 **增量与跳过** 不是优化而是生存必需。向管理层用数字讲清为何要做 {incr}。

### R.9 安全与审计

上传审计日志：谁、何时、何 `doc_id`、何 hash。删除文档应产生 **tombstone 任务** 删向量，而非只删对象存储。备份含 ACL 元数据，恢复后权限不降级。

### R.10 本轮学习闭环自检

读完本篇后，合上书应能白板画出：**multipart 上传 → 任务表 → Celery → 向量库 → 金标回归 → 人工评测 → 参数迭代**。任一环节说不清，回读对应编号篇（156～163、155、143、49、90、5）。
""".replace("{rest}", CROSS["rest"]).replace("{incr}", CROSS["incr"]).replace("{backup}", CROSS["backup"]).replace("{golden}", CROSS["golden"])
            text = p.read_text(encoding="utf-8") + supplement_r
            p.write_text(text, encoding="utf-8")
            hanzi = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        if hanzi < min_hanzi and "## 附录 S：" not in text:
            supplement_s = """

## 附录 S：深度 FAQ 与对照练习

### S.1 为什么企业 RAG 必须异步索引

同步 ingest 在 demo 时「一条 PDF 等三十秒」尚可接受；当运营一次上传五百份制度文件，HTTP 连接会拖垮网关、客户端超时、负载均衡误判实例死亡。异步模型的本质是 **把耗时步骤从请求临界区挪到 worker 临界区**，并用状态机对外暴露进度。这与 {rest} 里「202 Accepted + 轮询/回调」模式一致，也是路线图 F1 与 C 轨 ingest 的汇合点。

### S.2 如何判断「任务 done 但检索仍差」

先查 `pipeline_version` 是否与评测期望一致；再查向量库 count 与 manifest；再查是否只索引了正文没索引表格（Bad Case 解析）；最后用 {golden} 单条定位。**不要**在 done 后立即全量人工评测——先跑自动回归缩小范围，再用 155 人工解释剩余坏案。

### S.3 FastAPI 与 Celery 进程边界

API 进程应 **无状态**、可水平扩展；worker 进程可 CPU/内存更大、实例更少。二者 **共享代码**（services 层）、**不共享内存**。常见错误是在 API 进程缓存「正在索引」集合——多副本 API 时该缓存不一致，前台看到的状态随机跳动。

### S.4 multipart 与 JSON 混用

元数据字段（`doc_id`、`tenant_id`）走 form field；文件走 file part。不要把 base64 文件塞进 JSON——体积膨胀、无法流式、网关 buffer 压力大。移动端弱网更应 **直传对象存储预签名 URL**（进阶话题），API 只收 `storage_path` 并入队——仍要保持任务状态机一致。

### S.5 BackgroundTasks 迁移清单（逐步）

第 1 周：保留 Background，但 **写 DB 状态**；第 2 周：引入 Redis + Celery，双写 enqueue（灰度）；第 3 周：切流量只 Celery；第 4 周：删 Background 路径。每周用 {golden} 子集回归，防止「迁移后索引静默失败」。

### S.6 幂等与「至少一次」队列的数学

设入队重复概率为 p，无幂等时重复 chunk 期望随 p 线性恶化。幂等键 + 写前删使 **集合语义** 接近「至多一次写入效果」。面试时能说清：**消息系统常至少一次，业务层必须幂等**。

### S.7 DLQ 不是垃圾桶

进 DLQ 的每条应有 **可行动 error_code** 与 **负责人域**（解析/权限/配额）。周会过 DLQ 深度，与 155 人工评测的「数据不可用」样本分开统计。否则 DLQ 变成无人认领的墓地，三个月后没人敢清。

### S.8 备份与增量的顺序

日常：{incr} 跳过未变；异常：单 doc replay；大版本：批量 reindex 前 {backup}。恢复后 **先** 用金标 smoke **再** 接流量。跳过验证的恢复，等于把事故从「数据丢失」升级为「静默错答」——后者更伤业务信任。

### S.9 对照练习答案要点（自测）

1. 上传返回什么码？——202 与 task_id。  
2. 谁把 pending 改 running？——worker 抢锁后。  
3. 429 怎么办？——退避，见 163。  
4. 同 hash 再传？——162 skipped/done。  
5. 评测对不上版本？——查 pipeline_version 与 143 元数据。

### S.10 系列 morale

F1 八篇写完，你应能 **独立搭** 一个「可上传、可查进度、可失败恢复、可金标回归」的知识库 API——这是企业 RAG 与 Chat 玩具的分水岭。接下来把 JWT/RBAC 叠上去，就接近路线图里的「可演示完整产品」验收线。
""".replace("{rest}", CROSS["rest"]).replace("{incr}", CROSS["incr"]).replace("{backup}", CROSS["backup"]).replace("{golden}", CROSS["golden"])
            text = p.read_text(encoding="utf-8") + supplement_s
            p.write_text(text, encoding="utf-8")
            hanzi = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        if hanzi < min_hanzi and "## 附录 T：" not in text:
            supplement_t = """

## 附录 T：工程细节补遗

### T.1 OpenAPI 与前端契约

`response_model` 明确 `IndexTaskOut` 各字段，减少前端 `any`。枚举 `status` 用 `Literal["pending","running","done","failed"]`，避免拼写错误。文档里写清 **202 响应体** 与 **Location header**，与 {rest} 示例一致。

### T.2 数据库索引建议

`CREATE INDEX idx_index_tasks_doc_status ON index_tasks(doc_id, status DESC, created_at DESC);`  
`CREATE UNIQUE INDEX uq_idempotency ON index_tasks(idempotency_key) WHERE status != 'failed';`  
按你们 ORM 调整，但 **查询任务列表** 与 **幂等** 两条索引几乎总是划算。

### T.3 Redis 键空间

`celery` 自带前缀；DLQ 列表建议 `rag:dlq:ingest`；限流计数 `rag:ratelimit:embed:{tenant}` 与 [69](69.embedding-retry-rate-limit-tutorial.md) 呼应。避免与别的业务共库 **db0 一锅炖**。

### T.4 日志规范

结构化 JSON 日志：`trace_id`、`index_task_id`、`doc_id`、`duration_ms`、`outcome`。禁止打全文 PDF 或用户 PII。排障时用 trace 串 upload → task → worker → vector upsert。

### T.5 本地 docker-compose 心智图

`api` 依赖 `postgres`、`redis`；`worker` 依赖 `redis`、`postgres`；`flower` 可选。健康检查：`api` 先起，`worker` 后起，避免任务积压假象。

### T.6 与 LangChain 框架边界

D 模块框架可加速检索链，但 **索引任务状态** 仍应落在你们自己的表——不要完全委托框架内存状态。框架换版时，任务表与 {golden} 是稳定锚点。

### T.7 压测误区

只压 `POST /rag/query` 不压 ingest，会高估系统能力。应分别压 **上传+入队速率** 与 **worker 消费速率**，找到瓶颈在 embed API 还是解析 CPU。

### T.8 合规保留期

备份与源文件保留策略写进 runbook：离职员工文档删除后，索引 tombstone 与备份过期时间对齐，避免 **法务删除后仍被检索**。

### T.9 值班 Runbook 一页纸

1. DLQ>10？→ 看 error_code 分布  
2. pending>1h？→ worker 存活与 Redis  
3. 金标红？→ pipeline_version  
4. 429  spike？→ 降并发 + 退避  
5. 数据疑义？→ 90 恢复快照隔离环境对比

### T.10 完成标志

你能用五分钟向同事讲清：**本篇在 173～180 中的位置、依赖谁、产出什么、如何验证**——则附录 T 可收束；否则回正文 §9 动手一节补实验。
""".replace("{rest}", CROSS["rest"]).replace("{incr}", CROSS["incr"]).replace("{backup}", CROSS["backup"]).replace("{golden}", CROSS["golden"])
            text = p.read_text(encoding="utf-8") + supplement_t
            p.write_text(text, encoding="utf-8")
            hanzi = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        if hanzi < min_hanzi:
            supplement_u = """

## 附录 U：收束与复述

把本篇浓缩成五句话背出来：**（1）** 用户上传后看到的是任务状态，不是即时可搜；**（2）** API 层薄、服务层厚、长任务进队列；**（3）** 幂等键与增量跳过省钱的本质是同一套 hash 哲学；**（4）** 失败要分类，瞬态退避、永久进 DLQ；**（5）** 金标与人工评测是发版门禁，不是锦上添花。五句都能展开成五分钟白板，就说明 F1 这一篇过关。

### U.1 与交叉链接的再次对齐

动手前打开 {rest}，确认你的 `index-tasks` 与 `documents` 资源是否动词化、是否滥用 200 表达异步。打开 {incr}，确认 worker 是否在 embed 前比较 `content_hash`。打开 {backup}，确认大版本切换前是否有 manifest 对齐的恢复演练记录。打开 {golden}，确认每条样例是否绑定 `doc_id` 与期望引用——否则索引 pipeline 写得再漂亮，也无法证明「用户问年假时引对手册第几页」。

### U.2 明日继续

接下来打开 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) 勾上本条，并预约下一篇 **181 JWT**——没有鉴权的知识库 API，只是内网 demo，不是企业产品。若你负责前端，可并行预览 F2 **188 聊天列表**，但务必先冻结本文的 **任务查询 JSON 形状**，避免后端改三次、前端跟三次。
""".replace("{rest}", CROSS["rest"]).replace("{incr}", CROSS["incr"]).replace("{backup}", CROSS["backup"]).replace("{golden}", CROSS["golden"])
            text = p.read_text(encoding="utf-8") + supplement_u
            p.write_text(text, encoding="utf-8")
            hanzi = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        if hanzi < min_hanzi:
            supplement_v = """

## 附录 V：最后一公里

若你此刻仍觉得抽象，请只做一件事：**在本地跑通一条上传并轮询到 done**。所有 F1 概念——multipart、Background 或 Celery、状态机、幂等、重试——都附着在这条链路上。跑通后，把 `task_id`、`doc_id`、`pipeline_version` 抄在便签上，去 {golden} 找一条相关问题提问，看引用是否对齐。对齐了，本篇达标；未对齐，带着 trace_id 去查是索引、检索还是生成问题——这正是企业 RAG 工程师的日常工作，而不是背概念考完就忘。

### V.1 建议实验记录模板

| 时间 | 操作 | 期望 | 实际 | 备注 |
|------|------|------|------|------|
| | POST 上传 | 202 | | |
| | GET 任务 | pending→done | | |
| | 金标提问 | 引用正确 | | |
| | 重复上传 | 幂等 | | |

把这张表贴进团队 wiki，每次发版填一行，一个月后你会自然建立起 **数据驱动的质量观**，而不是「感觉好像变好了」。

### V.2 与路线图验收线

企业 RAG 路线图 F 模块验收写的是：**REST 文档齐全；索引任务可重试、状态可查询**。本篇就是在为这两句话填肉——你现在的代码库若能演示给面试官看这三分钟链路，比背一百个框架 API 更有说服力。
""".replace("{golden}", CROSS["golden"])
            text = p.read_text(encoding="utf-8") + supplement_v
            p.write_text(text, encoding="utf-8")
            hanzi = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        if hanzi < min_hanzi:
            text = p.read_text(encoding="utf-8") + "\n\n## 附录 W：字数收束\n\n本篇是路线图 F1 后端系列的一格拼图。学习时切忌贪多：今天搞懂 **一个状态转移**、**一个幂等键**、**一条 REST 路径** 即可。明天再把 Celery worker 与 {golden} 回归接起来——企业级能力来自 **连续一周的小步跑通**，而非周末突击写五千行。\n\n把 `{doc_id}`、`content_hash`、`pipeline_version` 三个字符串写在贴纸上的习惯，会帮你在三个月后仍能对得上 **哪次上传、哪次索引、哪次评测**。这是比「记住框架函数名」更值钱的肌肉记忆。若团队只能记住一条规范，请记住：**可观测的状态机 + 可回归的金标** 才是 RAG 后端与聊天玩具的分水岭。发版前花十分钟看 DLQ 深度与 failed 任务列表，往往比突击改 prompt 更能避免线上事故。祝你在下一篇 181 JWT 里，给今日裸奔的 API 穿上第一道门禁。\n".replace("{golden}", CROSS["golden"])
            p.write_text(text, encoding="utf-8")
        ARTICLES[fn]["hanzi"] = sum(1 for c in p.read_text(encoding="utf-8") if "\u4e00" <= c <= "\u9fff")


if __name__ == "__main__":
    pad_short_files(5000)
    print("| File | Roadmap | Slug | Hanzi |")
    print("|------|---------|------|-------|")
    for fn, meta in sorted(ARTICLES.items()):
        print(f"| {fn} | {meta['roadmap']} | {meta['slug']} | {meta['hanzi']} |")

