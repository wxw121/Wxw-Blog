---

layout: flow-diagram

style: hand-drawn-edu

aspect_ratio: 16:9

language: zh

---

Create educational infographic 16:9, hand-drawn-edu, Simplified Chinese.

Title: 文本清洗流水线

Flow left to right:

1 原始抽取文本（多源）
2 编码统一 UTF-8（链 48）
3 空白规范化
4 乱码检测 / 剔除
5 页眉页脚规则
6 控制字符清理
7 净文本 → 分块

Branch: 失败样本进人工队列

Footer: 文本清洗 · §7 流水线
