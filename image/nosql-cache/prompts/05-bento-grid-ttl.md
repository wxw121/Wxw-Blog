---
layout: bento-grid
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational infographic in hand-drawn-edu style: warm cream paper background (#F5F0E8), macaron pastel rounded cards,
hand-drawn wobble lines, stick-figure characters, clock doodles, Chinese text labels, landscape 16:9.
Layout: Bento grid with 4 cells around a central TTL concept
All visible text in Chinese (简体中文).

Title: TTL 过期时间——缓存不会永远新鲜

Central hero:
TTL = Time To Live（存活时间）
「这条缓存最多活多久，到期自动消失」

Cell 1 - 为什么需要 TTL:
- 商品价格会变
- 用户信息会更新
- 不能永远读旧数据
- 防止内存被塞满

Cell 2 - 常见设置:
- 热点商品：5~30 分钟
- 用户 Session：24 小时
- 验证码：5 分钟
- 配置信息：1 小时

Cell 3 - Redis 命令示例:
SET product:1001 "{...}" EX 300
→ 300 秒后自动删除

Cell 4 - TTL 过期的效果:
时间到 → key 消失
下次读取 → 缓存未命中
→ 重新从数据库加载

Bottom takeaway:
「TTL 是缓存的保鲜期，太短频繁打库，太长数据过时」
