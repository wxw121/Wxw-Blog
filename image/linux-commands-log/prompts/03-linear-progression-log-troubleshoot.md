---
layout: linear-progression
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Title: 日志排查六步法

Step1 确认症状 接口502/磁盘满/CPU高
Step2 找日志在哪 journalctl docker logs /var/log
Step3 缩小时间范围 --since 最近30分钟
Step4 grep 关键词 ERROR Exception
Step5 对照代码或配置
Step6 验证修复 再看日志

Bottom: 别一上来就 rm -rf
