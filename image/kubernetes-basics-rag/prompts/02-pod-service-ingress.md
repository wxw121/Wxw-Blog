---
layout: linear-progression
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create educational infographic 16:9, linear-progression left-to-right.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, Simplified Chinese.

Title: 流量路径：Pod → Service → Ingress

Steps:
1. Pod（api 容器，多副本）
2. Service ClusterIP（稳定虚拟 IP + DNS api.rag.svc）
3. Ingress（TLS 终止，/api 路由）
4. 用户浏览器 HTTPS

Callout: Pod 会重启换 IP，Service 不变

Footer: Kubernetes 基本概念 · §5
