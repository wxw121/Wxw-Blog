---
layout: hub-spoke
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: hub-spoke — center hub with four spokes.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: 知识库文档上传界面是什么？

Center hub: KbUploadPage = 进货口

Spoke 1: Dropzone 拖拽区
- 选 PDF/DOCX/MD
- 前端大小校验

Spoke 2: doc_id 元数据
- 独立业务主键
- 非原始文件名

Spoke 3: multipart 提交
- FormData POST
- 202 + task_id

Spoke 4: 衔接任务
- 161 状态机
- 180 索引进度

Footer: 知识库文档上传界面完全指南 · §3

All text Simplified Chinese.
