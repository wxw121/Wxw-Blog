---

layout: flowchart

style: hand-drawn-edu

aspect_ratio: 16:9

language: zh

---



Create a professional educational infographic, 16:9 landscape.

Layout: flowchart top-down decision tree.

Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.



Title: 变更检测：mtime 粗筛 + hash 确认



Steps:

1. 扫描源目录 → 当前快照

2. mtime 没变？→ 快路径跳过

3. mtime 变了 → 算 content_hash

4. hash 与 catalog 相同？→ 只更新 mtime，跳过 embed

5. hash 不同 → 进入 reindex pipeline

6. 差集检出 removed 文档



Side note: 目录表 catalog = 调度真相



Bottom: 误报变更用 hash 消掉；别只信 mtime



Footer: 增量更新与变更检测完全指南 · §5



All text Simplified Chinese.

