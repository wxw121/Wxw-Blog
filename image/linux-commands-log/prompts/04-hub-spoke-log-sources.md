---
layout: hub-spoke
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Title: Linux 日志从哪来？

Central: 你的应用出了错

Spoke1 systemd journal: journalctl -u nginx
Spoke2 /var/log/: syslog nginx/postgresql
Spoke3 Docker: docker compose logs -f web
Spoke4 应用自己写的: logs/app.log
Spoke5 云平台: 云监控/日志服务

Bottom: 先问「谁在管这个进程」
