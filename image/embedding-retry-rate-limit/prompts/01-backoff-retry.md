---

layout: linear-progression

style: hand-drawn-edu

aspect_ratio: 16:9

language: zh

---



Create a professional educational infographic, 16:9 landscape.

Layout: linear-progression — horizontal timeline showing retry attempts with increasing wait intervals.

Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.



Title: 指数退避（Exponential Backoff）重试节奏



Timeline nodes (left to right):

- 第 1 次请求 → 429 限流

- 等待 1s + jitter → 第 2 次请求 → 仍 429

- 等待 2s + jitter → 第 3 次请求 → 仍 429

- 等待 4s + jitter → 第 4 次请求 → 200 成功



Bottom callout boxes:

- 基础延迟 × 2^attempt

- 加随机抖动 jitter 防惊群

- 设 max_retries 与 max_wait 上限



Footer: Embedding API 重试与限流 · §4



All text Simplified Chinese.

