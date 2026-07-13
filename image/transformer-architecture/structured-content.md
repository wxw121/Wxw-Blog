# Structured Content: Transformer 架构

## Title
Transformer 架构完全指南

## Learning objectives
- 区分 RNN 串行与 Transformer 可并行直觉
- 识别编码器 / 解码器职责
- 将 BERT / GPT / Embedding 归入同一家族
- 说明 RAG 两处接点

## Sections (verbatim key points)

### RNN vs Transformer
- 旧路线必须按顺序；长句远处易淡
- 新路线整句可同时处理；远距离可直接连线
- 训练侧并行优势更明显

### Encoder–Decoder
- 编码器读懂输入
- 解码器写出输出
- 词嵌入、位置编码、自注意力、前馈网络
- 后世常只留解码器

### Family
- BERT 偏读；GPT 偏写；Embedding 偏检索向量
- RAG：Embedding API + Chat API

### Concept map
- 积木地图 → 下一篇注意力显微镜
