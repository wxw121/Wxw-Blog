---
layout: hub-spoke
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: hub-spoke — center "docker compose up", spokes to six services.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: RAG 全栈 Compose 服务拓扑

Center: docker compose（一键编排）

Spokes (clockwise):
1. frontend（Next.js :3000）
2. api（FastAPI :8000）
3. worker（Celery 索引）
4. postgres（元数据）
5. redis（队列 + 缓存）
6. chroma（向量库持久卷）

Side note: 同一 bridge 网络内用服务名互访，如 redis:6379

Footer: Docker Compose 全栈部署 · §3
