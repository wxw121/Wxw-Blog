---
layout: bento-grid
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: bento-grid, 6 cards.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: 编码检测概念速记

Cards:
1. (large) 文本 = 字节 + 解码规则（charset）
2. Mojibake：编码假设错了的可读 garbage
3. UTF-8：现代默认；GBK：中文遗留常见
4. chardet：老牌猜测库，置信度要读
5. charset-normalizer：更积极、可 normalize 到 UTF-8
6. RAG：ingest 前统一 UTF-8，元数据记原编码

Bottom: open(..., encoding='utf-8') 不够，要先认文件

Footer: 纯文本与编码检测完全指南 · §10

All text Simplified Chinese.
