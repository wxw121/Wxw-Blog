---
layout: hub-spoke
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: hub-spoke.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: RAG 结构化输出链路

Center hub: 检索 → LLM JSON → parse → 业务

Spoke 1: 生成
- response_format
- JSON Schema
Spoke 2: 解析
- json.loads + Pydantic
- 字段校验
Spoke 3: 引用
- citations[]
- 113/114 对齐
Spoke 4: 拒答
- refusal 字段
- 112 统一

Footer: 结构化输出 JSON Mode完全指南 · §3 结构化输出是什么

All text Simplified Chinese.
