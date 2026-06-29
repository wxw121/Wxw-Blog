---
illustration_id: 05
layout: hub-spoke
style: hand-drawn-edu
aspect: 16:9
language: zh
---

# 事件循环 — 异步引擎

## Center Hub
事件循环调度器（单线程）

## Spokes
- 待执行队列：任务 A B C D
- A await sleep → 暂停 A，调度 B
- B await socket → 暂停 B，调度 C
- C print 执行完毕
- sleep 到期 → 唤醒 A

## Key Insight
单线程协作式调度，CPU 密集会卡住整个循环
