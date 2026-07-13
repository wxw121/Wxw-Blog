---
layout: hub-spoke
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: hub-spoke — center hub with three spokes.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: 一个 Dockerfile，两个构建目标

Center hub: runtime 阶段
- python:3.11-slim
- COPY --from=builder 依赖
- COPY app 业务代码
- USER appuser

Spoke 1: builder 阶段
- gcc + pip install
- requirements.txt
- requirements-worker.txt

Spoke 2: target api
- CMD uvicorn app.main:app
- EXPOSE 8000
- /health 健康检查

Spoke 3: target worker
- CMD celery worker
- pymupdf 解析 PDF
- ingest 长任务

Footer: RAG FastAPI 多阶段部署 · §9

All text Simplified Chinese.
