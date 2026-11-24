#!/usr/bin/env python3
# news-image-20261124 — entry.png renderer.
#
# Hero story: NVIDIA reinstates Jensen Huang as CEO (Reuters/WSJ/CNN/
# Barron's, Mon 23 Nov 2026). Board vote unanimous; Trump intervened
# directly; shares surged ~33%, largest one-day gain since May 2003.
#
# One hero subject, vertical drama (rising chart + green glow + figure in
# black leather jacket + GPU chip), legible at thumbnail size. 960x960
# PNG, DejaVu fonts, PIL only. Deterministic: fixed seed, no network.
# The image is drawn, not photographed.
import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))

# ~~~ configuration: every colour, size and coordinate lives here ~~~
CFG = {
    "canvas": 960,
    "seed": 20261124,
    "font_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "font_regular": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "size_date": 36,
    "size_kicker": 26,
    "size_headline": 88,
    "size_sub": 24,
    "size_plus": 66,
    "size_tag": 22,
    "size_chip": 30,
    "size_chip2": 16,
    "size_lead": 24,
    "size_body": 22,
    "size_footer": 17,
    "masthead_h": 92,
    "hero_top": 252,
    "hero_bottom": 622,
    "band_top": 622,
    "row_y0": 640,
    "row_step": 48,
    "footer_y": 930,
}

PALETTE = {
    "navy": (7, 12, 24),
    "band": (10, 17, 32),
    "green": (118, 185, 0),
    "green_bright": (140, 220, 40),
    "white": (255, 255, 255),
    "gold": (216, 178, 90),
    "sub": (199, 210, 224),
    "body": (205, 214, 226),
    "footer": (140, 150, 165),
    "grid": (14, 24, 44),
    "glow": (30, 90, 20),
    "skin": (198, 158, 118),
    "hair": (210, 210, 210),
    "jacket": (18, 18, 22),
    "seam": (40, 40, 48),
    "shirt": (30, 30, 36),
    "chip": (16, 60, 28),
}

CHART = [(48, 585), (140, 560), (220, 575), (310, 520), (400, 540),
         (490, 470), (580, 480), (670, 400), (760, 410), (850, 320),
         (912, 300)]

ROWS = [
    ((70, 130, 200), "NATO", "AWACS jets to Poland after Russian missiles land"),
    ((210, 180, 40), "COP31", "Climate talks collapse — no deal over fossil fuels"),
    ((46, 160, 90), "SYRIA", "US weighs first training mission for Syrian forces"),
    ((230, 120, 30), "CROWDSRIKE", "Buys Zscaler in a $43.9B all-stock deal"),
    ((150, 90, 170), "CONGO", "Halts cobalt exports from Nov 30"),
    ((200, 70, 60), "INDONESIA", "Factory-fire rescue goes on — 24 dead"),
]

W = H = CFG["canvas"]


def font(name, size):
    return ImageFont.truetype(CFG[name], size)


def paint_background(d, rng):
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(
            int(7 + 6 * t), int(12 + 10 * t), int(24 + 22 * t)))
    for gx in range(0, W + 1, 80):
        d.line([(gx, CFG["hero_top"]), (gx, CFG["hero_bottom"])],
               fill=PALETTE["grid"], width=1)
    for gy in range(CFG["hero_top"], CFG["hero_bottom"] + 1, 62):
        d.line([(0, gy), (W, gy)], fill=PALETTE["grid"], width=1)
    for _ in range(90):
        x = rng.randint(0, W - 1)
        y = rng.randint(CFG["hero_top"], CFG["hero_bottom"] - 2)
        d.point((x, y), fill=(40 + rng.randint(0, 40),
                               70 + rng.randint(0, 40),
                               50 + rng.randint(0, 30)))


def paint_glow(img):
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([300, 220, 660, 640], fill=PALETTE["glow"])
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    return Image.blend(img, Image.blend(img, glow, 0.55), 0.55)


def paint_chart(d):
    d.line(CHART, fill=PALETTE["green"], width=7, joint="curve")
    d.line([(912, 300), (872, 296), (912, 300), (884, 336)],
           fill=PALETTE["green"], width=7)
    for (cx, cy) in CHART[1:-1]:
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6],
                  fill=PALETTE["green_bright"])
    d.text((648, 300), "+33%", font=font("font_bold", CFG["size_plus"]),
           fill=PALETTE["green_bright"])
    d.text((652, 372), "NVDA SHARES", font=font("font_bold", CFG["size_tag"]),
           fill=PALETTE["green"])


def paint_figure(d):
    # head + grey hair cap (top half of the ellipse only)
    d.ellipse([438, 318, 522, 402], fill=PALETTE["skin"])
    d.pieslice([438, 312, 522, 362], 180, 360, fill=PALETTE["hair"])
    # jacket torso
    d.polygon([(392, 622), (404, 452), (452, 424), (508, 424),
               (556, 452), (568, 622)], fill=PALETTE["jacket"])
    d.line([(452, 424), (480, 622)], fill=PALETTE["seam"], width=3)
    d.line([(508, 424), (480, 622)], fill=PALETTE["seam"], width=3)
    # shirt V + collar
    d.polygon([(462, 428), (498, 428), (480, 470)], fill=PALETTE["shirt"])
    # arms raised slightly
    d.line([(404, 460), (330, 396)], fill=PALETTE["jacket"], width=34)
    d.line([(556, 460), (630, 396)], fill=PALETTE["jacket"], width=34)
    d.ellipse([312, 378, 348, 414], fill=PALETTE["skin"])
    d.ellipse([612, 378, 648, 414], fill=PALETTE["skin"])
    # green rim light hugging the torso's right edge
    d.line([(556, 452), (568, 622)], fill=PALETTE["green"], width=4)


def paint_chip(d):
    d.rounded_rectangle([388, 528, 572, 612], radius=10,
                        fill=PALETTE["chip"], outline=PALETTE["green"], width=3)
    for px in range(404, 560, 22):
        d.line([(px, 528), (px, 512)], fill=PALETTE["gold"], width=4)
        d.line([(px, 612), (px, 618)], fill=PALETTE["gold"], width=4)
    d.text((480, 552), "GPU", font=font("font_bold", CFG["size_chip"]),
           fill=PALETTE["green_bright"], anchor="mm")
    d.text((480, 584), "NVIDIA", font=font("font_bold", CFG["size_chip2"]),
           fill=PALETTE["white"], anchor="mm")


def paint_header(d):
    d.rectangle([0, 0, W, CFG["masthead_h"]], fill=PALETTE["navy"])
    d.line([(0, CFG["masthead_h"]), (W, CFG["masthead_h"])],
           fill=PALETTE["gold"], width=3)
    d.text((36, 26), "TUESDAY 24 NOVEMBER 2026",
           font=font("font_bold", CFG["size_date"]), fill=PALETTE["white"])
    d.text((36, 108), "NVIDIA REINSTATES ITS CEO",
           font=font("font_bold", CFG["size_kicker"]),
           fill=PALETTE["green_bright"])
    d.text((36, 138), "HUANG IS BACK",
           font=font("font_bold", CFG["size_headline"]), fill=PALETTE["white"])
    d.text((36, 226),
           "Shares soar 33% as Trump-backed board reverses the firing",
           font=font("font_regular", CFG["size_sub"]), fill=PALETTE["sub"])


def paint_rows(d):
    d.rectangle([0, CFG["band_top"], W, H], fill=PALETTE["band"])
    d.line([(0, CFG["band_top"]), (W, CFG["band_top"])],
           fill=PALETTE["gold"], width=2)
    f_lead = font("font_bold", CFG["size_lead"])
    f_body = font("font_regular", CFG["size_body"])
    y = CFG["row_y0"]
    for col, lead, body in ROWS:
        d.rectangle([36, y + 4, 52, y + 20], fill=col)
        d.text((66, y), lead, font=f_lead, fill=PALETTE["white"])
        lw = d.textlength(lead, font=f_lead)
        d.text((66 + lw + 14, y + 1), body, font=f_body,
               fill=PALETTE["body"])
        y += CFG["row_step"]
    d.text((36, CFG["footer_y"]),
           "Sources: Reuters · WSJ · CNN · Barron's — 23–24 November 2026",
           font=font("font_regular", CFG["size_footer"]),
           fill=PALETTE["footer"])


def main():
    rng = random.Random(CFG["seed"])
    img = Image.new("RGB", (W, H), PALETTE["navy"])
    d = ImageDraw.Draw(img)
    paint_background(d, rng)
    img = paint_glow(img)
    d = ImageDraw.Draw(img)
    paint_chart(d)
    paint_figure(d)
    paint_chip(d)
    paint_header(d)
    paint_rows(d)
    img.save(os.path.join(HERE, "entry.png"))
    print("saved entry.png", img.size)


main()
