---
layout: hierarchical-tree
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: hierarchical-tree / document outline from top to bottom.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: Markdown 文档结构：标题树 + 块级元素

Tree structure:
- H1 文档标题
  - H2 第一章
    - 段落文字
    - 无序列表（- item）
    - 有序列表（1. item）
    - H3 小节
      - 段落
      - 围栏代码块 ```python ... ```
  - H2 第二章
    - 引用块 >
    - 表格 | col |

Side notes:
- # 数量 = 标题层级（勿跳级）
- 代码块是原子单元，分块时勿从中间切断
- 列表项宜与所属标题留在同 chunk

Bottom: 解析目标：AST / Token 流，不是纯字符串

Footer: Markdown 解析完全指南 · §4

All text Simplified Chinese.
