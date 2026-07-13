---

layout: comparison-matrix

style: hand-drawn-edu

aspect_ratio: 16:9

language: zh

---



Create a professional educational infographic, 16:9 landscape.

Layout: comparison-matrix — left: HTTP 429 response anatomy; right: client action checklist.

Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.



Title: 429 Too Many Requests 与限流响应头



Left panel — 响应解剖:

- Status: 429 Too Many Requests

- Header: Retry-After: 3（秒）

- Header: x-ratelimit-remaining: 0

- Header: x-ratelimit-reset: 1710000000

- Body: rate limit exceeded



Right panel — 客户端应对:

- 读 Retry-After，优先按其等待

- 无头则用指数退避

- 不要立即无限重试

- 记录 attempt 与 batch_id 便于幂等



Footer: Embedding API 重试与限流 · §5



All text Simplified Chinese.

