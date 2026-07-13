---
layout: binary-comparison
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: binary-comparison UTF-8 vs GBK.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: UTF-8 vs GBK：中文老文件常见坑

Left — UTF-8:
- 变长 1～4 字节，全球 Web 默认
- emoji、多语言友好
- 标签：新项目 · API · JSON

Right — GBK/GB18030:
- 中文 Windows 老系统、部分 CSV/日志
- 双字节为主
- 标签：遗留系统 · 政企内网导出

Center note: Python 3 默认 UTF-8 读写；legacy 文件要显式指定

Bottom: chardet / charset-normalizer 辅助猜测

Footer: 纯文本与编码检测完全指南 · §4

All text Simplified Chinese.
