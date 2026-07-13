---

layout: decision-tree

style: hand-drawn-edu

aspect_ratio: 16:9

language: zh

---



Create a professional educational infographic, 16:9 landscape.

Layout: decision-tree — top question branching to actions.

Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.



Title: 换模型还是微调 Embedding？



Root: 检索 Recall 不达标？



Branch A (是通用说法/多语): → 先换 bge-m3 / 更大模型 / 混合检索

Branch B (是领域黑话密集): → 收集 (query, 正例, 负例) 对

Branch C (数据 < 500 对): → 先换模型 + rerank，暂不微调

Branch D (数据 ≥ 数千对 + 评测集): → 考虑 Embedding 微调



Leaf notes:

- 微调不是默认项

- 换模型要重建索引



Footer: Embedding 微调概念完全指南 · §4



All text Simplified Chinese.

