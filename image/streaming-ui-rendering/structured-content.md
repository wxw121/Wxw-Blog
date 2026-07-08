# Structured Content: 流式 UI 渲染完全指南信息图

## Title
流式 UI 渲染：逐字显示、中断与用户感知

## Learning Objectives
1. 区分传输层流式与展示层流式
2. 掌握聊天 UI 五态状态机
3. 理解发送→chunk追加→停止的端到端流程

---

## 图1: 传输层 vs 展示层（§2）

**Key Concept**: 服务器推流 ≠ 打字机效果，两层可解耦

**Content**:
| 层次 | 决定什么 | 典型 API |
| 传输层 | 多快收到第一块数据 | POST /chat/stream、SSE |
| 展示层 | 多快画到屏幕上 | setState、Vue ref、节流 |

传输层：服务器生成 → HTTP 长连接/SSE → readSSEStream/getReader
展示层：更新 messages state → ChatBubble 重绘 → 用户看到字变长

**Visual Element**: binary-comparison, left transport, right display, pipeline connecting them

**Text Labels**:
- Headline: "两层问题：传输流式 vs 界面流式"
- Left: 传输层 · 水管里的水一股一股来
- Right: 展示层 · 杯子接到一点倒一点给用户看
- Footer: "R 之后才是本篇重点"

---

## 图2: UI 状态机（§12.2）

**Key Concept**: streaming 是唯一显示停止、禁用输入的状态

**Content**:
- idle → streaming: 用户发送
- streaming → done: 流正常结束
- streaming → aborted: 用户点停止
- streaming → error: 网络/服务端错误
- done / aborted / error → idle: 可再次发送

**Visual Element**: circular-flow or state diagram with 5 nodes

**Text Labels**:
- Headline: "聊天 UI 状态机"
- Nodes: idle / streaming / done / aborted / error
- Callout: streaming 时显示停止按钮、禁用输入
- Footer: "中断是正常路径，不是异常"

---

## 图3: 端到端数据流（§12.3）

**Key Concept**: 发送→读流→追加→停止的完整链路

**Content**:
1. 用户点击发送
2. UI 追加 user + 空 assistant
3. fetch + signal → 流式 API
4. loop 每个 chunk: API 返回文本 → content += chunk
5. 用户点停止 → abort() → status=aborted, idle

**Visual Element**: linear-progression horizontal sequence with 5-6 steps

**Text Labels**:
- Headline: "端到端：从发送到停止"
- Steps: 发送 / 追加消息 / fetch+signal / chunk追加 / 流结束或abort
- Footer: "一条 assistant = 一个气泡，content 追加 chunk"

---

## Design Instructions
- hand-drawn-edu, landscape 16:9, Simplified Chinese
