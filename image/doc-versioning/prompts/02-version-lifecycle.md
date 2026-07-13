---

layout: flowchart

style: hand-drawn-edu

aspect_ratio: 16:9

language: zh

---



Create a professional educational infographic, 16:9 landscape.

Layout: two parallel vertical lifecycles (覆盖 vs 留历史).

Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.



Title: 文档版本生命周期



Path A — 覆盖更新:

1. 上传 v3 → 按 doc_id 删旧向量

2. 仅 is_latest 可检索

3. 存储省，历史丢



Path B — 保留历史:

1. 上传 v3 → 新 chunk 写入

2. v2 标 is_latest=false 仍可查

3. 检索默认 filter is_latest



Shared steps: content_hash 检测 → version 递增



Bottom: 混合策略：默认最新 + 后台看历史



Footer: 文档版本管理完全指南 · §5



All text Simplified Chinese.

