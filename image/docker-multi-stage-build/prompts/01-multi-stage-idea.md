---
layout: comparison-matrix
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: comparison-matrix — two columns side by side.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: 单阶段 vs 多阶段：最终镜像里有什么？

Left column (red tint header): 单阶段镜像
- python:3.11 全量基础镜像
- build-essential、git 留在最终层
- pip 缓存与 pytest 打进镜像
- 体积 1.5GB+，攻击面大

Right column (green tint header): 多阶段镜像
- Stage builder：gcc + pip install → /install
- Stage runtime：python:3.11-slim
- COPY --from=builder 只拿 wheel
- 无编译器，体积约 1/3

Footer: Docker 多阶段构建完全指南 · §3

All text Simplified Chinese.
