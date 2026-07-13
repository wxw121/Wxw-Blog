---
layout: flowchart
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create educational infographic 16:9, hand-drawn-edu, Simplified Chinese.

Title: 越权泄露风险链路

Flowchart top to bottom:
1. 索引未写 acl → 全库可检索
2. 检索未过滤 → 机密 chunk 进 top-k
3. 拼进 prompt → 模型复述机密
4. 用户截图外传 → 合规事故

Side branch coral 补救:
- 入库写 acl
- 检索带 filter
- 日志审计 chunk_ids
- 拒答不能替代权限

Footer: ACL 访问控制元数据 · §7

All text Simplified Chinese.
