---
title: "流式 UI 渲染完全指南配图"
topic: educational/technical
data_type: comparison/process/cycle/overview
complexity: complex
point_count: 14
source_language: zh
user_language: zh
---

## Main Topic
流式 UI 渲染地基教程：传输层流式 vs 展示层流式、打字机效果、聊天状态机、chunk 追加、AbortController 中断、竞态与性能。

## Learning Objectives
1. 区分传输层流式与展示层流式，二者可解耦
2. 掌握聊天 UI 状态机：idle → streaming → done/aborted/error → idle
3. 理解 chunk 追加渲染与 AbortController 中断收尾
4. 识别竞态与常见陷阱

## Target Audience
- **Knowledge Level**: 会 React useState / fetch 的初学者
- **Context**: 做聊天页、需要逐字显示与停止按钮
- **Expectations**: 设计流式聊天 UI 的状态与交互

## Content Type Analysis
- **Data Structure**: 两层分解 → 状态模型 → 追加逻辑 → 中断/竞态 → 状态机总结
- **Key Relationships**: 传输层(SSE/getReader) → 展示层(setState追加) → 用户感知
- **Visual Opportunities**: §2 双层流程图、§3 真/假流式对照、§12.2 状态机、§12.3 时序图

## Key Data Points (Verbatim)
- "传输层流式：一次 HTTP 响应的 body 分多次到达"
- "展示层流式：每收到一段文本，就在 DOM / 虚拟 DOM 里追加到当前气泡"
- "一条回答 = 一个气泡，回答变长 = 同一个气泡里的字变多"
- "content_new = content_old + chunk"
- "idle → streaming → done/aborted/error → idle"

## Design Instructions
- BLOG 第十五篇配图
- EXTEND.md: hand-drawn-edu, landscape 16:9, zh

## Recommended Combinations
1. **binary-comparison + hand-drawn-edu** (图1 §2): 传输层 vs 展示层
2. **circular-flow + hand-drawn-edu** (图2 §12.2): UI 状态机
3. **linear-progression + hand-drawn-edu** (图3 §12.3): 端到端数据流
4. **bento-grid + hand-drawn-edu** (备选): §12.1 综合概念地图
