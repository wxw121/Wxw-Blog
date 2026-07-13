---
layout: hub-spoke
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create educational infographic 16:9, hub-spoke.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: RAG 组件在 K8s 里长什么样

Center: Kubernetes 集群

Spokes mapping:
- Deployment + Pod → api / worker
- StatefulSet → postgres（或云 RDS 外置）
- Service ClusterIP → redis / chroma 内网
- Ingress → frontend HTTPS 入口
- Secret → OPENAI_API_KEY
- ConfigMap → 非敏感配置

Footer: Kubernetes 基本概念 · §3
