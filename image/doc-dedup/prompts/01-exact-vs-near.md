---

layout: binary-comparison

style: hand-drawn-edu

aspect_ratio: 16:9

language: zh

---

Create educational infographic 16:9, hand-drawn-edu, Simplified Chinese.

Title: 精确去重 vs 近似去重

LEFT peach「精确 hash SHA-256」:
- 字节级完全一致才重复
- 改一个标点 → 不同 hash
- 适合防重复上传同一文件

RIGHT mint「近似 SimHash」:
- 正文改几个字仍相近
- 汉明距离小 → 近重复
- 适合 v1/v1.1 制度稿

Bottom: RAG 两者都要：省存储 + 减检索噪音

Footer: 文档去重 · §3
