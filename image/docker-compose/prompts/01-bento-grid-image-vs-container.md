---
layout: bento-grid
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational infographic, hand-drawn-edu, cream paper, macaron pastels, Chinese, landscape 16:9, bento grid.
Title: Docker 核心三件套：镜像、容器、仓库

Hero: 镜像 = 安装包 / 容器 = 运行中的程序

Cell 1 镜像 Image:
- 只读模板，像 ISO 或安装光盘
- 分层存储，可复用
- 例: postgres:16-alpine

Cell 2 容器 Container:
- 镜像的运行实例
- 可启停删，互不影响
- 类比: 同一张光盘装多台电脑

Cell 3 仓库 Registry:
- 存放镜像的「应用商店」
- Docker Hub 最常用
- docker pull / docker push

Cell 4 关系:
docker pull → docker run → 容器
改容器不自动改镜像

Bottom: 镜像是类，容器是对象
