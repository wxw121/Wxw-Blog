---
layout: hub-spoke
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Educational infographic 16:9 landscape, hand-drawn-edu hub-spoke dual column UI.

Title: 聊天 + 侧栏 · 数据流与布局

CENTER: chat/page.js state
messages[] · activeCitation · isStreaming

LEFT spoke 主栏 flex:1:
ChatMessage Markdown
CitationList 点[1]
onCitationSelect 向上

RIGHT spoke 侧栏 300px:
SourcePanel
显示 snippet
onClose 清空

Flow arrows:
发送→SSE→onCitations→点卡片→setActiveCitation→侧栏snippet

Bottom: props向下 事件向上
Footer: Next.js 学习系列（九)

Simplified Chinese, flex layout sketch.