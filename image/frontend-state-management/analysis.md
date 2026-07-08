---
title: "前端状态管理完全指南配图"
topic: educational/technical
data_type: comparison/process/hierarchy/overview
complexity: complex
point_count: 13
source_language: zh
user_language: zh
---

## Main Topic
前端客户端全局状态管理地基教程：从 useState、Context 到 Zustand、Redux、Pinia，以及与 TanStack Query（服务端状态）的分工选型。

## Learning Objectives
After viewing these infographics, the viewer should understand:
1. 客户端状态与服务端状态的区别及各自该用什么工具
2. Redux 单向数据流：UI → dispatch(action) → reducer → 新 state → UI
3. Zustand / Redux / Pinia 选型决策路径
4. 遇到问题该用 useState、Context、Store 还是 Query

## Target Audience
- **Knowledge Level**: 会 React useState 或 Vue ref 的初学者
- **Context**: 多页面状态不同步、prop drilling 痛点，需要选型
- **Expectations**: 建立「先分类再选库」的全局地图

## Content Type Analysis
- **Data Structure**: 二分（客户端/服务端）→ 递进手段 → 三库对比 → 决策树 → 概念地图
- **Key Relationships**: Query 管 API 缓存；Store 管 UI/会话；URL 管可分享状态
- **Visual Opportunities**: §2 双 subgraph 流程图、§5.2 单向数据流、§9.2 决策树、§11 概念表

## Key Data Points (Verbatim)
- "客户端状态：由浏览器端产生、主要服务于 UI 交互，不一定有对应「数据库里的一行」。"
- "服务端状态：权威数据在服务器，前端通过 HTTP/WebSocket **取副本** 展示；服务器上别人改了，你的副本会**过期**。"
- "左边适合本篇三类库；右边适合 Query 一类"
- "UI → dispatch(action) → reducer → 新 state → UI 重渲染"
- "React：TanStack Query（documents、user profile）+ Zustand（sidebar、theme、activeChatId）"

## Layout × Style Signals
- Content type: comparison + process + decision → binary-comparison, linear-progression, tree-branching, bento-grid
- Tone: 教学向、选型导向 → hand-drawn-edu（EXTEND.md）
- Complexity: complex → 3 张图各锚定一章

## Design Instructions
- BLOG 第十四篇文档配图
- EXTEND.md: hand-drawn-edu, landscape 16:9, zh

## Recommended Combinations
1. **binary-comparison + hand-drawn-edu** (图1 §2): 客户端 vs 服务端状态对照
2. **linear-progression + hand-drawn-edu** (图2 §5-6): 单向数据流 Redux 叙事核心
3. **tree-branching + hand-drawn-edu** (图3 §9.2): 三库选型决策树
4. **bento-grid + hand-drawn-edu** (备选): §11 综合概念地图
