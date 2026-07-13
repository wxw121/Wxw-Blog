---
layout: binary-comparison
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: binary-comparison wrong vs right.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: 乱码 Mojibake：字节对了，解码错了

Left — 错误解码:
- 文件本是 UTF-8，用 GBK 打开
- 显示「锟斤拷」「烫烫烫」类乱码
- 火柴人皱眉看日志

Right — 正确解码:
- 检测/声明编码 → UTF-8 读入
- 中文正常显示
- 火柴人点头

Center: 乱码 ≠ 文件损坏，常是 charset 不匹配

Bottom: 先检测再 decode，别默认 cp1252

Footer: 纯文本与编码检测完全指南 · §3

All text Simplified Chinese.
