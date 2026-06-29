---
layout: bento-grid
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational infographic in hand-drawn-edu style: warm cream paper background (#F5F0E8), macaron pastel rounded cards
(mint #B5E5CF, blue #A8D8EA, lavender #D5C6E0, peach #FFD5C2), hand-drawn wobble lines,
stick-figure characters, doodle decorations, Chinese text labels, landscape 16:9, generous whitespace.
Layout: Multi-panel bento grid overview
All visible text in Chinese (简体中文).
Content to visualize faithfully:
风险 1: 未加密的连接
┌────────────────────────────────────────────────────┐
│ ❌ ws://  明文传输，中间人可以看到所有消息            │
│ ✅ wss:// TLS 加密，和 HTTPS 一样安全                │
│                                                    │
│ 生产环境必须用 wss://，就像必须用 https:// 一样       │
└────────────────────────────────────────────────────┘

风险 2: 未验证的连接
┌────────────────────────────────────────────────────┐
│ WebSocket 握手是 HTTP 请求——你可以在握手阶段           │
│ 验证身份（cookie、token、API key）。                    │
│                                                    │
│ 不要在 WebSocket 消息里传 token——在握手时验证。        │
│                                                    │
│ ✅ 做法:                                            │
│ const ws = new WebSocket(                          │
│   `wss://api.example.com/ws?token=${accessToken}`  │
│ );                                                 │
│                                                    │
│ 服务端在握手时验证 token，不合法就返回 401 拒绝升级     │
└────────────────────────────────────────────────────┘

风险 3: 跨站 WebSocket 劫持 (Cross-Site WebSocket Hijacking)
┌────────────────────────────────────────────────────┐
│ 恶意网站可能用你的 cookie 建立 WebSocket 连接。       │
│                                                    │
│ 防御:                                              │
│ • 服务端验证 Origin 头                              │
│ • 用 token 而非 cookie 做认证                       │
│ • 设置严格的 CORS                                   │
└────────────────────────────────────────────────────┘

风险 4: 消息轰炸
┌────────────────────────────────────────────────────┐
│ 客户端可以疯狂发消息——比 HTTP 请求更难限流。          │
│                                                    │
│ 防御:                                              │
│ • 服务端做频率限制（按连接计数，不是按 IP）            │
│ • 设置最大消息大小（如 64KB）                        │
│ • 对广播消息做内容过滤                               │
└────────────────────────────────────────────────────┘

风险 5: 拒绝服务 (DoS)
┌────────────────────────────────────────────────────┐
│ 攻击者建立大量 WebSocket 连接但不发数据              │
│                                                    │
│ 防御:                                              │
│ • 限制单个 IP 最大连接数                            │
│ • 设置连接最长空闲时间                              │
│ • 设置心跳检测，静默连接主动断开                     │
│ • 设置全局最大连接数                                │
└────────────────────────────────────────────────────┘