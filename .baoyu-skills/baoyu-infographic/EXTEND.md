---
version: 1
preferred_layout: null
preferred_style: hand-drawn-edu
preferred_aspect: landscape
language: zh
preferred_image_backend: auto
output_dir: image
---

# 项目配图约定

- **输出目录**：`image/{topic-slug}/`（PNG 与 `prompts/`、`analysis.md` 等同目录存放）
- **文章引用**：
  - 仓库根目录教程：`![alt](image/{topic-slug}/NN-name.png)`
  - `nextjs/` 子目录教程：`![alt](../image/{topic-slug}/NN-name.png)`
- **勿用** `infographic/` 目录（已废弃，统一迁入 `image/`）
