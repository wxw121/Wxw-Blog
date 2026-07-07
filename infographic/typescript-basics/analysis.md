---
title: "TypeScript 基础完全指南配图"
topic: educational/technical
data_type: process/comparison/hierarchy/overview
complexity: complex
point_count: 16
source_language: zh
user_language: zh
---

## Main Topic
TypeScript 基础地基教程：从「JavaScript 加类型」到读懂现代前端 `.ts` / `.tsx` 代码。涵盖超集关系、静态检查流程、工具链、基础类型、对象描述、联合与收窄、泛型入门及常见陷阱。

## Learning Objectives
After viewing these infographics, the viewer should understand:
1. TypeScript 与 JavaScript 的关系，以及类型在编译后擦掉、运行的是 JS
2. 静态检查三阶段（编辑时 / 构建时 / 运行时）各自管什么
3. 本章核心类型名词（`: string`、`interface`、`A | B`、`<T>` 等）及其典型场景
4. 何时值得学 TypeScript 的决策路径

## Target Audience
- **Knowledge Level**: 能读现代 JavaScript 的初学者
- **Context**: 读 React/Next 教程时被 `interface`、`string | null` 拦住，需要地基概念
- **Expectations**: 快速建立 TS 全局地图，能对照文章章节查阅

## Content Type Analysis
- **Data Structure**: 概念递进（是什么→怎么检查→工具链→类型语法→综合地图→决策）
- **Key Relationships**: JS⊃TS 超集；.ts→检查→.js→运行时；类型世界 vs 值的世界
- **Visual Opportunities**: 流程图（§3 mermaid）、概念对照表（§14）、决策树（§16.2）、JS vs TS 对照（§2）

## Key Data Points (Verbatim)
- "TypeScript（类型脚本）：由微软维护的开源语言，语法是 **JavaScript 的超集**（superset）。"
- "编译（compile，编译）：把一种语言翻译成另一种，这里指把 TS **擦掉类型**并转成目标版本的 JS。"
- "动态类型（dynamic typing）：变量**不绑定**固定类型……类型错误多在**运行**时暴露。"
- "静态类型（static typing）：在**不运行程序**的情况下，根据源码里的类型标注和推断，检查赋值、传参是否匹配。"
- "1. **编辑时**：IDE 用 TS 语言服务标红、补全。 2. **构建时**：`tsc` 或 Vite/Webpack 里的 TS 插件 3. **运行时**：**没有** TS 类型警察"
- "TS = JS + 静态类型；类型在编译后擦掉，运行的是 JS。"
- "`any`：关闭对该值的类型检查，**传染性**强"
- "`unknown`：表示「不知道类型」，但**不能**直接当具体类型用，必须先**收窄**"

## Layout × Style Signals
- Content type: process + overview → suggests `linear-progression`, `bento-grid`, `tree-branching`
- Tone: 教学向、初学者友好 → suggests `hand-drawn-edu`（EXTEND.md 偏好）
- Audience: 前端初学者 → hand-drawn macaron pastels, stick figures
- Complexity: complex (16 sections) → 拆成 3 张图，各聚焦一个章节锚点

## Design Instructions (from user input)
- BLOG 项目第十三篇文档配图
- 格式参考 `.baoyu-skills/baoyu-infographic/EXTEND.md`
- preferred_style: hand-drawn-edu
- preferred_aspect: landscape (16:9)
- language: zh

## Recommended Combinations
1. **linear-progression + hand-drawn-edu** (Recommended for 图1): §3 静态检查三阶段流程，步骤清晰
2. **bento-grid + hand-drawn-edu** (Recommended for 图2): §14 综合概念地图，多模块并列
3. **tree-branching + hand-drawn-edu** (Recommended for 图3): §16.2 何时上 TypeScript 决策树
4. **binary-comparison + hand-drawn-edu**: §2 JS vs TS 或 §5.3 any vs unknown 对照（备选单图）
5. **hub-spoke + hand-drawn-edu**: 以「TS = JS + 类型」为中心辐射核心概念（备选总览图）
