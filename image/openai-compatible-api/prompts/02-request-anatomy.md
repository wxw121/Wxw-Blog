---

layout: annotated-diagram

style: hand-drawn-edu

aspect_ratio: 16:9

language: zh

---



Create educational infographic 16:9, hand-drawn-edu, Simplified Chinese.



Title: Chat Completions 请求解剖



Show JSON box with callouts:

- model（chat 模型名）

- messages[]（system/user/assistant）

- temperature / max_tokens（可选）



Response side: choices[0].message.content, usage tokens



Arrow: POST /v1/chat/completions



Footer: OpenAI 兼容 API · §5

