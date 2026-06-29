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
401 Unauthorized (未认证)
┌─────────────────────────────────────────────┐
│ "我不知道你是谁"                             │
│                                             │
│ 场景:                                        │
│ • 没有提供 token                             │
│ • token 过期                                │
│ • token 格式不对                             │
│                                             │
│ 响应: 告诉客户端「你需要先登录」               │
│ 客户端应该: 跳转到登录页                      │
└─────────────────────────────────────────────┘

403 Forbidden (未授权)
┌─────────────────────────────────────────────┐
│ "我知道你是谁，但你不能做这个操作"             │
│                                             │
│ 场景:                                        │
│ • 普通用户试图访问管理员功能                   │
│ • 用户试图修改他人的资源                      │
│                                             │
│ 响应: 告诉客户端「你没权限做这个」              │
│ 客户端应该: 提示用户「无权操作」               │
└─────────────────────────────────────────────┘