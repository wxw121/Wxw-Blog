# -*- coding: utf-8 -*-
"""Remove duplicate generic pad sections; ensure >=5000 hanzi."""
import re
from pathlib import Path

FILES = [
    "87.ann-recall-latency-tutorial.md",
    "88.metadata-filter-retrieval-tutorial.md",
    "89.multi-tenant-namespace-tutorial.md",
    "90.vector-db-backup-tutorial.md",
    "91.dense-retrieval-tutorial.md",
    "92.sparse-retrieval-rag-tutorial.md",
    "93.hybrid-search-tutorial.md",
    "94.rrf-fusion-tutorial.md",
]

GENERIC_HEADERS = (
    "## 系列衔接与复习要点",
    "## 工程实践补充",
)

# One extra substantive block per file if below 5000 after dedup
TOPUP = {
"89.multi-tenant-namespace-tutorial.md": """
## 10.8 租户隔离评审终检

上线前由安全与架构联合签字：JWT 注入 tenant 已实现；跨租户自动化测试全绿；备份路径含 tenant_id；删除租户 runbook 已演练；配额与限流已配置；与 [88](88.metadata-filter-retrieval-tutorial.md) ACL 双层文档已归档。任一项缺失则 **延期上线**，不以「先上再补」替代。
""",
"90.vector-db-backup-tutorial.md": """
## 10.5 备份 owner 周常事务

每周一检查备份 job 成功率与快照体积曲线；每月核对 manifest 字段完整率；每季 restore drill 填表归档。与 [87](87.ann-recall-latency-tutorial.md) 共用 probe query 包，减少重复维护。新 embed 模型发布前 **必须** 新 manifest 版本号，禁止覆盖旧 manifest 无审计。
""",
"91.dense-retrieval-tutorial.md": """
## 10.7 Dense 流水线评审要点

评审 PR 时检查：embed 模型与 manifest 一致；normalize 与 metric 与 [26][66] 一致；ANN 参数来自 [87] 曲线；chunk_id 与 sparse 路一致 [92]；filter 在 query 路径 [88]。五项齐再合并，避免「能跑 demo」与「能上线」混淆。
""",
"92.sparse-retrieval-rag-tutorial.md": """
## 10.7 稀疏路季度维护

每季度更新领域词典；检查 ES mapping 与 analyzer 版本；跑单号类回归集三十条；与 dense 路 chunk 数对齐；Hybrid [93] 分路贡献率无异常骤降。稀疏路无人维护时 **六个月** 后往往成为 hybrid 隐形短板。
""",
"93.hybrid-search-tutorial.md": """
## 10.6 Hybrid 生产就绪清单

双路 filter 等价测试通过；RRF 参数文档化；并行与超时已配置；降级开关已演练；四列消融报告归档；rerank [95] 串联契约测试通过。缺一项标为 **beta**，不对全量客户承诺 SLA。
""",
"94.rrf-fusion-tutorial.md": """
## 11.9 RRF 上线检查

每路输入已排序验证；rank 1-based 单测覆盖；chunk_id 规范化；与 [93] orchestrator 日志字段对齐；ES rank_constant 与自研 k 映射表已 wiki。上线后首周 **每日** 抽查十条融合日志，确认无未排序路输入。
""",
"88.metadata-filter-retrieval-tutorial.md": """
## 10.7 过滤规则变更流程

任何 metadata 或 filter 规则变更须：更新 schema 文档；跑三用户矩阵；跑带 filter 的 recall 子集 [87]；更新混合检索双路契约 [93]；安全签字。紧急变更事后 **四十八小时内** 补全渗透与文档。
""",
"87.ann-recall-latency-tutorial.md": """
## 10.11 索引 owner 月度例行

每月对比 N 增长与 P95 趋势；recall 周回归无连续下跌；efSearch 配置与 manifest 一致；差集报告有新簇则评估 embed 或分块。将 CSV 与曲线 **至少保留十二个月** 便于跨年对比。
""",
}

MARKER = "## 综合概念地图"


def remove_duplicate_sections(text: str, header: str) -> str:
    parts = text.split(header)
    if len(parts) <= 2:
        return text
    # keep first occurrence: parts[0] + header + parts[1], drop parts[2:]
    # parts[1] is content until next header - we need to find where section ends
    # Simpler: regex remove all but first
    pattern = re.compile(
        r"(?m)^" + re.escape(header) + r"\n.*?(?=^(?:## |\Z))",
        re.DOTALL,
    )
    matches = list(pattern.finditer(text))
    if len(matches) <= 1:
        return text
    for m in reversed(matches[1:]):
        text = text[: m.start()] + text[m.end() :]
    return text


def main():
    root = Path(__file__).parent
    for fname in FILES:
        path = root / fname
        text = path.read_text(encoding="utf-8")
        for h in GENERIC_HEADERS:
            text = remove_duplicate_sections(text, h)
        hz = len(re.findall(r"[\u4e00-\u9fff]", text))
        if hz < 5000 and fname in TOPUP:
            text = text.replace(MARKER, TOPUP[fname] + "\n\n" + MARKER, 1)
        path.write_text(text, encoding="utf-8")
        hz2 = len(re.findall(r"[\u4e00-\u9fff]", text))
        print(f"{fname}: {hz} -> {hz2} hanzi")


if __name__ == "__main__":
    main()
