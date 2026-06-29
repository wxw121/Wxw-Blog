from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1040, 1720
img = Image.new("RGB", (W, H), "#0f172a")
draw = ImageDraw.Draw(img)

try:
    title_font = ImageFont.truetype("msyh.ttc", 36)
    q_font = ImageFont.truetype("msyh.ttc", 26)
    main_font = ImageFont.truetype("msyhbd.ttc", 28)
    sub_font = ImageFont.truetype("msyh.ttc", 24)
    legend_font = ImageFont.truetype("msyh.ttc", 20)
except OSError:
    title_font = ImageFont.load_default()
    q_font = main_font = sub_font = legend_font = title_font

cx = W // 2
box_w = 840
x0 = (W - box_w) // 2


def text_center(y, text, font, fill="#f8fafc"):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, y), text, font=font, fill=fill)


def rounded_box(y, h, fill, stroke, texts):
    draw.rounded_rectangle(
        [x0, y, x0 + box_w, y + h], radius=16, fill=fill, outline=stroke, width=3
    )
    ty = y + 24
    for i, (text, font, color) in enumerate(texts):
        text_center(ty + i * 34, text, font, color)


def arrow(y1, y2):
    draw.line([(cx, y1), (cx, y2 - 18)], fill="#64748b", width=3)
    draw.polygon([(cx, y2), (cx - 10, y2 - 18), (cx + 10, y2 - 18)], fill="#64748b")


text_center(40, "Python 虚拟环境工具选择", title_font)

y = 110
blocks = [
    (
        "你是一个 Python 新手，想快速上手？",
        [
            ("从 venv 开始", main_font, "#f8fafc"),
            ("理解虚拟环境的核心概念之后，再升级", sub_font, "#94a3b8"),
        ],
        (8, 51, 68),
        "#22d3ee",
        150,
    ),
    (
        "你需要管理正式项目，需要锁文件和统一工具链？",
        [
            ("Poetry 或 uv", main_font, "#f8fafc"),
            ("如果追求速度 → uv", sub_font, "#94a3b8"),
            ("如果要发布包 → Poetry", sub_font, "#94a3b8"),
        ],
        (6, 78, 59),
        "#34d399",
        180,
    ),
    (
        "大型项目，依赖几十上百个包，安装速度让你抓狂？",
        [
            ("uv，毫不犹豫", main_font, "#f8fafc"),
            ("速度差距是数量级", sub_font, "#94a3b8"),
        ],
        (59, 130, 246),
        "#60a5fa",
        150,
    ),
    (
        "你在维护遗留项目，已经有 requirements.txt？",
        [
            ("用 uv pip 兼容模式", main_font, "#f8fafc"),
            ("渐进迁移到 uv", sub_font, "#94a3b8"),
        ],
        (76, 29, 149),
        "#a78bfa",
        150,
    ),
]

for question, answers, rgb, stroke, ah in blocks:
    qh = 96
    rounded_box(y, qh, (120, 53, 15), "#fbbf24", [(question, q_font, "#f8fafc")])
    y += qh + 8
    arrow(y, y + 36)
    y += 44
    rounded_box(y, ah, rgb, stroke, answers)
    y += ah + 36

draw.rounded_rectangle([100, H - 70, 124, H - 46], radius=4, fill=(120, 53, 15), outline="#fbbf24", width=2)
draw.text((136, H - 68), "场景问题", font=legend_font, fill="#94a3b8")
draw.rounded_rectangle([280, H - 70, 304, H - 46], radius=4, fill=(8, 51, 68), outline="#22d3ee", width=2)
draw.text((316, H - 68), "推荐方案", font=legend_font, fill="#94a3b8")

BLOG_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(BLOG_ROOT, "image", "python-tool-choice.png")
img.save(out, "PNG")
print("saved", out)
