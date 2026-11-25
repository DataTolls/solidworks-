# -*- coding: utf-8 -*-
"""扫描 预览图/ 下的 PNG，按类别前缀分组，重建 README.md 中的作品画廊。

用法：python tools/generate_gallery.py
新增图片后重跑一次即可，画廊位于 <!-- GALLERY:START --> 与 <!-- GALLERY:END --> 之间。
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREVIEW_DIR = os.path.join(ROOT, "预览图")
README = os.path.join(ROOT, "README.md")

START = "<!-- GALLERY:START -->"
END = "<!-- GALLERY:END -->"

CATEGORY_ORDER = ["曲面造型", "钣金件", "工程机械", "五金件", "家电数码", "生活文创"]
COLS = 3
IMG_WIDTH = 220


def build_gallery():
    files = sorted(f for f in os.listdir(PREVIEW_DIR) if f.lower().endswith(".png"))
    groups = {}
    for filename in files:
        stem = os.path.splitext(filename)[0]
        category = stem.split("-", 1)[0]
        groups.setdefault(category, []).append(stem)

    lines = []
    for category in CATEGORY_ORDER:
        items = groups.pop(category, [])
        if not items:
            continue
        lines.append("### {} · {} 项".format(category, len(items)))
        lines.append("")
        lines.append("|" + "|".join([" :--: "] * COLS) + "|")
        for i in range(0, len(items), COLS):
            cells = []
            for stem in items[i:i + COLS]:
                cells.append(
                    '<img src="预览图/{s}.png" width="{w}"><br>[{s}.SLDPRT](./{s}.SLDPRT)'.format(
                        s=stem, w=IMG_WIDTH
                    )
                )
            while len(cells) < COLS:
                cells.append("")
            lines.append("| " + " | ".join(cells) + " |")
        lines.append("")

    for category in sorted(groups):  # 出现新前缀时兜底，不丢图
        items = groups[category]
        lines.append("### {} · {} 项".format(category, len(items)))
        lines.append("")
        lines.append("|" + "|".join([" :--: "] * COLS) + "|")
        for i in range(0, len(items), COLS):
            cells = []
            for stem in items[i:i + COLS]:
                cells.append(
                    '<img src="预览图/{s}.png" width="{w}"><br>[{s}.SLDPRT](./{s}.SLDPRT)'.format(
                        s=stem, w=IMG_WIDTH
                    )
                )
            while len(cells) < COLS:
                cells.append("")
            lines.append("| " + " | ".join(cells) + " |")
        lines.append("")

    return START + "\n\n" + "\n".join(lines).rstrip() + "\n\n" + END


def main():
    with open(README, "r", encoding="utf-8") as fh:
        text = fh.read()
    block = build_gallery()
    updated, count = re.subn(
        re.escape(START) + r".*?" + re.escape(END),
        lambda _m: block,
        text,
        flags=re.S,
    )
    if count != 1:
        raise SystemExit("README.md 中未找到唯一的画廊标记块，已中止")
    with open(README, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(updated)
    print("画廊已重建：{} 张预览图".format(
        len([f for f in os.listdir(PREVIEW_DIR) if f.lower().endswith(".png")])
    ))


if __name__ == "__main__":
    main()
