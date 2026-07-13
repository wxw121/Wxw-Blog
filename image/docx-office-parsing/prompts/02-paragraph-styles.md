---
layout: flowchart
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: top-down flowchart with style boxes.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: DOCX 段落与样式：分块靠它

Flow:
1. Document 打开 .docx
2. 遍历 paragraphs（段落）
3. 读 paragraph.style.name → Heading 1 / Normal / List Bullet
4. 分支：Heading → 新 section 标题；Normal → 正文 chunk
5. 页眉页脚单独过滤（可选）

Side boxes:
- runs：同一段落内加粗/斜体片段
- tables：表格另走 table.rows 路径

Bottom: 样式名比「字号猜标题」稳

Footer: DOCX / Office 文档解析完全指南 · §4

All text Simplified Chinese.
