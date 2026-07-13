---

layout: linear-progression

style: hand-drawn-edu

aspect_ratio: 16:9

language: zh

---



Create a professional educational infographic, 16:9 landscape.

Layout: linear-progression — left to right pipeline with 4 boxes.

Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.



Title: 本地 Embedding 推理技术栈



Box 1: HuggingFace 模型权重

- BAAI/bge-small-zh-v1.5

- 下载到本地缓存



Arrow →



Box 2: sentence-transformers

- SentenceTransformer.encode()

- batch + normalize_embeddings



Arrow →



Box 3 (optional branch): ONNX Runtime

- 导出 .onnx 加速 CPU

- 标签：低延迟 CPU 部署



Arrow →



Box 4: 向量输出

- float32 数组

- 送入 FAISS / pgvector



Footer note: GPU 用 PyTorch CUDA；CPU 小模型 + ONNX 常见



Footer: 本地 Embedding 推理完全指南 · §5



All text Simplified Chinese.

