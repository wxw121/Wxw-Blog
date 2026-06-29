"""Copy generated assets to manifest img_path locations."""
import json
import os
import shutil

BLOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 生成图资产目录，默认 <仓库>/assets；也可用环境变量 BLOG_ASSETS_DIR 覆盖
ASSETS = os.environ.get("BLOG_ASSETS_DIR", os.path.join(BLOG, "assets"))

# Manual mapping: generated asset basename -> manifest img_path
COPY_MAP = {
    "01-binary-comparison-sync-async.png": "image/python-asyncio/01-binary-comparison-sync-async.png",
    "02-bento-grid-kitchen-analogy.png": "image/python-asyncio/02-bento-grid-kitchen-analogy.png",
    "03-tree-branching-when-async.png": "image/python-asyncio/03-tree-branching-when-async.png",
    "04-linear-progression-coroutine-lifecycle.png": "image/python-asyncio/04-linear-progression-coroutine-lifecycle.png",
    "05-hub-spoke-event-loop.png": "image/python-asyncio/05-hub-spoke-event-loop.png",
    "06-tree-awaitable-hierarchy.png": "image/python-asyncio/01-comparison-matrix-diagram-01.png",
    "07-linear-gather-timeline.png": "image/python-asyncio/08-linear-gather-timeline.png",
    "08-linear-semaphore-timeline.png": "image/python-asyncio/09-linear-semaphore-timeline.png",
    "09-hub-spoke-crawler-architecture.png": "image/python-asyncio/03-comparison-matrix-异步爬虫架构.png",
    "10-linear-producer-consumer.png": "image/python-asyncio/04-comparison-matrix-生产者-消费者-流水线.png",
    "11-comparison-sync-async-libs.png": "image/python-asyncio/05-comparison-matrix-diagram-05.png",
    "12-bento-async-four-cores.png": "image/python-asyncio/06-bento-grid-diagram-06.png",
    "13-tree-when-use-asyncio.png": "image/python-asyncio/07-comparison-matrix-需要处理大量-I-O-操作.png",
}


def main():
    for src_name, rel_path in COPY_MAP.items():
        src = os.path.join(ASSETS, src_name)
        dst = os.path.join(BLOG, rel_path)
        if not os.path.isfile(src):
            print(f"SKIP missing: {src_name}")
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        print(f"OK {rel_path}")


if __name__ == "__main__":
    main()
