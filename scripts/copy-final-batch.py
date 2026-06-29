"""Final copy of all remaining assets to manifest paths."""
import os
import shutil

BLOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 生成图资产目录，默认 <仓库>/assets；也可用环境变量 BLOG_ASSETS_DIR 覆盖
ASSETS = os.environ.get("BLOG_ASSETS_DIR", os.path.join(BLOG, "assets"))

MAP = {
    "sse-05.png": "image/sse/05-comparison-matrix-diagram-05.png",
    "06-comparison-matrix-你要实现什么功能.png": "image/sse/06-comparison-matrix-你要实现什么功能.png",
    "07-bento-grid-diagram-07.png": "image/sse/07-bento-grid-diagram-07.png",
    "08-bento-grid-diagram-08.png": "image/sse/08-bento-grid-diagram-08.png",
    "ws-03-full-duplex.png": "image/websocket/03-bento-grid-diagram-03.png",
    "04-comparison-matrix-传统-HTTP-请求-响应模型.png": "image/websocket/04-comparison-matrix-传统-HTTP-请求-响应模型.png",
    "ws-05-bento-grid-diagram-05.png": "image/websocket/05-bento-grid-diagram-05.png",
    "ws-06-comparison-matrix-diagram-06.png": "image/websocket/06-comparison-matrix-diagram-06.png",
    "ws-07-bento-grid-diagram-07.png": "image/websocket/07-bento-grid-diagram-07.png",
    "08-comparison-matrix-WebSocket-实例有四个-readyStat.png": "image/websocket/08-comparison-matrix-WebSocket-实例有四个-readyStat.png",
    "09-comparison-matrix-diagram-09.png": "image/websocket/09-comparison-matrix-diagram-09.png",
    "10-bento-grid-diagram-10.png": "image/websocket/10-bento-grid-diagram-10.png",
    "11-comparison-matrix-diagram-11.png": "image/websocket/11-comparison-matrix-diagram-11.png",
    "12-comparison-matrix-你要实现什么功能.png": "image/websocket/12-comparison-matrix-你要实现什么功能.png",
    "13-comparison-matrix-diagram-13.png": "image/websocket/13-comparison-matrix-diagram-13.png",
    "14-bento-grid-风险-1-未加密的连接.png": "image/websocket/14-bento-grid-风险-1-未加密的连接.png",
    "15-bento-grid-diagram-15.png": "image/websocket/15-bento-grid-diagram-15.png",
}


def main():
    for src, rel in MAP.items():
        s = os.path.join(ASSETS, src)
        d = os.path.join(BLOG, rel)
        if not os.path.isfile(s):
            print(f"MISSING {src}")
            continue
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(s, d)
        print(f"OK {rel}")


if __name__ == "__main__":
    main()
