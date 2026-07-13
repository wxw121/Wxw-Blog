---
layout: linear-flow
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create educational infographic 16:9, hand-drawn-edu, Simplified Chinese.

Title: RAG ingest 中的 OCR 流水线

Flow left to right:
上传 PDF/图片 → 按页探测文本层 → 分支（有层 / 需 OCR）→ 渲染 pixmap 300 DPI → Tesseract 或云 OCR → 文本清洗 → 分块 → Embedding → 向量库

Side note box: metadata 含 page · extraction_method · ocr_engine · confidence

Footer: OCR 与扫描件 · §5

All text Simplified Chinese.
