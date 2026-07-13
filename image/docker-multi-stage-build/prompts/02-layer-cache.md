---
layout: linear-progression
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Educational linear progression, hand-drawn-edu, cream paper, Chinese, landscape 16:9.
Title: Docker 层缓存：COPY 顺序决定 CI 速度

Horizontal steps (correct order, green checkmarks):
Step 1: FROM python:3.11-slim
Step 2: COPY requirements.txt only
Step 3: RUN pip install（依赖层，很少变）
Step 4: COPY app ./app（业务层，常变）
Step 5: 改一行代码 → 仅 Step 4 重建

Below with red X — wrong order:
COPY . . 在 pip 之前 → 改代码重装全部依赖

Side note: .dockerignore 排除 .venv tests .env

Bottom: 依赖清单先于业务代码 COPY

All text Simplified Chinese.
