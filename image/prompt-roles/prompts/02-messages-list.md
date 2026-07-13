---
layout: linear-progression
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create educational infographic 16:9, hand-drawn-edu, Simplified Chinese.

Title: API 吃的是 messages 列表

Flow left to right:
1. [{role, content}, …] 数组
2. system 在前（契约）
3. 多轮 user / assistant 交替追加
4. chat.completions.create
5. 返回新的 assistant 文本 → 写回列表

Bottom: 调试时先打印整份 messages，不要只看最后一句

Footer: System/User/Assistant 完全指南 · §4
