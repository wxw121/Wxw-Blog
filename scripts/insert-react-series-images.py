#!/usr/bin/env python3
"""Insert infographic refs into react/*.md (reuse nextjs-* PNGs where topics align)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG_REF = re.compile(r"!\[[^\]]*\]\(\.\./image/[^)]+\)")

# article path under repo root -> [(anchor_substring, image_dir, png, alt), ...]
INSERTIONS: dict[str, list[tuple[str, str, str, str]]] = {
    "react/02.vite-jsx-first-component.md": [
        (
            "通俗说：`index.html` 留一个空插座 `#root`，`main.jsx` 把整棵组件树插上去。",
            "nextjs-02-first-page",
            "01-directory-map.png",
            "Vite React 项目目录地图",
        ),
        (
            "**数据通常从上往下流**（父 → 子 via props）。",
            "nextjs-02-first-page",
            "02-layout-page-link.png",
            "组件树：父传 props、子回调通知父",
        ),
    ],
    "react/03.use-effect-data-fetching.md": [
        (
            "本篇**先用 `[]`** 做「进页面拉一次列表」。依赖数组的精细行为系列进阶再讲。",
            "nextjs-03-server-client",
            "01-server-client-compare.png",
            "对照 Next：Vite 默认全在浏览器，列表用 useEffect + fetch",
        ),
        (
            "这叫 **早返回**（Early Return）：主界面逻辑留在最后，上面专门挡 loading/error。第二篇 §6.4 条件渲染的实战版。",
            "nextjs-03-server-client",
            "02-data-flow.png",
            "Vite 客户端取数：挂载 → fetch → setState → 渲染",
        ),
        (
            "本篇不展开配置项；**记住：前端 `fetch('/api/users')` 的 path 要和 REST 文档一致**。",
            "nextjs-03-server-client",
            "03-self-check.png",
            "自检：这段请求代码该放哪个组件",
        ),
    ],
    "react/04.react-router-list-detail.md": [
        (
            "| `/users/:id` | `UserDetailPage` | `GET .../users/:id` |",
            "nextjs-03-server-client",
            "02-data-flow.png",
            "列表页与详情页：各路由各拉各的数据",
        ),
    ],
    "react/05.forms-post-create-user.md": [
        (
            "所以前端要 **提交中禁用按钮**。",
            "nextjs-04-server-actions",
            "04-02-post-create-flow.png",
            "POST 创建用户全流程（Vite 客户端 fetch）",
        ),
        (
            "## 5. fetch 发 POST：method、headers、body",
            "nextjs-04-server-actions",
            "04-01-client-vs-server-action.png",
            "Vite 路线：浏览器 fetch POST（对照 Next Server Actions）",
        ),
        (
            "`disabled={submitting}` 防止连点两次 POST——对应 REST 里 POST 非幂等。",
            "nextjs-04-server-actions",
            "04-03-form-states-redirect.png",
            "提交三态：idle / submitting / error 与跳转",
        ),
    ],
    "react/06.fullstack-vite-fastapi.md": [
        (
            "浏览器里你访问的是 **5173**；`fetch('/api/users')` 的 host 也是 5173——再由 Vite **转发**到 8000。",
            "nextjs-05-fullstack-fastapi",
            "05-01-dual-port-architecture.png",
            "全栈联调：5173 与 8000",
        ),
        (
            "初学 **优先 A**：前端代码里 URL 永远是 **`/api/users`**，不写死后端 host，和生产用 Nginx 反代的思路接近。",
            "nextjs-05-fullstack-fastapi",
            "05-02-rewrites-two-paths.png",
            "Vite 代理 vs 直连后端：两条请求路径",
        ),
        (
            "3. 重启 **仅后端** 后人数回 2——说明数据在内存，未接数据库（预期行为）。",
            "nextjs-05-fullstack-fastapi",
            "05-03-two-terminals-crud.png",
            "两个终端 · CRUD 联调闭环",
        ),
    ],
    "react/07.sse-streaming-chat.md": [
        (
            "| 取消 | 关页面即可（进阶用 Abort） | **应**提供停止按钮 |",
            "nextjs-07-sse-streaming",
            "07-01-json-vs-streaming.png",
            "一次性 JSON vs 流式 SSE",
        ),
        (
            "预期行为：后端每推一个 `data: {\"token\":\"你\"}`，`onToken` 就被调用一次，参数为 `\"你\"`。",
            "nextjs-07-sse-streaming",
            "07-02-sse-read-pipeline.png",
            "readSSEStream · 从字节到 token",
        ),
        (
            "前置：§5 `readSSEStream`、§6 `AbortController`。",
            "nextjs-07-sse-streaming",
            "07-03-handle-send-flow.png",
            "handleSend · 聊天状态机",
        ),
    ],
    "react/08.markdown-message-render.md": [
        (
            "读图时看数据流：**流式只改字符串**；是否排版由 `ChatMessage` 内是否调用 `react-markdown` 决定——不必为 Markdown 单独改 state 结构。",
            "nextjs-08-markdown-render",
            "08-01-markdown-pipeline.png",
            "从 SSE 到排版 DOM",
        ),
        (
            "| `react-markdown` + **`rehype-raw`** | ⚠️ 慎用 | 允许原始 HTML 进 DOM，需配合 `rehype-sanitize` |",
            "nextjs-08-markdown-render",
            "08-02-xss-safe-render.png",
            "AI 输出怎么渲染才安全？",
        ),
        (
            "- 进阶：节流 `setState`（第七篇 FAQ）、或用专门 tolerant 解析器——日常可跳过。",
            "nextjs-08-markdown-render",
            "08-03-streaming-strategy-ab.png",
            "流式半截 Markdown · 策略 A vs B",
        ),
    ],
    "react/09.citation-source-ui.md": [
        (
            "| 侧栏 `SourcePanel` | 展示当前选中引用的 `snippet` 全文 |",
            "nextjs-09-citation-ui",
            "09-02-content-vs-citations.png",
            "正文与出处 · 别混在一个字段",
        ),
        (
            "**为何 citations 放在流末尾？**",
            "nextjs-09-citation-ui",
            "09-01-sse-dual-events.png",
            "SSE 双事件 · token 与 citations 分两路",
        ),
        (
            "发送新问题时是否清空侧栏——产品选择；建议在 `handleSend` 开头 `setActiveCitation(null)`，避免张冠李戴。",
            "nextjs-09-citation-ui",
            "09-03-chat-sidebar-flow.png",
            "聊天 + 侧栏 · 数据流与布局",
        ),
    ],
}


def insert_after_anchor(content: str, anchor: str, img_dir: str, png: str, alt: str) -> str:
    img_line = f"![{alt}](../image/{img_dir}/{png})"
    if img_line in content:
        return content
    idx = content.find(anchor)
    if idx == -1:
        raise ValueError(f"Anchor not found: {anchor!r}")
    line_end = content.find("\n", idx)
    if line_end == -1:
        line_end = len(content)
    insert_at = line_end + 1
    return content[:insert_at] + f"\n{img_line}\n" + content[insert_at:]


def main() -> None:
    updated = 0
    for article, items in INSERTIONS.items():
        path = ROOT / article
        if not path.exists():
            print(f"SKIP missing: {article}")
            continue
        content = path.read_text(encoding="utf-8")
        if len(IMG_REF.findall(content)) >= len(items):
            print(f"SKIP already done: {article}")
            continue
        for anchor, img_dir, png, alt in items:
            png_path = ROOT / "image" / img_dir / png
            if not png_path.exists():
                raise FileNotFoundError(png_path)
            content = insert_after_anchor(content, anchor, img_dir, png, alt)
        path.write_text(content, encoding="utf-8")
        print(f"OK {article}: {len(items)} images")
        updated += 1
    print(f"\nDone: {updated} articles updated")


if __name__ == "__main__":
    main()
