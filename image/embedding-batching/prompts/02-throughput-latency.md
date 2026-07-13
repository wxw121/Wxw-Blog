---
layout: comparison-matrix
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: comparison-matrix — batch_size small vs large tradeoff.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: 吞吐 vs 延迟 vs 内存（Throughput vs Latency）

Left column: batch_size = 1
- 延迟低，单条快返回
- 吞吐差，索引 10k 要 10k 次请求
- 适合在线单条查询 embed

Right column: batch_size = 64～256
- 吞吐高，索引任务快完成
- 单 batch 延迟略升
- 内存占用随 batch 增大

Center: 甜蜜点需压测 + 厂商限流

Footer: 批量 Embedding 完全指南 · §5

All text Simplified Chinese.
