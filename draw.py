#!/usr/bin/env python3
"""ONE DAY ON EARTH - Monday 23 November 2026 (round 2, fresh build).

Draws a 1024x1024 newspaper front page summarising the day's world news.
Pure Pillow, deterministic: no randomness, no timestamps, fixed fonts.
Usage: python3 draw.py  -> writes entry.png next to this file.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

PAPER = (248, 244, 236)
INK = (20, 20, 20)
GREY = (110, 108, 100)
LIGHT_LINE = (205, 198, 186)
RED = (176, 30, 36)
CARD = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"

def font(size, bold=False, serif=False):
    name = "DejaVuSerif-Bold.ttf" if (serif and bold) else \
           "DejaVuSerif.ttf" if serif else \
           "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)

def wrap(draw, text, fnt, maxw):
    """Greedy word wrap; returns list of lines that fit maxw."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def fit_lines(draw, text, fnt, maxw, max_lines):
    """Wrap text to at most max_lines; ellipsize the last line if needed."""
    lines = wrap(draw, text, fnt, maxw)
    if len(lines) <= max_lines:
        return lines
    lines = lines[:max_lines]
    while lines and draw.textlength(lines[-1] + " ...", font=fnt) > maxw:
        lines[-1] = lines[-1].rsplit(" ", 1)[0] if " " in lines[-1] else lines[-1][:-1]
    lines[-1] = lines[-1].rstrip() + " ..."
    return lines

def badge(draw, x, y, kind, big=False):
    """Verification pill. kind: C=CONFIRMED, O=OFFICIAL, R=REPORTED."""
    col = {"C": (30, 125, 50), "O": (21, 101, 192), "R": (230, 108, 0)}[kind]
    word = {"C": "CONFIRMED", "O": "OFFICIAL", "R": "REPORTED"}[kind]
    if big:
        f = font(11, bold=True)
        w = int(draw.textlength(word, font=f)) + 16
        h = 18
    else:
        f = font(9, bold=True)
        w = 22
        h = 13
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=col)
    if big:
        draw.text((x + 8, y + 3), word, font=f, fill=(255, 255, 255))
    else:
        draw.text((x + 8, y + 2), kind, font=f, fill=(255, 255, 255))
    return w

# ---------------------------------------------------------------- data
REGIONS = {
    "GULF":    (139, 26, 26),
    "EUROPE":  (31, 78, 121),
    "ISRAEL":  (122, 92, 0),
    "ASIA":    (11, 107, 79),
    "AFRICA":  (179, 84, 30),
    "AMERICAS": (91, 45, 142),
    "CLIMATE": (14, 124, 134),
    "MARKETS": (68, 68, 68),
    "SPORT":   (194, 24, 91),
}

NUMBERS = [
    ("2", "TANKERS ABLAZE\nIN HORMUZ"),
    ("14", "KILLED IN RUSSIAN\nSTRIKES, KYIV REGION"),
    ("24", "KILLED IN INDONESIA\nFACTORY FIRE"),
    ("23", "ISRAELI SOLDIERS DIED\nBY SUICIDE IN 2026"),
    ("350%", "RISE IN WEST BANK\nHEALTH-SECTOR INCIDENTS"),
    ("$35B", "CITIGROUP UK ERROR\nMAY CLOUD US EXIT"),
]

HEROES = [
    {
        "scene": "hormuz", "tag": "HORMUZ: ON FIRE", "badge": "C",
        "head": "Two tankers ablaze after mine strikes",
        "body": "Iran's Revolutionary Guard says two supertankers on 'unauthorised' routes hit naval mines east of the strait and caught fire; both were halted off Oman.",
        "src": "IRGC via Mehr, China Daily, The Statesman",
    },
    {
        "scene": "kyiv", "tag": "KYIV: 14 KILLED", "badge": "C",
        "head": "Strikes kill 14 across the Kyiv region",
        "body": "An overnight strike flattened part of a five-storey block in Dymer, killing 11; a supermarket hit in Vyshneve killed 3 more. Rescuers dug through rubble all day.",
        "src": "Reuters, CNA, The Hindu",
    },
    {
        "scene": "trump", "tag": "TRUMP: IRAN WARNING", "badge": "C",
        "head": "Trump 'inclined' to resume Iran strikes",
        "body": "The US president says he leans towards resuming military strikes on Iran after the New Year if talks fail to produce a deal he calls acceptable.",
        "src": "Yeni Safak, Economic Times",
    },
]

# grid stories: (region, headline, source, badge)
GRID = [
    ("GULF", "IRGC says it downed a US Predator drone", "The Statesman, China Daily", "C"),
    ("GULF", "Iran vows to use all means to counter US blockade", "Yeni Safak, Dunya", "C"),
    ("GULF", "Qatar and Germany urge Iran to drop Houthi support", "Dunya", "R"),
    ("EUROPE", "Drone debris falls on Kyiv schools and warehouse", "Ukrainska Pravda, Kyiv Independent", "C"),
    ("EUROPE", "NATO fears Russia may launch a nuclear-armed satellite", "Economic Times", "R"),
    ("EUROPE", "Russian cargo ship ablaze in Baltic after drone strike", "Dunya", "R"),
    ("EUROPE", "German army tests kamikaze drones and AI targeting", "Dunya", "R"),
    ("ISRAEL", "Eisenkot's 48-hour bid to topple Netanyahu", "Economic Times", "R"),
    ("ISRAEL", "23 Israeli soldiers died by suicide in 2026, a 16-year high", "Haaretz via Yeni Safak", "R"),
    ("ISRAEL", "Attacks on West Bank health sector up 350%, group says", "Yeni Safak", "R"),
    ("ISRAEL", "Prisoners in Ofer 'lose dozens of kilograms'", "Yeni Safak", "R"),
    ("ASIA", "Bangladesh vows to arrest Hasina if she returns", "Reuters", "O"),
    ("ASIA", "Indonesia confirms 24 killed in candy-factory fire", "Reuters, Al Jazeera, CNA", "C"),
    ("ASIA", "Seoul minister quits over exam cheating chaos", "Dunya", "R"),
    ("ASIA", "India tests AI anti-drone missile at Pokhran", "Economic Times", "R"),
    ("ASIA", "Kim: North Korea seeks security, not supremacy", "Economic Times, Manila Times", "C"),
    ("ASIA", "Modi offers Nepal $1.6B for flood rebuild", "Rio Times", "R"),
    ("ASIA", "China slams US ban on telecom firms", "Manila Times", "R"),
    ("AFRICA", "Drone strikes hit homes and a UN building in Khartoum", "Manila Times", "R"),
    ("AFRICA", "RSF accused of looting shops and livestock in W. Kordofan", "Yeni Safak", "R"),
    ("AFRICA", "Libya's east files UN complaint over Benghazi ship attacks", "Yeni Safak", "R"),
    ("AFRICA", "WHO chief pleads for peace in Ebola-hit DR Congo area", "Manila Times", "R"),
    ("AMERICAS", "US forms elite team to stop air-traffic outages", "Economic Times, Yeni Safak", "C"),
    ("AMERICAS", "Trump to host gala for meme-coin investors", "Economic Times", "R"),
    ("AMERICAS", "Appeals court strikes down pregnant-worker law", "AP via Manila Times", "R"),
    ("AMERICAS", "Father and daughter detained by ICE at Seattle airport", "AP via Manila Times", "R"),
    ("AMERICAS", "Drones hit police command in Cucuta, Colombia", "Rio Times", "R"),
    ("AMERICAS", "Brazil's lower house votes on spending curbs", "Rio Times", "R"),
    ("CLIMATE", "Blame game begins after COP31 collapse", "Dunya", "R"),
    ("CLIMATE", "UN chief: 'no ambiguity in the science'", "UN News, Manila Times", "C"),
    ("MARKETS", "Citigroup's $35B UK error clouds its US penalty exit", "Economic Times", "R"),
    ("MARKETS", "Asia investment spending to hit $16T by 2030", "Economic Times", "R"),
    ("MARKETS", "Nvidia chief's affair partner 'in touch with China spy agency'", "NYT via Economic Times", "R"),
    ("MARKETS", "Skubal agrees record 9-year, $450M deal with the Mets", "NSE Sport", "R"),
    ("SPORT", "49ers beat Vikings 35-10 in Mexico City", "BBC, ESPN", "C"),
    ("SPORT", "Carney brings a Trump to Canada's comedy dinner", "Economic Times", "R"),
]

REGION_STRIP = [("GULF", 3), ("EUROPE", 4), ("ISRAEL", 4), ("ASIA", 7),
                ("AFRICA", 4), ("AMERICAS", 6), ("CLIMATE", 2),
                ("MARKETS", 4), ("SPORT", 2)]

# ---------------------------------------------------------------- scenes
def scene_hormuz(d, x, y, w, h):
    """Night strait: dark sea, two tankers burning, a mine, smoke. All art inside the box."""
    d.rectangle([x, y, x + w, y + h], fill=(16, 42, 74))
    d.ellipse([x + w - 52, y + 8, x + w - 22, y + 38], fill=(235, 228, 200))  # moon
    d.rectangle([x, y + h - 40, x + w, y + h], fill=(10, 28, 52))  # sea band
    for i in range(4):  # wave lines
        yy = y + h - 32 + i * 8
        d.line([x + 8, yy, x + w - 8, yy], fill=(90, 140, 190), width=1)
    # coast silhouette
    d.polygon([(x, y + h - 40), (x + 90, y + h - 58), (x + 170, y + h - 40)],
              fill=(24, 52, 44))
    # tanker 1 (left)
    tx, ty = x + 18, y + h - 70
    d.polygon([(tx, ty + 18), (tx + 8, ty + 30), (tx + 118, ty + 30),
               (tx + 128, ty + 18)], fill=(30, 30, 34))
    d.rectangle([tx + 14, ty, tx + 52, ty + 18], fill=(176, 30, 36))
    d.rectangle([tx + 58, ty, tx + 96, ty + 18], fill=(31, 78, 121))
    d.rectangle([tx + 100, ty - 8, tx + 112, ty + 18], fill=(240, 240, 240))
    # tanker 2 (right, smaller, behind)
    tx2, ty2 = x + w - 150, y + h - 60
    d.polygon([(tx2, ty2 + 14), (tx2 + 6, ty2 + 24), (tx2 + 96, ty2 + 24),
               (tx2 + 104, ty2 + 14)], fill=(40, 40, 44))
    d.rectangle([tx2 + 12, ty2, tx2 + 44, ty2 + 14], fill=(176, 30, 36))
    d.rectangle([tx2 + 48, ty2, tx2 + 80, ty2 + 14], fill=(31, 78, 121))
    # flames on both tankers
    for fx, fy, s in [(tx + 30, ty - 4, 12), (tx + 76, ty - 4, 10),
                      (tx2 + 28, ty2 - 4, 10), (tx2 + 62, ty2 - 4, 8)]:
        d.polygon([(fx - s, fy + 8), (fx - s // 2, fy - s), (fx, fy + 2),
                   (fx + s // 2, fy - s + 4), (fx + s, fy + 8)],
                  fill=(255, 122, 0))
        d.polygon([(fx - s // 2, fy + 8), (fx - s // 4, fy - s // 2),
                   (fx + s // 4, fy - s // 2), (fx + s // 2, fy + 8)],
                  fill=(255, 214, 64))
    # smoke plumes
    for sx, sy, r in [(tx + 34, ty - 18, 7), (tx + 78, ty - 16, 6),
                      (tx2 + 30, ty2 - 16, 6)]:
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(120, 120, 120))
        d.ellipse([sx - r + 5, sy - r - 5, sx + r + 5, sy + r - 5],
                  fill=(150, 150, 150))
    # naval mine in the water
    mx, my = x + w // 2 + 8, y + h - 20
    d.ellipse([mx - 9, my - 9, mx + 9, my + 9], fill=(15, 15, 15))
    for dx, dy in [(-12, 0), (12, 0), (0, -12), (0, 12), (-8, -8), (8, -8),
                   (-8, 8), (8, 8)]:
        d.line([mx, my, mx + dx, my + dy], fill=(15, 15, 15), width=2)

def scene_kyiv(d, x, y, w, h):
    """Dusk street: five-storey block with a collapsed corner, rubble, ladder. All art inside the box."""
    d.rectangle([x, y, x + w, y + h], fill=(58, 52, 66))  # dusk sky
    d.rectangle([x, y + h - 34, x + w, y + h], fill=(38, 34, 44))  # ground
    d.ellipse([x + w - 46, y + 6, x + w - 20, y + 32], fill=(255, 196, 120))
    # main block: 4 floors x 5 cols of windows, all inside the block
    bx, by, bw, bh = x + 22, y + 6, 170, h - 40
    d.rectangle([bx, by, bx + bw, by + 8], fill=(150, 138, 122))  # roofline
    d.rectangle([bx, by, bx + bw, by + bh], fill=(196, 184, 168))
    for r in range(4):
        for c in range(5):
            wx = bx + 10 + c * 30
            wy = by + 12 + r * 12
            lit = (r + c) % 4 == 0
            d.rectangle([wx, wy, wx + 15, wy + 8],
                        fill=(255, 196, 90) if lit else (70, 66, 80))
    # collapsed corner: jagged break on the right side
    d.polygon([(bx + bw, by + 20), (bx + bw - 40, by + 34), (bx + bw - 18, by + 44),
               (bx + bw - 44, by + 54), (bx + bw, by + bh)],
              fill=(90, 84, 96))
    d.polygon([(bx + bw, by + 20), (bx + bw - 40, by + 34), (bx + bw - 18, by + 44),
               (bx + bw - 44, by + 54), (bx + bw, by + bh)],
              outline=(40, 36, 48))
    # rubble pile at the base of the break
    for rx, ry, rr in [(bx + bw - 52, by + bh - 6, 10), (bx + bw - 30, by + bh - 3, 12),
                       (bx + bw - 70, by + bh - 3, 8), (bx + bw - 12, by + bh - 4, 9)]:
        d.polygon([(rx - rr, by + bh), (rx - rr // 2, ry - rr), (rx + rr // 2, ry - rr),
                   (rx + rr, by + bh)], fill=(120, 112, 104))
    # small flames at the rubble base
    for fx, fy, s in [(bx + bw - 46, by + bh - 2, 9), (bx + bw - 24, by + bh - 2, 7)]:
        d.polygon([(fx - s, fy + 4), (fx - s // 2, fy - s), (fx, fy + 1),
                   (fx + s // 2, fy - s + 3), (fx + s, fy + 4)],
                  fill=(255, 122, 0))
        d.polygon([(fx - s // 2, fy + 4), (fx - s // 4, fy - s // 2),
                   (fx + s // 4, fy - s // 2), (fx + s // 2, fy + 4)],
                  fill=(255, 214, 64))
    # rescue ladder leaning on the building
    d.line([bx + 8, by + bh, bx + 56, by + 24], fill=(230, 70, 45), width=5)
    d.line([bx + 16, by + bh, bx + 64, by + 24], fill=(230, 70, 45), width=5)
    for t in range(1, 5):
        lx = bx + 8 + t * 11
        ly = by + bh - t * 10
        d.line([lx, ly, lx + 8, ly], fill=(230, 70, 45), width=3)
    # small neighbour block, intact, far right
    d.rectangle([x + w - 58, y + 34, x + w - 14, y + h - 34], fill=(150, 140, 128))
    for r in range(2):
        for c in range(2):
            d.rectangle([x + w - 50 + c * 20, y + 42 + r * 12,
                         x + w - 38 + c * 20, y + 50 + r * 12],
                        fill=(70, 66, 80))

def scene_trump(d, x, y, w, h):
    """Split scene: White House dome left, missile arc and burst right."""
    d.rectangle([x, y, x + w, y + h], fill=(18, 34, 64))  # deep blue
    # stars
    for sx, sy in [(14, 12), (52, 26), (96, 10), (150, 20), (210, 12),
                   (260, 28), (300, 14), (40, 48), (120, 44)]:
        d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1],
                  fill=(255, 255, 255))
    # White House silhouette (left), wider and clearer
    wx, wy = x + 14, y + h - 58
    d.rectangle([wx, wy, wx + 124, wy + 58], fill=(232, 228, 218))
    d.rectangle([wx - 4, wy + 52, wx + 128, wy + 58], fill=(200, 194, 182))
    d.polygon([(wx + 20, wy), (wx + 38, wy - 20), (wx + 86, wy - 20),
               (wx + 104, wy)], fill=(232, 228, 218))
    d.ellipse([wx + 38, wy - 34, wx + 86, wy - 6], fill=(232, 228, 218))
    for i in range(6):
        cx = wx + 10 + i * 19
        d.rectangle([cx, wy + 14, cx + 9, wy + 52], fill=(178, 172, 160))
    # flag on the dome
    d.line([wx + 62, wy - 38, wx + 62, wy - 30], fill=(255, 255, 255), width=2)
    d.polygon([(wx + 62, wy - 38), (wx + 80, wy - 34), (wx + 62, wy - 30)],
              fill=(176, 30, 36))
    # missile arcing up right
    mx0, my0 = x + w - 160, y + h - 24
    d.line([mx0, my0, mx0 + 48, my0 - 40], fill=(255, 214, 64), width=7)
    d.line([mx0, my0, mx0 + 48, my0 - 40], fill=(255, 122, 0), width=3)
    # missile body
    mx, my = mx0 + 48, my0 - 40
    d.polygon([(mx, my - 26), (mx + 11, my - 12), (mx + 8, my + 10),
               (mx - 8, my + 10), (mx - 11, my - 12)], fill=(220, 220, 220))
    d.polygon([(mx, my - 26), (mx + 7, my - 12), (mx - 7, my - 12)],
              fill=(176, 30, 36))
    # explosion burst at the top right
    bx, by = x + w - 34, y + 30
    for ang in range(0, 360, 30):
        r1, r2 = 7, 16
        a = math.radians(ang)
        d.line([bx + int(r1 * math.cos(a)), by + int(r1 * math.sin(a)),
                bx + int(r2 * math.cos(a)), by + int(r2 * math.sin(a))],
               fill=(255, 214, 64), width=3)
    d.ellipse([bx - 9, by - 9, bx + 9, by + 9], fill=(255, 122, 0))
    d.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(255, 240, 180))

SCENES = {"hormuz": scene_hormuz, "kyiv": scene_kyiv, "trump": scene_trump}

# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 16  # side margin

    # masthead
    y = 10
    d.text((M, y), "ONE DAY ON EARTH", font=font(20, bold=True, serif=True),
           fill=RED)
    right = "39 STORIES  \u00b7  9 REGIONS  \u00b7  ALL DATED MONDAY 23 NOVEMBER 2026"
    d.text((W - M - d.textlength(right, font=font(11, bold=True)), y + 5),
           right, font=font(11, bold=True), fill=INK)
    d.line([M, y + 28, W - M, y + 28], fill=RED, width=2)
    y += 34

    # big date title
    title = "Monday 23 November 2026"
    tf = font(52, bold=True, serif=True)
    tw = d.textlength(title, font=tf)
    d.text(((W - tw) / 2, y), title, font=tf, fill=INK)
    y += 60
    sub = ("Two tankers ablaze in Hormuz  \u00b7  14 killed near Kyiv  "
           "\u00b7  Trump warns Iran strikes may resume")
    sf = font(15, bold=False)
    d.text(((W - d.textlength(sub, font=sf)) / 2, y), sub, font=sf, fill=(60, 58, 52))
    y += 20
    d.line([M, y, W - M, y], fill=LIGHT_LINE, width=1)
    y += 8

    # numbers strip: 6 cells
    cell_w = (W - 2 * M - 5 * 6) // 6
    strip_top = y
    for i, (num, lab) in enumerate(NUMBERS):
        cx = M + i * (cell_w + 6)
        nf = font(28, bold=True, serif=True)
        d.text((cx + (cell_w - d.textlength(num, font=nf)) / 2, y), num,
               font=nf, fill=RED)
        lf = font(9, bold=True)
        lines = wrap(d, lab.replace("\n", " "), lf, cell_w - 4)
        ly = y + 34
        for ln in lines:
            d.text((cx + (cell_w - d.textlength(ln, font=lf)) / 2, ly), ln,
                   font=lf, fill=INK)
            ly += 11
        if i < 5:
            d.line([cx + cell_w + 3, y + 2, cx + cell_w + 3, y + 54],
                   fill=LIGHT_LINE, width=1)
    y = strip_top + 56
    d.line([M, y, W - M, y], fill=LIGHT_LINE, width=1)
    y += 8

    # hero row: 3 panels
    hero_w = (W - 2 * M - 2 * 8) // 3
    hero_h = 196
    scene_h = 96
    for i, hero in enumerate(HEROES):
        hx = M + i * (hero_w + 8)
        # scene
        SCENES[hero["scene"]](d, hx, y, hero_w, scene_h)
        # red banner over the bottom of the scene
        d.rectangle([hx, y + scene_h - 20, hx + hero_w, y + scene_h],
                    fill=RED)
        bf = font(12, bold=True)
        d.text((hx + 8, y + scene_h - 17), hero["tag"], font=bf,
               fill=(255, 255, 255))
        badge(d, hx + hero_w - 96, y + scene_h - 17, hero["badge"], big=True)
        # headline + body
        ty = y + scene_h + 6
        hf = font(16, bold=True)
        for ln in fit_lines(d, hero["head"], hf, hero_w - 4, 2):
            d.text((hx, ty), ln, font=hf, fill=INK)
            ty += 19
        bf2 = font(11)
        for ln in fit_lines(d, hero["body"], bf2, hero_w - 4, 3):
            d.text((hx, ty), ln, font=bf2, fill=(50, 48, 44))
            ty += 14
        sf2 = font(9, bold=True)
        d.text((hx, ty + 2), hero["src"], font=sf2, fill=GREY)
    y += hero_h + 8

    # region strip
    d.text((M, y + 2), "WHERE IT HAPPENED:", font=font(11, bold=True), fill=RED)
    sx = M + 148
    for name, count in REGION_STRIP:
        col = REGIONS[name]
        label = f"{name} {count}"
        lf = font(10, bold=True)
        lw = int(d.textlength(label, font=lf)) + 14
        d.rounded_rectangle([sx, y, sx + lw, y + 18], radius=9, fill=col)
        d.text((sx + 7, y + 3), label, font=lf, fill=(255, 255, 255))
        sx += lw + 5
    y += 24

    # grid: 4 columns x 9 rows = 36 stories, no filler cells
    cols, rows = 4, 9
    gap = 6
    gw = (W - 2 * M - (cols - 1) * gap) // cols
    grid_top = y
    grid_h = 9 * 54 + 8 * gap
    gh = (grid_h - (rows - 1) * gap) // rows
    for idx in range(cols * rows):
        r, c = divmod(idx, cols)
        cx = M + c * (gw + gap)
        cy = grid_top + r * (gh + gap)
        if idx < len(GRID):
            region, head, src, kind = GRID[idx]
            col = REGIONS[region]
            d.rectangle([cx, cy, cx + gw, cy + gh], fill=CARD,
                        outline=LIGHT_LINE, width=1)
            d.rectangle([cx, cy, cx + gw, cy + 3], fill=col)
            # tag + badge
            tf2 = font(9, bold=True)
            d.text((cx + 6, cy + 5), region, font=tf2, fill=col)
            badge(d, cx + gw - 28, cy + 4, kind)
            # headline (max 2 lines)
            hf = font(12, bold=True)
            lines = fit_lines(d, head, hf, gw - 12, 2)
            ly = cy + 17
            for ln in lines:
                d.text((cx + 6, ly), ln, font=hf, fill=INK)
                ly += 13
            # source
            sf3 = font(9)
            d.text((cx + 6, cy + gh - 10), src, font=sf3, fill=GREY)
        else:
            u = idx - len(GRID)
            d.rectangle([cx, cy, cx + gw, cy + gh], fill=(238, 232, 220),
                        outline=LIGHT_LINE, width=1)
            uf = font(9, bold=True)
            if u == 0:
                d.text((cx + 6, cy + 6), "HOW WE CHECKED", font=uf, fill=RED)
                lines = wrap(d, "CONFIRMED = 2+ outlets. OFFICIAL = on the record. REPORTED = one outlet.",
                             font(9), gw - 12)
                ly = cy + 20
                for ln in lines:
                    d.text((cx + 6, ly), ln, font=font(9), fill=INK)
                    ly += 11
            elif u == 1:
                d.text((cx + 6, cy + 6), "THE DAY IN ONE LINE", font=uf, fill=RED)
                lines = wrap(d, "A war at sea, a war on land, and a climate summit that ended in blame.",
                             font(9), gw - 12)
                ly = cy + 20
                for ln in lines:
                    d.text((cx + 6, ly), ln, font=font(9), fill=INK)
                    ly += 11
            else:
                d.text((cx + 6, cy + 6), "READ IT THIS WAY", font=uf, fill=RED)
                lines = wrap(d, "Start with the three big pictures, then read across. Every card is one story.",
                             font(9), gw - 12)
                ly = cy + 20
                for ln in lines:
                    d.text((cx + 6, ly), ln, font=font(9), fill=INK)
                    ly += 11
    y = grid_top + grid_h + 8

    # DATE CHECK footer
    box_h = 42
    d.rectangle([M, y, W - M, y + box_h], outline=RED, width=2)
    d.text((M + 8, y + 5), "DATE CHECK \u2014 left out as earlier news:",
           font=font(10, bold=True), fill=RED)
    dc = ("Sun 22 Nov: Democrats clinch 258 House seats (AP); COP31 talks end with no deal "
          "(Reuters); Liverpool beat Man Utd.  Sat 21 Nov: BepiColombo enters Mercury orbit (AP); "
          "Bitcoin hits $55,130 low; Sinaloa kingpin arrested (toll confirmed 22 Nov).")
    ly = y + 20
    for ln in wrap(d, dc, font(9), W - 2 * M - 16):
        d.text((M + 8, ly), ln, font=font(9), fill=INK)
        ly += 11
    y += box_h + 4

    # credit line doubles as the verification legend
    credit = ("CONFIRMED = 2+ outlets  \u00b7  OFFICIAL = on the record  \u00b7  "
              "REPORTED = one outlet.   Every story happened or was first reported "
              "Mon 23 Nov 2026.  make.fun/r/kh987p5b")
    d.text((M, y), credit, font=font(9), fill=GREY)
    d.text((W - M - d.textlength("ONE DAY ON EARTH \u00b7 23 NOVEMBER 2026",
                                  font=font(9, bold=True)), y),
           "ONE DAY ON EARTH \u00b7 23 NOVEMBER 2026", font=font(9, bold=True),
           fill=GREY)
    print("layout: bottom y =", y + 12, "of", H)

    img.save(os.path.join(HERE, "entry.png"), optimize=True)
    print("saved", os.path.join(HERE, "entry.png"))

if __name__ == "__main__":
    build()
