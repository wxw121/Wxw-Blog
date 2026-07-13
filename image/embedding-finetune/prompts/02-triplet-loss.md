---

layout: hub-spoke

style: hand-drawn-edu

aspect_ratio: 16:9

language: zh

---



Create a professional educational infographic, 16:9 landscape.

Layout: hub-spoke — anchor at center, positive and negative around.

Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.



Title: Triplet Loss：拉近正例、推远负例



Center: Anchor 锚点（用户 query 或 chunk）



Right (green): Positive 正例 — 应该检索到的文档句

- 箭头：距离缩短



Left (red): Negative 负例 — 不应排前面的相似句

- 箭头：距离拉大



Bottom formula box (simplified, no heavy math):

Loss = max(0, d(a,p) - d(a,n) + margin)



Footer note: 生产常用 (query, pos, neg) 三元组；Hard negative 挖掘是难点



Footer: Embedding 微调概念完全指南 · §6



All text Simplified Chinese.

