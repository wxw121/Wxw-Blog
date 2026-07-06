---
layout: hub-spoke
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational hub-spoke, hand-drawn-edu, cream paper, Chinese, landscape 16:9.
Title: Docker Compose 多服务架构一览

Central hub: docker-compose.yml
「一个文件定义整套服务」

Spoke 1 web 服务:
FastAPI / Nginx
ports 8000:8000

Spoke 2 db 服务:
PostgreSQL
volume 持久化数据

Spoke 3 cache 服务:
Redis
内部网络访问

Spoke 4 网络 network:
服务用服务名互访 db:5432

Spoke 5 数据卷 volumes:
数据库文件落盘

Bottom: docker compose up -d 一键拉起
