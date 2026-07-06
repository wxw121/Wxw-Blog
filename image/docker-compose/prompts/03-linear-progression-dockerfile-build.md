---
layout: linear-progression
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational linear progression, hand-drawn-edu, cream paper, Chinese, landscape 16:9.
Title: 从 Dockerfile 到镜像：构建流水线

Horizontal steps:
Step 1: 写 Dockerfile（FROM, COPY, RUN, CMD）
Step 2: docker build -t myapp:1.0 .
Step 3: Docker 按层缓存构建镜像
Step 4: docker images 看到新镜像
Step 5: docker run myapp:1.0 启动容器

Side note: .dockerignore 排除无关文件

Bottom: Dockerfile 是镜像的「菜谱」
