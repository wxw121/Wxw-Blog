---

layout: annotated-scene

style: hand-drawn-edu

aspect_ratio: 16:9

language: zh

---

Create educational infographic 16:9, hand-drawn-edu, Simplified Chinese.

Title: SimHash 直觉：指纹相近即近重复

Show two long text blocks A and B:
- 大部分句子相同
- B 多了一段「修订说明」

Process arrows:
- 分词 / shingle → 特征
- 64-bit 指纹
- 汉明距离 = 3（阈值内 → 近重复）

Contrast: SHA-256(A) ≠ SHA-256(B) 完全不同

Footer: 文档去重 · §5 SimHash
