# -*- coding: utf-8 -*-
"""扫描 预览图/ 下的 PNG，生成 README.md 中的作品目录表格。

生成结果是一张单一、纵向的 Markdown 表格，全列居中对齐，按类别排序，
每行一项作品；新增图片后重跑一次即可，区块位于
<!-- GALLERY:START --> 与 <!-- GALLERY:END --> 之间。

用法：python tools/generate_gallery.py
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREVIEW_DIR = os.path.join(ROOT, "预览图")
README = os.path.join(ROOT, "README.md")

START = "<!-- GALLERY:START -->"
END = "<!-- GALLERY:END -->"

CATEGORY_ORDER = ["曲面造型", "钣金件", "工程机械", "五金件", "家电数码", "生活文创"]
STEP_DIR = "该目录下的SW跨版本兼容模型"
IMG_WIDTH = 220


def collect_items():
    """返回 [(类别, 模型名), ...]，按受控词表顺序排列，同类内按名称排序。"""
    files = sorted(f for f in os.listdir(PREVIEW_DIR) if f.lower().endswith(".png"))
    groups = {}
    for filename in files:
        stem = os.path.splitext(filename)[0]
        category = stem.split("-", 1)[0]
        groups.setdefault(category, []).append(stem)

    ordered = []
    for category in CATEGORY_ORDER:
        ordered += [(category, stem) for stem in sorted(groups.pop(category, []))]
    for category in sorted(groups):  # 出现新前缀时兜底，不丢图
        ordered += [(category, stem) for stem in sorted(groups[category])]
    return ordered


def build_table():
    items = collect_items()
    lines = [
        "共 **{}** 项作品，按类别顺序纵向排列，向下滚动即可浏览全部内容。".format(len(items)),
        "",
        "| 序号 | 预览图 | 作品名称 | 类别 | 源文件下载 |",
        "|:---:|:---:|:---:|:---:|:---:|",
    ]
    for index, (category, stem) in enumerate(items, 1):
        image = '<a href="./{s}.SLDPRT"><img src="预览图/{s}.png" width="{w}" alt="{s}"></a>'.format(
            s=stem, w=IMG_WIDTH
        )
        download = '[SLDPRT](./{s}.SLDPRT)<br>[STEP](./{d}/{s}.STEP)'.format(
            s=stem, d=STEP_DIR
        )
        lines.append("| {n:02d} | {img} | **{s}** | {c} | {dl} |".format(
            n=index, img=image, s=stem, c=category, dl=download
        ))
    return START + "\n\n" + "\n".join(lines) + "\n\n" + END


def main():
    with open(README, "r", encoding="utf-8") as fh:
        text = fh.read()
    block = build_table()
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
    print("目录表已重建：{} 项作品".format(len(collect_items())))


if __name__ == "__main__":
    main()
