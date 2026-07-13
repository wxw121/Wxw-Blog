---

layout: flow-diagram

style: hand-drawn-edu

aspect_ratio: 16:9

language: zh

---

Create educational infographic 16:9, hand-drawn-edu, Simplified Chinese.

Title: Unstructured 统一分区入口

CENTER hub「partition()」:
- 一个函数吃多种格式
- PDF / DOCX / HTML / PPTX / 图片…

LEFT inputs（小图标）:
- 企业知识库多格式文件
- 不再为每种格式写 if-else 链

RIGHT outputs:
- 元素列表 List[Element]
- Title / NarrativeText / Table…
- 可接清洗、分块、Embedding

Bottom arrow flow:
文件 → partition → 元素流 → RAG ingest

Footer: Unstructured.io · §3 统一入口
