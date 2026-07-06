---
layout: bento-grid
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Title: 排错常备命令速查

Cell1 journalctl -u svc -f --since "1 hour ago"
Cell2 tail -n 200 -f /var/log/nginx/error.log
Cell3 grep -R "ERROR" /var/log --include="*.log"
Cell4 df -h && du -sh /*
Cell5 ss -tlnp | grep 8000
Cell6 ps aux | grep uvicorn

Bottom: 在服务器上先 whoami 确认权限
