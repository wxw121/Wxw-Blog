---
title: "Markdown 渲染与安全完全指南配图"
topic: educational/technical/security
data_type: process/comparison/hierarchy
complexity: complex
point_count: 15
source_language: zh
user_language: zh
---

## Main Topic
Markdown 渲染与安全地基：从 remark/rehype 管线到 XSS 攻击面、信任边界、四种渲染路径与消毒策略。

## Learning Objectives
1. 理解 Markdown 字符串 → remark → rehype → React/DOM 的渲染管线
2. 对比纯文本、innerHTML、react-markdown、raw+sanitize 的风险
3. 用决策树选择安全的助手消息渲染路径

## Target Audience
- **Knowledge Level**: 会 React/HTML 基础的初学者
- **Context**: RAG 聊天要上 Markdown 排版，担心 XSS
- **Expectations**: 选对渲染管道，知道何时消毒

## Content Type Analysis
- **Data Structure**: 管线流程 → 攻击面 → 信任边界 → 路径对照 → 决策树
- **Key Relationships**: 不可信 content → 解析 → DOM；raw 与 sanitize 成对
- **Visual Opportunities**: §3 mermaid 管线、§7 四路径表、§13.2 决策树

## Key Data Points (Verbatim)
- "Markdown 渲染：把 Markdown 源码字符串转成浏览器里的标题、段落、列表、代码块等结构化 UI"
- "存储型 XSS：恶意内容存进数据库，别人打开页面就触发"
- "模型输出不可信——与用户信息同级防护，禁止不可信 innerHTML"
- "react-markdown 默认：高安全、中高排版、✅ RAG 助手推荐"
- "innerHTML：很高风险、❌"

## Design Instructions
- BLOG 第十六篇；输出 `image/markdown-rendering-security/`
- EXTEND.md: hand-drawn-edu, landscape 16:9, zh

## Recommended Combinations
1. **linear-progression + hand-drawn-edu** (图1 §3): 渲染管线
2. **comparison-matrix + hand-drawn-edu** (图2 §7): 四种渲染路径风险对照
3. **tree-branching + hand-drawn-edu** (图3 §13.2): 选型决策树
