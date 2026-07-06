---
layout: bento-grid
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational bento grid, hand-drawn-edu, cream paper, Chinese, landscape 16:9.
Title: Docker Compose 常用命令速查

Cell 1 docker compose up -d
后台启动所有服务

Cell 2 docker compose down
停止并删除容器和网络（默认不删 volume；加 -v 才删卷）

Cell 3 docker compose ps
查看运行状态

Cell 4 docker compose logs -f web
跟踪某个服务日志

Cell 5 docker compose exec db psql
进入容器执行命令

Cell 6 docker compose build
重新构建镜像

Bottom: 在 compose.yml 所在目录执行
