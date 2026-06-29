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
方式一：API Key（最简单，适合服务间调用）
┌─────────────────────────────────────────────┐
│ GET /api/users                              │
│ Authorization: ApiKey sk-abc123xyz          │
│ 或                                          │
│ X-API-Key: sk-abc123xyz                     │
│                                             │
│ 适用: 机器对机器调用、简单的自动化脚本        │
│ 缺点: key 泄露后任何人都能用，无法区分用户    │
└─────────────────────────────────────────────┘

方式二：Bearer Token / JWT（最流行）
┌─────────────────────────────────────────────┐
│ GET /api/users                              │
│ Authorization: Bearer eyJhbGciOi...          │
│                                             │
│ JWT (JSON Web Token) 结构:                   │
│ eyJhbGciOi.eyJzdWIiOi.xYz                    │
│   Header   .  Payload  . Signature           │
│                                             │
│ Payload 包含: user_id, role, exp(过期时间)    │
│ 适用: Web 应用、移动 App、前后端分离          │
└─────────────────────────────────────────────┘

方式三：OAuth 2.0（适合第三方授权）
┌─────────────────────────────────────────────┐
│ 「用微信登录」「用 Google 登录」的场景         │
│                                             │
│ 适用: 需要第三方授权的场景                    │
│ 复杂: 实现成本高，一般用现成的库              │
└─────────────────────────────────────────────┘