#!/usr/bin/env python3
"""Generate disclosure figures and a Word copy of the technical disclosure."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Polygon
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent
FIG_DIR = ROOT / "附图"
MD_PATH = ROOT / "专利技术交底书.md"
DOCX_PATH = ROOT / "专利技术交底书.docx"
FONT = "WenQuanYi Micro Hei"


def setup_font() -> None:
    plt.rcParams["font.sans-serif"] = [FONT, "Droid Sans Fallback"]
    plt.rcParams["axes.unicode_minus"] = False


def box(ax, xy, w, h, text, fc="#E8F1FB", ec="#1F4E79", fontsize=9):
    x, y = xy
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.2,
        facecolor=fc,
        edgecolor=ec,
    )
    ax.add_patch(patch)
    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color="#1B1B1B",
        wrap=True,
    )
    return (x + w / 2, y, x + w / 2, y + h)


def arrow(ax, p1, p2):
    ax.add_patch(
        FancyArrowPatch(
            p1,
            p2,
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=1.1,
            color="#1F4E79",
            shrinkA=0,
            shrinkB=0,
        )
    )


def save(fig, name: str) -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / name
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def fig1_overall():
    fig, ax = plt.subplots(figsize=(7.2, 10.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 16)
    ax.axis("off")
    ax.set_title("图1  岩芯行检测与回次划分方法总体流程", fontsize=13, pad=8, color="#1F4E79")

    steps = [
        (12.8, "获取岩芯多边形、图像宽高\n以及可选的岩芯牌位置"),
        (11.2, "沿图像宽度划分为若干竖向条带"),
        (9.6, "按条带竖向边界裁剪多边形\n得到各条带内的截面多边形"),
        (8.0, "各条带内对截面中心纵坐标\n做局部行聚类，得到候选行数"),
        (6.4, "对各有效条带行数投票\n得到基准行数N"),
        (4.8, "箱首条带是否为N+1？\n是则做末行不满校验，锁定最终行数"),
        (3.2, "按最终行数，用局部簇中心初始化\n对原始多边形做一次行归属"),
        (1.6, "若有岩芯牌：遇牌结束、无牌延续\n全箱连续编号划分回次"),
        (0.2, "输出行数、行标签、行中心\n以及回次编号与区间"),
    ]
    centers = []
    for y, text in steps:
        cx, y0, _, y1 = box(ax, (1.3, y), 7.4, 1.25, text, fontsize=9.5)
        centers.append((cx, y0, y1))
    for i in range(len(centers) - 1):
        arrow(ax, (centers[i][0], centers[i][1] - 0.04), (centers[i + 1][0], centers[i + 1][2] + 0.04))
    return save(fig, "图1-总体流程.png")


def fig2_clip():
    fig, ax = plt.subplots(figsize=(9.2, 5.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_title("图2  竖向条带划分与多边形截面裁剪示意", fontsize=13, pad=8, color="#1F4E79")

    # image frame
    ax.add_patch(Rectangle((0.6, 1.4), 10.8, 4.6, fill=False, lw=1.6, ec="#333333"))
    # strips
    for i, x in enumerate([0.6, 3.3, 6.0, 8.7]):
        ax.add_patch(Rectangle((x, 1.4), 2.7, 4.6, facecolor="#F7FAFC" if i % 2 == 0 else "#EEF4EA", edgecolor="#7A8B99", lw=0.8))
        ax.text(x + 1.35, 5.75, f"条带{i}", ha="center", va="center", fontsize=10, color="#1F4E79")

    verts = [(1.15, 4.15), (5.15, 3.45), (5.35, 2.55), (1.35, 3.20)]
    ax.add_patch(Polygon(verts, closed=True, facecolor="none", edgecolor="#C0392B",
                         lw=1.6, linestyle="--"))
    left = Polygon([(1.15, 4.15), (3.3, 3.61), (3.3, 2.74), (1.35, 3.20)], closed=True,
                   facecolor="#5B9BD5", edgecolor="#1F4E79", lw=1.5, alpha=0.7)
    right = Polygon([(3.3, 3.61), (5.15, 3.45), (5.35, 2.55), (3.3, 2.74)], closed=True,
                    facecolor="#70AD47", edgecolor="#2E7D32", lw=1.5, alpha=0.7)
    ax.add_patch(left)
    ax.add_patch(right)
    ax.text(7.8, 4.15, "斜跨两条带的岩芯多边形\n（虚线为完整轮廓）", ha="center", fontsize=9, color="#C0392B")
    ax.annotate("", xy=(5.2, 3.5), xytext=(6.6, 4.0),
                arrowprops=dict(arrowstyle="->", color="#C0392B"))
    ax.text(1.95, 1.65, "条带0内的截面\n用该截面中心Y聚类", ha="center", fontsize=9, color="#1F4E79")
    ax.text(4.55, 1.65, "条带1内的截面\n不用整框中心代替", ha="center", fontsize=9, color="#2E7D32")

    ax.text(6.0, 0.55, "竖直线为条带边界；边跨边界时线性插值求交，只保留落在本带内的轮廓。", ha="center", fontsize=9)
    return save(fig, "图2-条带裁剪示意.png")


def fig3_vote():
    fig, ax = plt.subplots(figsize=(8.4, 10.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 15.2)
    ax.axis("off")
    ax.set_title("图3  行数投票、末行不满触发与误增行校验", fontsize=13, pad=8, color="#1F4E79")

    box(ax, (1.0, 13.5), 8.0, 1.15, "各有效条带给出候选行数")
    box(ax, (1.0, 11.85), 8.0, 1.2, "按出现次数投票；众数并列时取较小值\n得到基准行数N")
    box(ax, (1.0, 9.95), 8.0, 1.4, "第0条带（箱首）的候选行数是否等于N+1？", fc="#FFF2CC")
    box(ax, (0.4, 7.55), 4.2, 1.5, "否\n最终行数锁定为N", fc="#FCE4D6")
    box(ax, (5.4, 7.55), 4.2, 1.5, "是：暂定N+1（末行不满）\n第1条带及以后单独N+1不触发", fc="#E2EFDA")
    box(ax, (5.4, 5.35), 4.2, 1.7, "取第1～4条带中恰好为N行者\n比较箱首多出一行与参考末行的Y差", fc="#E2EFDA")
    box(ax, (5.4, 3.15), 4.2, 1.6, "差值比率是否小于阈值？\n阈值＝2×条带内邻域比例", fc="#FFF2CC")
    box(ax, (0.4, 1.15), 4.2, 1.4, "是：判定为假行\n撤销，最终行数改回N", fc="#FCE4D6")
    box(ax, (5.4, 1.15), 4.2, 1.4, "否：两组高度确实分开\n保留最终行数N+1", fc="#E2EFDA")

    arrow(ax, (5, 13.5), (5, 13.05))
    arrow(ax, (5, 11.85), (5, 11.35))
    arrow(ax, (3.0, 9.95), (2.5, 9.05))
    arrow(ax, (7.0, 9.95), (7.5, 9.05))
    arrow(ax, (7.5, 7.55), (7.5, 7.05))
    arrow(ax, (7.5, 5.35), (7.5, 4.75))
    arrow(ax, (6.4, 3.15), (2.5, 2.55))
    arrow(ax, (7.5, 3.15), (7.5, 2.55))
    return save(fig, "图3-投票与末行校验.png")


def fig4_runs():
    fig, ax = plt.subplots(figsize=(9.4, 5.8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.2)
    ax.axis("off")
    ax.set_title("图4  遇牌结束、无牌延续的回次划分示意", fontsize=13, pad=8, color="#1F4E79")

    colors = ["#5B9BD5", "#ED7D31", "#70AD47", "#9B59B6"]
    # rows from top (small Y in image = top of box). Draw 3 rows.
    # Row 0: tag at x=4.2, left run0, right run1
    ax.add_patch(Rectangle((1.0, 4.7), 3.2, 1.15, facecolor=colors[0], edgecolor="#333", alpha=0.85))
    ax.add_patch(Rectangle((4.2, 4.7), 6.3, 1.15, facecolor=colors[1], edgecolor="#333", alpha=0.85))
    ax.plot([4.2, 4.2], [4.55, 6.0], color="#C0392B", lw=2.4)
    ax.text(2.6, 5.27, "回次0", ha="center", va="center", fontsize=10, color="white")
    ax.text(7.3, 5.27, "回次1", ha="center", va="center", fontsize=10, color="white")
    ax.text(0.35, 5.27, "第0行", ha="center", va="center", fontsize=10, color="#1F4E79")
    ax.text(4.2, 6.15, "牌", ha="center", fontsize=9, color="#C0392B")

    # Row 1: no tag, all run1
    ax.add_patch(Rectangle((1.0, 3.05), 9.5, 1.15, facecolor=colors[1], edgecolor="#333", alpha=0.85))
    ax.text(5.75, 3.62, "回次1（本行无牌，整行延续）", ha="center", va="center", fontsize=10, color="white")
    ax.text(0.35, 3.62, "第1行", ha="center", va="center", fontsize=10, color="#1F4E79")

    # Row 2: two tags
    ax.add_patch(Rectangle((1.0, 1.4), 2.4, 1.15, facecolor=colors[1], edgecolor="#333", alpha=0.85))
    ax.add_patch(Rectangle((3.4, 1.4), 3.3, 1.15, facecolor=colors[2], edgecolor="#333", alpha=0.85))
    ax.add_patch(Rectangle((6.7, 1.4), 3.8, 1.15, facecolor=colors[3], edgecolor="#333", alpha=0.85))
    ax.plot([3.4, 3.4], [1.25, 2.7], color="#C0392B", lw=2.4)
    ax.plot([6.7, 6.7], [1.25, 2.7], color="#C0392B", lw=2.4)
    ax.text(2.2, 1.97, "回次1", ha="center", va="center", fontsize=10, color="white")
    ax.text(5.05, 1.97, "回次2", ha="center", va="center", fontsize=10, color="white")
    ax.text(8.6, 1.97, "回次3", ha="center", va="center", fontsize=10, color="white")
    ax.text(0.35, 1.97, "第2行", ha="center", va="center", fontsize=10, color="#1F4E79")
    ax.text(3.4, 2.85, "牌", ha="center", fontsize=9, color="#C0392B")
    ax.text(6.7, 2.85, "牌", ha="center", fontsize=9, color="#C0392B")

    ax.text(6.0, 0.55, "牌是当前回次的结束标记；回次数＝牌数＋1；编号全箱连续，不在行首清零。", ha="center", fontsize=9)
    return save(fig, "图4-回次划分示意.png")


def md_to_docx(md_text: str, fig_paths: list[Path]) -> None:
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(2.2)
    section.bottom_margin = Cm(2.2)
    section.left_margin = Cm(2.4)
    section.right_margin = Cm(2.4)

    style = doc.styles["Normal"]
    style.font.name = "宋体"
    style.font.size = Pt(12)
    style.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    style.paragraph_format.line_spacing = 1.35
    style.paragraph_format.space_after = Pt(6)

    for i in range(1, 4):
        hs = doc.styles[f"Heading {i}"]
        hs.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
        hs.font.name = "黑体"
        hs.element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
        hs.font.bold = True

    lines = md_text.splitlines()
    in_code = False
    in_table = False
    table_rows: list[list[str]] = []

    def flush_table():
        nonlocal table_rows, in_table
        if not table_rows:
            in_table = False
            return
        cols = len(table_rows[0])
        table = doc.add_table(rows=len(table_rows), cols=cols)
        table.style = "Table Grid"
        for ri, row in enumerate(table_rows):
            for ci, cell in enumerate(row):
                table.rows[ri].cells[ci].text = cell
                for p in table.rows[ri].cells[ci].paragraphs:
                    for r in p.runs:
                        r.font.size = Pt(10)
                        r.font.name = "宋体"
                        r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
                    if ri == 0:
                        for r in p.runs:
                            r.bold = True
        doc.add_paragraph("")
        table_rows = []
        in_table = False

    def split_cells(line: str) -> list[str]:
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        return parts

    for raw in lines:
        line = raw.rstrip()
        if line.strip().startswith("```"):
            if in_code:
                in_code = False
            else:
                flush_table()
                in_code = True
            continue
        if in_code:
            p = doc.add_paragraph(line)
            for r in p.runs:
                r.font.name = "Consolas"
                r.font.size = Pt(9)
            continue
        if line.strip().startswith("|") and "|" in line.strip()[1:]:
            cells = split_cells(line)
            if all(set(c.replace("-", "").replace(":", "").replace(" ", "")) == set() for c in cells):
                continue
            if not in_table:
                flush_table()
                in_table = True
            table_rows.append(cells)
            continue
        else:
            if in_table:
                flush_table()

        if not line.strip():
            continue
        if line.startswith("# "):
            p = doc.add_heading(line[2:].strip(), level=0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            continue
        if line.startswith("## "):
            doc.add_heading(line[3:].strip(), level=1)
            continue
        if line.startswith("### "):
            doc.add_heading(line[4:].strip(), level=2)
            continue
        if line.startswith("---"):
            continue
        if line.startswith("- **图") or line.startswith("- **"):
            text = line[2:].replace("**", "")
            doc.add_paragraph(text, style="List Bullet")
            continue
        if line.startswith("- "):
            doc.add_paragraph(line[2:], style="List Bullet")
            continue
        if line[:2] in {f"{i}." for i in range(1, 10)} or (len(line) > 2 and line[0].isdigit() and line[1] == "."):
            doc.add_paragraph(line, style="List Number")
            continue

        p = doc.add_paragraph()
        text = line
        # very small markdown: **bold**
        while "**" in text:
            pre, rest = text.split("**", 1)
            if "**" not in rest:
                p.add_run(pre + "**" + rest)
                text = ""
                break
            bold, text = rest.split("**", 1)
            if pre:
                p.add_run(pre)
            run = p.add_run(bold)
            run.bold = True
        if text:
            p.add_run(text)

    flush_table()

    doc.add_heading("附图", level=1)
    for path in fig_paths:
        doc.add_paragraph(path.stem)
        doc.add_picture(str(path), width=Cm(15.5))

    doc.save(DOCX_PATH)


def main() -> None:
    setup_font()
    figs = [fig1_overall(), fig2_clip(), fig3_vote(), fig4_runs()]
    md_to_docx(MD_PATH.read_text(encoding="utf-8"), figs)
    print("figures:")
    for p in figs:
        print(" ", p, p.stat().st_size)
    print("docx:", DOCX_PATH, DOCX_PATH.stat().st_size)


if __name__ == "__main__":
    main()
