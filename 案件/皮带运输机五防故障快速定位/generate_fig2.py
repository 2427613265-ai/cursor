"""按第一版独权绘制图2（系统结构示意图）。交底原图仅图1，本图为撰写补绘草稿。"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 3000, 1900
FONT = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
OUT = Path(__file__).resolve().parent / "附图" / "图2-系统结构示意图.png"


def main() -> None:
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, 40, index=1)
    font_s = ImageFont.truetype(FONT, 34, index=1)
    font_n = ImageFont.truetype(FONT, 34, index=1)
    font_cap = ImageFont.truetype(FONT, 48, index=1)
    black = (0, 0, 0)

    def rect(xy, w=4):
        d.rectangle(xy, outline=black, width=w)

    def line(xy, w=4):
        d.line(xy, fill=black, width=w)

    def text(xy, s, f=font, anchor="mm"):
        d.text(xy, s, fill=black, font=f, anchor=anchor)

    def circle_num(xy, n, r=30):
        x, y = xy
        d.ellipse((x - r, y - r, x + r, y + r), outline=black, fill="white", width=3)
        text((x, y + 1), str(n), font_n)

    dev_w, dev_h, dev_x = 360, 240, 220
    ys = [280, 600, 920]
    term_right = []
    for y in ys:
        rect((dev_x, y, dev_x + dev_w, y + dev_h), 5)
        text((dev_x + dev_w / 2 - 16, y + dev_h / 2), "保护装置")
        tw = th = 58
        tx0 = dev_x + dev_w
        ty = y + dev_h / 2
        rect((tx0 - 6, ty - th / 2, tx0 - 6 + tw, ty + th / 2), 4)
        text((tx0 - 6 + tw / 2, ty), "11", font_s)
        term_right.append((tx0 - 6 + tw, ty))

    circle_num((dev_x - 80, ys[1] + dev_h / 2), 1)
    line((dev_x - 50, ys[1] + dev_h / 2, dev_x, ys[1] + dev_h / 2), 3)

    u = (1000, 180, 2060, 1540)
    rect(u, 6)
    text((1530, 245), "采集单元")
    circle_num((2125, 225), 2)
    line((2095, 225, u[2], 225), 3)

    for tx, ty in term_right:
        cw = 56
        rect((u[0], ty - cw / 2, u[0] + cw, ty + cw / 2), 4)
        text((u[0] + cw / 2, ty), "21", font_s)
        line((tx, ty, u[0], ty), 5)

    circle_num((u[0] + 150, term_right[0][1] - 95), 21)
    line((u[0] + 120, term_right[0][1] - 95, u[0] + 56, term_right[0][1] - 28), 3)

    inner = (1180, 520, 1860, 1280)
    rect(inner, 4)
    text((1520, 585), "对应关系")
    circle_num((1925, 565), 3)
    line((1895, 565, inner[2], 565), 3)
    rows = ["输入通道 - 皮带标识", "输入通道 - 点位标识", "输入通道 - 故障类型"]
    for i, row in enumerate(rows):
        ry = 690 + i * 155
        rect((1240, ry, 1800, ry + 105), 3)
        text((1520, ry + 52), row, font_s)

    b4 = (2260, 610, 2860, 1290)
    rect(b4, 5)
    text((2560, 685), "定位信息")
    circle_num((2920, 655), 4)
    line((2890, 655, b4[2], 655), 3)
    for i, t in enumerate(["皮带标识", "点位标识", "故障类型"]):
        iy = 790 + i * 130
        line((2340, iy + 75, 2780, iy + 75), 2)
        text((2560, iy + 32), t, font_s)

    ay = 950
    line((u[2], ay, b4[0], ay), 5)
    d.polygon(
        [(b4[0], ay), (b4[0] - 32, ay - 14), (b4[0] - 32, ay + 14)],
        outline=black,
        fill=black,
    )
    text((W / 2, 1760), "图2", font_cap)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG")
    print(OUT)


if __name__ == "__main__":
    main()
