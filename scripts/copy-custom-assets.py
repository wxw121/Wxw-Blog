"""Copy prefixed asset files to manifest img_path (explicit map + basename)."""
import json
import os
import shutil

BLOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 生成图资产目录，默认 <仓库>/assets；也可用环境变量 BLOG_ASSETS_DIR 覆盖
ASSETS = os.environ.get("BLOG_ASSETS_DIR", os.path.join(BLOG, "assets"))

CUSTOM = {
    "ra-05-url-design.png": "image/rest-api-design/05-bento-grid-diagram-05.png",
    "ra-07-status-codes.png": "image/rest-api-design/07-bento-grid-diagram-07.png",
    "ra-08-error-format.png": "image/rest-api-design/08-comparison-matrix-diagram-08.png",
    "11-bento-grid-方式一-API-Key-最简单-适合服务间调用.png": "image/rest-api-design/11-bento-grid-方式一-API-Key-最简单-适合服务间调用.png",
    "12-comparison-matrix-资源关系图.png": "image/rest-api-design/12-comparison-matrix-资源关系图.png",
    "13-comparison-matrix-diagram-13.png": "image/rest-api-design/13-comparison-matrix-diagram-13.png",
    "14-comparison-matrix-你的-API-给谁用.png": "image/rest-api-design/14-comparison-matrix-你的-API-给谁用.png",
    "15-bento-grid-diagram-15.png": "image/rest-api-design/15-bento-grid-diagram-15.png",
    "09-bento-grid-401-Unauthorized-未认证.png": "image/rest-api-design/09-bento-grid-401-Unauthorized-未认证.png",
    "10-binary-comparison-三种分页方式对比.png": "image/rest-api-design/10-binary-comparison-三种分页方式对比.png",
    "ws-01-websocket-vs-http.png": "image/websocket/01-bento-grid-diagram-01.png",
    "ws-02-handshake.png": "image/websocket/02-bento-grid-diagram-02.png",
}


def main():
    n = 0
    for src_name, rel in CUSTOM.items():
        src = os.path.join(ASSETS, src_name)
        dst = os.path.join(BLOG, rel)
        if not os.path.isfile(src):
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        n += 1
        print(f"OK {rel}")
    print(f"Copied {n}")


if __name__ == "__main__":
    main()
