# Structured Content: Markdown 渲染与安全完全指南信息图

## Title
Markdown 渲染与安全：从排版到 XSS 防护

## Learning Objectives
1. 看清 Markdown → DOM 的 remark/rehype 管线
2. 对比四种渲染路径的 XSS 风险
3. 决策：默认 react-markdown 还是 raw+sanitize

---

## 图1: 渲染管线（§3）

**Key Concept**: 安全策略挂在 remark/rehype 各关

**Content**:
Markdown 字符串 → remark 解析 → mdast 语法树 → mdast → hast → hast HTML 树 → rehype 插件 → React 组件 / DOM

- remark：认 #、*、链接语法的「Markdown 专家」
- rehype：管 h1、pre 怎么生成、要不要删 script 的「HTML 专家」
- react-markdown：终点是 React 组件树，不是 innerHTML 字符串

**Visual Element**: linear-progression horizontal 6-node pipeline

**Text Labels**:
- Headline: 渲染管线：从字符串到 DOM
- Nodes: Markdown 字符串 / remark / mdast / hast / rehype / React·DOM
- Footer: 安全策略可挂在解析、AST、消毒、CSP 多层

---

## 图2: 四种渲染路径风险对照（§7）

**Key Concept**: 排版能力越大，攻击面往往越大

**Content**:
| 路径 | XSS 风险 | 排版能力 | RAG 助手推荐 |
| 纯文本 | 很低 | 低 | 流式阶段 |
| innerHTML | 很高 | 高 | ❌ |
| react-markdown 默认 | 低 | 中高 | ✅ |
| raw + sanitize | 中（配置不当则高） | 高 | ⚠️ 有需求再做 |

**Visual Element**: comparison-matrix 2x2 or 4-row matrix

**Text Labels**:
- Headline: 四种渲染路径与风险对照
- Rows: 纯文本 / innerHTML / react-markdown / raw+sanitize
- Footer: 禁止不可信 innerHTML

---

## 图3: 选型决策树（§13.2）

**Key Concept**: 能不 raw 就不 raw

**Content**:
```
要渲染助手 Markdown？
├─ 否 → 纯文本，流式/历史皆然
└─ 是 → 能用 react-markdown 默认？
    ├─ 是 → + remark-gfm；链接/图片自定义；流式结束后再渲染
    └─ 必须支持内联 HTML？
        ├─ 是 → rehype-raw + rehype-sanitize（紧 schema）+ CSP
        └─ 否 → 不要加 raw
```

**Visual Element**: tree-branching decision flow

**Text Labels**:
- Headline: Markdown 渲染安全决策树
- Leaves: 纯文本 / react-markdown+GFM / raw+sanitize+CSP / 不要加 raw
- Footer: 模型输出不可信

---

## Design Instructions
hand-drawn-edu, landscape 16:9, Simplified Chinese
