---

layout: binary-comparison

style: hand-drawn-edu

aspect_ratio: 16:9

language: zh

---

Create educational infographic 16:9, hand-drawn-edu, Simplified Chinese.

Title: 脏文本 vs 净文本（RAG 视角）

LEFT peach「脏文本」:
- 连续空行、全角空格
- 页眉「内部资料」每页重复
- Mojibake 乱码片段
- PDF 断行 hyphen 残留

RIGHT mint「净文本」:
- 统一 UTF-8
- 页眉页脚已剔除
- 空白规范化
- 适合分块与 Embedding

Bottom: 解析抽字 ≠ 可入库；清洗是独立阶段

Footer: 文本清洗 · §3
