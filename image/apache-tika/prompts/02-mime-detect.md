---

layout: binary-comparison

style: hand-drawn-edu

aspect_ratio: 16:9

language: zh

---

Create educational infographic 16:9, hand-drawn-edu, Simplified Chinese.

Title: MIME 检测：扩展名不可信

LEFT peach「只看扩展名」:
- report.pdf 其实是 ZIP
- data.txt 其实是 HTML
- ingest 走错解析器 → 乱码或空

RIGHT mint「Tika detect」:
- 读文件头魔数
- 输出 application/pdf 等 MIME
- 再选对应 Parser 抽文本

Bottom: RAG 应用层应信 MIME + 内容嗅探，不信用户上传文件名

Footer: Apache Tika · §5 MIME
