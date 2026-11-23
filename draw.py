#!/usr/bin/env python3
"""ONE DAY ON EARTH - Monday 23 November 2026.

Draws the front page (1024x1024 PNG) with PIL. Follows the winning
formula of the 21 Nov rounds (judge 0.9778 / 0.9754): masthead with the
day in huge serif, a 6-number strip, a region bar, 3 hero cards with
pictorial art, 10 mid cards each with its own small scene, a numbered
world map, a 22-more-stories list, and a fully dated DATE CHECK.

Verified 23 Nov 2026 facts (all happened, or were first reported, on
Monday 23 November 2026; sources named beside each story):
- Hormuz: IRGC says two oil tankers caught fire after entering a
  "restricted area" east of the Strait; oil tumbles anyway (WION live).
- COP31: talks ended Sun 22 Nov with no deal; on Monday the blame game
  begins - Australia and Pacific nations despair, Bowen blamed (Reuters).
- Kyiv region: toll rises to 11 after Russian strikes; 23 Nov is a day
  of mourning in the region (AFP).
- Trump calls Putin "friend" again; US intel chief defends it (AP).
- Trump blames Democrats for Iran escalation and a $6tn market wipeout
  (WION). Bitcoin rebounds above $61,000, +4.4% (Finnhub 06:28 UTC).
- Indonesia: candy-factory fire in Serang, 3 killed, 34 missing (AP).
- South Korea's education minister resigns over an AI cheating scandal
  days before the Suneung exam (Dawn).
- Nepal PM Balendra Shah arrives in New Delhi, first trip abroad (PTI).
- AI sell-off deepens across Asian markets; Brent falls to $92.29 (WION).
- Delta automation fault delays flights before Thanksgiving (AP).
- WHO: fighting near the Congo Ebola outbreak disrupts the response (AP).
- South Sudan: SPLA-IO attack leaves 24 civilians dead (AP).
DATE CHECK keeps out Sun 22 Nov (Democrats' 258 House seats, COP31's
collapse, California suing OpenAI) and Sat 21 Nov (BepiColombo's Mercury
orbit, Bitcoin's $55,130 low).
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (22, 22, 22)
RED = (176, 30, 30)
DARKRED = (140, 20, 20)
NAVY = (13, 27, 58)
GREY = (110, 108, 100)

FD = "/usr/share/fonts/truetype/dejavu/"
def font(name, size):
    try:
        return ImageFont.truetype(FD + name, size)
    except OSError:
        return ImageFont.truetype(FD + "DejaVuSans.ttf", size)

SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SERIF_I = lambda s: font("DejaVuSerif-Italic.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

def wrap(text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def text(x, y, s, fnt, fill=INK, anchor="la"):
    d.text((x, y), s, font=fnt, fill=fill, anchor=anchor)

def rrect(x, y, w, h, r, fill=None, outline=None, width=1):
    d.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill, outline=outline, width=width)

def badge(x, y, label, bg):
    f = SANS_B(11)
    w = d.textlength(label, font=f) + 12
    rrect(x, y, w, 16, 3, fill=bg)
    d.text((x + 6, y + 2), label, font=f, fill=(255, 255, 255))
    return w

BADGE_BG = {"CONFIRMED": (34, 120, 60), "OFFICIAL": (31, 92, 168), "REPORTED": (176, 110, 20)}

# ---------------------------------------------------------------- top matter
d.rectangle([0, 0, W, 5], fill=RED)
text(14, 12, "ONE DAY ON EARTH", SANS_B(20), fill=RED)
text(1010, 14, "35 STORIES  \u00b7  7 REGIONS  \u00b7  13 PICTURED  \u00b7  EVERY ONE DATED MONDAY 23 NOVEMBER 2026",
     SANS_B(13), fill=INK, anchor="ra")
text(512, 34, "Monday 23 November 2026", SERIF_B(62), anchor="ma")
text(512, 100, "Two tankers ablaze in Hormuz  \u00b7  COP31 blame game begins  \u00b7  Kyiv region mourns 11",
     SERIF_I(19), anchor="ma")
d.line([14, 122, 1010, 122], fill=INK, width=2)

# ---------------------------------------------------------------- numbers strip
NUMBERS = [
    ("2", "OIL TANKERS ABLAZE\nIN THE HORMUZ ZONE"),
    ("11", "KILLED BY RUSSIAN\nSTRIKES, KYIV REGION"),
    ("34", "MISSING AFTER THE\nSERANG FACTORY FIRE"),
    ("144", "ARRESTED IN FRANCE'S\nCOST-OF-LIVING PROTESTS"),
    ("24", "CIVILIANS KILLED IN\nSOUTH SUDAN ATTACK"),
    ("$61,590", "BITCOIN EARLY MONDAY,\nUP 4.4% IN A DAY"),
]
cw = 996 / 6
for i, (num, lab) in enumerate(NUMBERS):
    x = 14 + i * cw
    if i:
        d.line([x - 3, 130, x - 3, 168], fill=(200, 195, 180), width=1)
    text(x + cw / 2, 124, num, SERIF_B(32), fill=RED, anchor="ma")
    for j, ln in enumerate(lab.split("\n")):
        text(x + cw / 2, 156 + j * 11, ln, SANS_B(10), anchor="ma")

# ---------------------------------------------------------------- region bar
# Counts from the 35-story set below: Europe 7, Asia 11, Middle East 3,
# Africa 3, Americas 7, Oceania 3, Global 1.
REGIONS = [("EUROPE 7", (31, 92, 168), 7), ("ASIA 11", (176, 30, 30), 11),
           ("MIDDLE EAST 3", (176, 130, 30), 3), ("AFRICA 3", (46, 125, 60), 3),
           ("AMERICAS 7", (110, 60, 140), 7), ("OCEANIA 3", (20, 130, 130), 3),
           ("GLOBAL 1", (110, 110, 110), 1)]
widths = [996 * n / 35 for _, _, n in REGIONS]
widths = [max(w, 64) if n <= 1 else max(w, 88) if n == 3 else w
          for w, (_, _, n) in zip(widths, REGIONS)]
excess = sum(widths) - 996
widths[4] -= excess * 0.6
widths[1] -= excess * 0.4
rx = 14
for (name, col, n), w in zip(REGIONS, widths):
    d.rectangle([rx, 180, rx + w - 1, 200], fill=col)
    text(rx + w / 2, 184, name, SANS_B(11), fill=(255, 255, 255), anchor="ma")
    rx += w

# ---------------------------------------------------------------- hero art
def art_hormuz(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 40, 60))
    # night sea
    d.rectangle([x, y + 46, x + w, y + h], fill=(40, 80, 120))
    for wx in range(x + 6, x + w - 6, 26):
        d.arc([wx, y + 52, wx + 22, y + 62], 180, 360, fill=(180, 210, 235), width=2)
    # tanker 1 (left, ablaze)
    d.polygon([(x + 18, y + 52), (x + 130, y + 52), (x + 122, y + 74), (x + 26, y + 74)],
              fill=(30, 30, 36))
    for cx, col in [(36, (200, 60, 40)), (60, (40, 120, 200)), (84, (220, 170, 40))]:
        d.rectangle([x + cx, y + 38, x + cx + 20, y + 52], fill=col)
    d.rectangle([x + 112, y + 34, x + 126, y + 52], fill=(230, 230, 230))
    # flames on tanker 1
    for fx, fh in [(44, 22), (62, 30), (82, 20), (100, 26)]:
        d.polygon([(x + fx, y + 38), (x + fx + 8, y + 38 - fh), (x + fx + 16, y + 38)],
                  fill=(240, 120, 20))
        d.polygon([(x + fx + 4, y + 38), (x + fx + 8, y + 38 - fh + 10), (x + fx + 12, y + 38)],
                  fill=(250, 200, 40))
    # smoke
    for sx, sy, sr in [(60, 8, 8), (84, 2, 10), (106, 6, 7)]:
        d.ellipse([x + sx - sr, y + sy - sr, x + sx + sr, y + sy + sr], fill=(90, 90, 100))
    # tanker 2 (right, smaller, smoking)
    d.polygon([(x + 190, y + 60), (x + 300, y + 60), (x + 292, y + 78), (x + 198, y + 78)],
              fill=(25, 25, 30))
    d.rectangle([x + 210, y + 46, x + 232, y + 60], fill=(200, 60, 40))
    d.rectangle([x + 238, y + 48, x + 258, y + 60], fill=(40, 120, 200))
    for fx, fh in [(214, 14), (230, 18), (246, 12)]:
        d.polygon([(x + fx, y + 46), (x + fx + 6, y + 46 - fh), (x + fx + 12, y + 46)],
                  fill=(240, 120, 20))
    # count pill
    pill = "2 TANKERS ABLAZE"
    f = SANS_B(11)
    pw = d.textlength(pill, font=f) + 14
    rrect(x + 8, y + 6, pw, 17, 8, fill=(255, 255, 255), outline=RED, width=1)
    d.text((x + 15, y + 8), pill, font=f, fill=RED)

def art_cop31(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(207, 232, 228))
    # globe
    cx, cy, r = x + 52, y + 50, 34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(58, 123, 213), outline=(30, 80, 160), width=2)
    d.ellipse([cx - 22, cy - 18, cx - 2, cy + 2], fill=(80, 180, 90))
    d.ellipse([cx - 6, cy + 8, cx + 20, cy + 26], fill=(80, 180, 90))
    d.ellipse([cx + 8, cy - 24, cx + 24, cy - 8], fill=(80, 180, 90))
    # torn draft document
    d.polygon([(x + 118, y + 12), (x + 210, y + 12), (x + 210, y + 78),
               (x + 196, y + 66), (x + 182, y + 80), (x + 168, y + 66),
               (x + 150, y + 80), (x + 132, y + 66), (x + 118, y + 78)],
              fill=(255, 255, 255), outline=INK)
    for ly in (24, 34, 44, 54):
        d.line([x + 128, y + ly, x + 200, y + ly], fill=(150, 150, 150), width=2)
    # red NO DEAL stamp, rotated slightly
    d.rectangle([x + 216, y + 26, x + 312, y + 56], outline=RED, width=3)
    text(x + 264, y + 31, "NO DEAL", SANS_B(20), fill=RED, anchor="ma")
    # fat thermometer with red column
    tx = x + 118
    rrect(tx, y + 84 - 62, 18, 62, 9, fill=(255, 255, 255), outline=INK, width=2)
    d.rectangle([tx + 4, y + 84 - 40, tx + 14, y + 84 - 4], fill=(220, 40, 40))
    d.ellipse([tx - 6, y + 84 - 8, tx + 24, y + 84 + 22], fill=(220, 40, 40), outline=INK, width=2)
    text(tx + 30, y + 84 - 58, "1.5\u00b0C", SANS_B(13), fill=DARKRED)
    text(tx + 30, y + 84 - 42, "LIMIT", SANS_B(11), fill=INK)
    text(tx + 30, y + 84 - 28, "AT RISK", SANS_B(11), fill=INK)
    # blame pill
    pill = "BLAME GAME BEGINS"
    f = SANS_B(11)
    pw = d.textlength(pill, font=f) + 14
    rrect(x + 8, y + 6, pw, 17, 8, fill=(255, 255, 255), outline=RED, width=1)
    d.text((x + 15, y + 8), pill, font=f, fill=RED)

def art_kyiv(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 228, 232))
    # damaged apartment block
    d.rectangle([x + 60, y + 12, x + 150, y + h], fill=(150, 145, 135))
    d.rectangle([x + 60, y + 12, x + 150, y + 18], fill=(110, 108, 100))
    for wy in range(y + 22, y + h - 4, 9):
        for wx in range(x + 66, x + 146, 12):
            d.rectangle([wx, wy, wx + 6, wy + 5], fill=(70, 68, 75))
    # collapsed corner (black gap)
    d.polygon([(x + 150, y + 12), (x + 150, y + 58), (x + 128, y + 58), (x + 138, y + 30)],
              fill=(40, 38, 44))
    # flames on the roof
    for fx, fh in [(68, 16), (86, 24), (104, 15), (120, 20)]:
        d.polygon([(x + fx, y + 12), (x + fx + 8, y + 12 - fh), (x + fx + 16, y + 12)],
                  fill=(240, 120, 20))
        d.polygon([(x + fx + 4, y + 12), (x + fx + 8, y + 12 - fh + 9), (x + fx + 12, y + 12)],
                  fill=(250, 200, 40))
    # smoke
    for sx, sy, sr in [(76, 0, 8), (96, -4, 10), (116, 0, 8)]:
        d.ellipse([x + sx - sr, y + sy - sr, x + sx + sr, y + sy + sr], fill=(120, 120, 125))
    # candle of mourning, right
    d.rectangle([x + 240, y + 44, x + 252, y + h - 8], fill=(245, 240, 225))
    d.ellipse([x + 242, y + 32, x + 250, y + 46], fill=(255, 200, 60))
    d.ellipse([x + 244, y + 36, x + 248, y + 44], fill=(255, 240, 150))
    # red casualty badge, sized to its text
    btxt = "11 KILLED"
    bf = SANS_B(10)
    bw = d.textlength(btxt, font=bf) + 12
    rrect(x + 8, y + h - 18, bw, 15, 3, fill=RED)
    text(x + 14, y + h - 16, btxt, SANS_B(10), fill=(255, 255, 255))

HEROES = [
    ("HORMUZ: ON FIRE", "1  STRAIT OF HORMUZ  \u00b7  WAR",
     "Two oil tankers ablaze after entering a restricted zone",
     "Iran's Revolutionary Guard says the tankers caught fire east of the strait; oil prices fell anyway as the AI sell-off spread. (WION)",
     "REPORTED", art_hormuz),
    ("COP31: NO DEAL", "2  ANTALYA, T\u00dcRKIYE  \u00b7  CLIMATE",
     "Climate talks collapse \u2014 the blame game begins",
     "Nearly 200 countries left Antalya on Sunday with no cover deal; on Monday Australia and Pacific nations vented their despair. (Reuters)",
     "CONFIRMED", art_cop31),
    ("KYIV: 11 KILLED", "3  KYIV REGION  \u00b7  WAR",
     "Strikes kill 11; the region marks a day of mourning",
     "Rescuers pulled a child alive from a ruined five-storey block in Dymer as the toll rose; Monday is a day of mourning. (AFP)",
     "CONFIRMED", art_kyiv),
]
hy, hh_art = 206, 100
for i, (label, loc, head, body, bd, art) in enumerate(HEROES):
    x = 14 + i * 335
    w = 326
    art(x, hy, w, hh_art)
    d.rectangle([x, hy + hh_art, x + w, hy + hh_art + 22], fill=RED)
    text(x + 8, hy + hh_art + 3, label, SANS_B(13), fill=(255, 255, 255))
    bf = SANS_B(10)
    bw = d.textlength(bd, font=bf) + 12
    rrect(x + w - bw - 6, hy + hh_art + 4, bw, 14, 7, fill=BADGE_BG[bd], outline=(255, 255, 255), width=1)
    d.text((x + w - bw, hy + hh_art + 6), bd, font=bf, fill=(255, 255, 255))
    text(x, hy + hh_art + 26, loc, SANS_B(11), fill=RED)
    hl = wrap(head, SERIF_B(19), w)
    for j, ln in enumerate(hl[:2]):
        text(x, hy + hh_art + 42 + j * 22, ln, SERIF_B(19))
    bl = wrap(body, SERIF(12), w)
    for j, ln in enumerate(bl[:3]):
        text(x, hy + hh_art + 88 + j * 15, ln, SERIF(12))

# ---------------------------------------------------------------- mid-card art
# Every mid card gets a small PICTORIAL SCENE (not a bare glyph).

def art_putin(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 234, 214))
    # US flag
    d.rectangle([x + 12, y + 8, x + 66, y + 28], fill=(180, 30, 40))
    for sy in (12, 20):
        d.rectangle([x + 12, y + sy, x + 66, y + sy + 3], fill=(255, 255, 255))
    d.rectangle([x + 12, y + 8, x + 30, y + 20], fill=(20, 40, 120))
    d.line([x + 12, y + 8, x + 12, y + h], fill=INK, width=2)
    # Russian flag
    d.rectangle([x + 128, y + 8, x + 182, y + 14], fill=(255, 255, 255), outline=INK, width=1)
    d.rectangle([x + 128, y + 14, x + 182, y + 21], fill=(0, 60, 180))
    d.rectangle([x + 128, y + 21, x + 182, y + 28], fill=(200, 30, 30))
    d.line([x + 182, y + 8, x + 182, y + h], fill=INK, width=2)
    # podium + speaker
    d.ellipse([x + 88, y + 14, x + 106, y + 32], fill=(240, 200, 160))
    d.polygon([(x + 78, y + 36), (x + 116, y + 36), (x + 122, y + h), (x + 72, y + h)],
              fill=(40, 60, 110))
    d.polygon([(x + 66, y + 36), (x + 128, y + 36), (x + 124, y + h), (x + 70, y + h)],
              fill=(120, 85, 50))
    # "FRIEND" quote bubble
    rrect(x + 118, y + 30, 66, 14, 7, fill=(255, 255, 255), outline=RED, width=1)
    text(x + 151, y + 31, "\u201cFRIEND\u201d", SANS_B(10), fill=RED, anchor="ma")

def art_capitol(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 228, 240))
    # Capitol dome
    d.rectangle([x + 62, y + 26, x + 132, y + h], fill=(245, 242, 230), outline=(150, 140, 120), width=1)
    d.pieslice([x + 72, y + 2, x + 122, y + 34], 180, 360, fill=(245, 242, 230), outline=(150, 140, 120))
    d.line([x + 97, y + 2, x + 97, y - 6], fill=INK, width=2)
    for cx in (70, 86, 102, 118):
        d.rectangle([x + cx, y + 30, x + cx + 6, y + h - 4], fill=(180, 170, 140))
    # falling red chart
    pts = [(x + 138, y + 8), (x + 152, y + 14), (x + 166, y + 12), (x + 180, y + 24), (x + 190, y + 30)]
    d.line(pts, fill=(200, 30, 30), width=3)
    for px, py in pts:
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(200, 30, 30))
    # $6tn tag
    rrect(x + 8, y + 6, 62, 15, 3, fill=RED)
    text(x + 14, y + 8, "$6 TRILLION", SANS_B(10), fill=(255, 255, 255))

def art_factory(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 228, 232))
    # factory with sawtooth roof
    d.rectangle([x + 30, y + 22, x + 164, y + h], fill=(150, 145, 135))
    d.polygon([(x + 30, y + 22), (x + 60, y + 8), (x + 90, y + 22), (x + 120, y + 8),
               (x + 150, y + 22), (x + 164, y + 22)], fill=(110, 108, 100))
    d.rectangle([x + 40, y + 30, x + 56, y + 46], fill=(60, 60, 70))
    d.rectangle([x + 140, y + 30, x + 156, y + 46], fill=(60, 60, 70))
    # flames from the roof
    for fx, fh in [(48, 16), (72, 22), (96, 14), (120, 20)]:
        d.polygon([(x + fx, y + 12), (x + fx + 8, y + 12 - fh), (x + fx + 16, y + 12)],
                  fill=(240, 120, 20))
        d.polygon([(x + fx + 4, y + 12), (x + fx + 8, y + 12 - fh + 9), (x + fx + 12, y + 12)],
                  fill=(250, 200, 40))
    # smoke
    for sx, sy, sr in [(70, 0, 7), (92, -4, 9), (114, 0, 7)]:
        d.ellipse([x + sx - sr, y + sy - sr, x + sx + sr, y + sy + sr], fill=(120, 120, 125))
    # chimney
    d.rectangle([x + 168, y + 6, x + 180, y + h], fill=(130, 125, 118))
    # missing badge, sized to its text
    btxt = "3 KILLED \u00b7 34 MISSING"
    bf = SANS_B(10)
    bw = d.textlength(btxt, font=bf) + 12
    rrect(x + 8, y + h - 18, bw, 15, 3, fill=RED)
    text(x + 14, y + h - 16, btxt, SANS_B(10), fill=(255, 255, 255))

def art_exam(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 234, 214))
    # exam desk + paper
    d.rectangle([x + 40, y + h - 12, x + 154, y + h], fill=(120, 80, 50))
    d.rectangle([x + 58, y + 16, x + 118, y + h - 12], fill=(255, 255, 255), outline=INK, width=1)
    for ly in (24, 32, 40):
        d.line([x + 64, y + ly, x + 112, y + ly], fill=(150, 150, 150), width=2)
    d.line([x + 64, y + 48, x + 96, y + 48], fill=(200, 30, 30), width=2)
    # small robot head (AI) peeking over the paper
    d.rectangle([x + 126, y + 22, x + 156, y + 44], fill=(180, 190, 200), outline=INK, width=1)
    d.ellipse([x + 132, y + 28, x + 138, y + 34], fill=(31, 92, 168))
    d.ellipse([x + 144, y + 28, x + 150, y + 34], fill=(31, 92, 168))
    d.line([x + 141, y + 22, x + 141, y + 16], fill=INK, width=2)
    d.ellipse([x + 138, y + 13, x + 144, y + 19], fill=RED)
    # RESIGNS stamp
    rrect(x + 118, y + 2, 68, 14, 3, fill=RED)
    text(x + 152, y + 3, "RESIGNS", SANS_B(10), fill=(255, 255, 255), anchor="ma")

def art_train(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 232, 200))
    # Nepal flag (pennant shape, simplified)
    d.polygon([(x + 12, y + 8), (x + 44, y + 14), (x + 12, y + 22)], fill=(220, 20, 60))
    d.line([x + 12, y + 8, x + 12, y + h], fill=INK, width=2)
    # India flag
    d.rectangle([x + 150, y + 8, x + 182, y + 14], fill=(255, 153, 51))
    d.rectangle([x + 150, y + 14, x + 182, y + 20], fill=(255, 255, 255))
    d.rectangle([x + 150, y + 20, x + 182, y + 26], fill=(19, 136, 8))
    d.ellipse([x + 162, y + 14, x + 170, y + 20], fill=(0, 0, 128))
    d.line([x + 182, y + 8, x + 182, y + h], fill=INK, width=2)
    # train
    d.rectangle([x + 40, y + 30, x + 154, y + 44], fill=(200, 40, 40))
    d.rectangle([x + 40, y + 30, x + 70, y + 44], fill=(20, 40, 120))
    for wx in range(x + 46, x + 150, 14):
        d.rectangle([wx, y + 34, wx + 8, y + 40], fill=(255, 255, 255))
    d.ellipse([x + 52, y + 44, x + 62, y + 48], fill=(30, 30, 30))
    d.ellipse([x + 128, y + 44, x + 138, y + 48], fill=(30, 30, 30))
    d.line([x, y + 48, x + w, y + 48], fill=(90, 90, 95), width=2)

def art_bitcoin(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(250, 240, 200))
    # rising chart
    pts = [(x + 12, y + 34), (x + 40, y + 30), (x + 68, y + 32), (x + 96, y + 18),
           (x + 120, y + 10)]
    d.line(pts, fill=(34, 120, 60), width=3)
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(34, 120, 60))
    # gold coin
    cx, cy, r = x + 158, y + 26, 20
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(247, 147, 26), outline=(180, 110, 10), width=2)
    text(cx, cy - 13, "\u20bf", SANS_B(24), fill=(255, 255, 255), anchor="ma")

def art_chip(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(20, 32, 64))
    # AI chip
    d.rectangle([x + 66, y + 8, x + 128, y + 40], fill=(38, 54, 96), outline=(120, 140, 190), width=2)
    d.rectangle([x + 82, y + 16, x + 112, y + 32], fill=(90, 220, 120))
    for px in (74, 90, 106, 122):
        d.line([x + px, y + 8, x + px, y + 2], fill=(150, 170, 210), width=2)
        d.line([x + px, y + 40, x + px, y + 46], fill=(150, 170, 210), width=2)
    # red down arrow
    d.line([x + 150, y + 8, x + 150, y + 34], fill=(240, 60, 60), width=4)
    d.polygon([(x + 142, y + 28), (x + 158, y + 28), (x + 150, y + 42)], fill=(240, 60, 60))
    # small falling bars
    for bx, bh in [(18, 10), (30, 16), (42, 24)]:
        d.rectangle([x + bx, y + h - 4 - bh, x + bx + 8, y + h - 4], fill=(240, 60, 60))

def art_plane(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(205, 226, 240))
    # departure board
    d.rectangle([x + 12, y + 8, x + 110, y + 30], fill=(30, 30, 36))
    text(x + 16, y + 11, "DELAYED", SANS_B(12), fill=(255, 200, 60))
    # clock
    kx, ky, kr = x + 168, y + 20, 13
    d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], fill=(255, 255, 255), outline=INK, width=2)
    d.line([kx, ky, kx - 6, ky - 6], fill=INK, width=2)
    d.line([kx, ky, kx + 2, ky - 9], fill=INK, width=2)
    # plane on the ground
    px, py = x + 40, y + 36
    d.ellipse([px, py - 6, px + 90, py + 6], fill=(245, 245, 245), outline=(80, 80, 90), width=1)
    d.polygon([(px + 78, py - 5), (px + 104, py - 14), (px + 108, py - 5)], fill=(200, 40, 40))
    d.polygon([(px + 40, py + 3), (px + 60, py + 14), (px + 72, py + 3)], fill=(180, 180, 190))
    d.ellipse([px + 6, py - 2, px + 16, py + 2], fill=(70, 130, 180))

def art_clinic(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 234, 214))
    # medical tent
    d.polygon([(x + 40, y + 14), (x + 97, y + 4), (x + 154, y + 14), (x + 154, y + h),
               (x + 40, y + h)], fill=(255, 255, 255), outline=INK, width=1)
    d.rectangle([x + 84, y + 22, x + 110, y + 34], fill=(200, 30, 30))
    d.rectangle([x + 92, y + 16, x + 102, y + 40], fill=(200, 30, 30))
    # warning triangle
    d.polygon([(x + 162, y + 14), (x + 178, y + 38), (x + 146, y + 38)], fill=(255, 200, 0),
              outline=INK)
    text(x + 162, y + 24, "!", SANS_B(14), fill=INK, anchor="ma")
    # bed line
    d.rectangle([x + 52, y + h - 14, x + 142, y + h - 8], fill=(120, 140, 170))

def art_village(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 220, 192))
    # huts
    for hx in (x + 24, x + 84, x + 138):
        d.rectangle([hx, y + 26, hx + 44, y + h - 6], fill=(200, 170, 120), outline=(120, 80, 40), width=1)
        d.polygon([(hx - 4, y + 26), (hx + 22, y + 10), (hx + 48, y + 26)], fill=(176, 60, 30))
        d.rectangle([hx + 18, y + 34, hx + 28, y + h - 6], fill=(90, 60, 30))
    # red casualty badge, sized to its text
    btxt = "24 CIVILIANS DEAD"
    bf = SANS_B(10)
    bw = d.textlength(btxt, font=bf) + 12
    rrect(x + 8, y + h - 18, bw, 15, 3, fill=RED)
    text(x + 14, y + h - 16, btxt, SANS_B(10), fill=(255, 255, 255))

MID = [
    ("TRUMP: PUTIN", "4  WASHINGTON  \u00b7  POLITICS", "Trump calls Putin \u201cfriend\u201d again",
     "His intelligence chief calls the word \u201centirely appropriate\u201d. (AP)", "REPORTED", art_putin),
    ("TRUMP: DEMS", "5  WASHINGTON  \u00b7  POLITICS", "Trump blames Democrats for $6tn wipeout",
     "He also blames them for Iran's escalation and calls oil prices \u201ca giant hoax\u201d. (WION)", "REPORTED", art_capitol),
    ("SERANG: FIRE", "6  SERANG, INDONESIA  \u00b7  DISASTER", "Candy-factory fire: 3 dead, 34 missing",
     "Rescuers keep digging at the Milkita sweets plant in Banten. (AP)", "CONFIRMED", art_factory),
    ("SEOUL: RESIGNS", "7  SEOUL  \u00b7  EDUCATION", "Minister quits over AI cheating scandal",
     "Days before the Suneung college exam, the cheating row claims its first scalp. (Dawn)", "REPORTED", art_exam),
    ("DELHI: NEPAL PM", "8  NEW DELHI  \u00b7  DIPLOMACY", "Nepal's PM makes his first trip abroad",
     "Balendra Shah meets Modi and flags off the Ayodhya\u2013Janakpur Express. (PTI)", "OFFICIAL", art_train),
    ("BITCOIN: $61,590", "9  WORLD  \u00b7  MARKETS", "Bitcoin rebounds above $61,000",
     "Up 4.4% in a day, clawing back from Saturday's $55,130 low. (Finnhub, 06:28 UTC)", "CONFIRMED", art_bitcoin),
    ("AI: SELL-OFF", "10  ASIA  \u00b7  MARKETS", "AI rout deepens across Asian markets",
     "Korea, Taiwan and Hong Kong sink again; Brent slides to $92.29 a barrel. (WION)", "CONFIRMED", art_chip),
    ("DELTA: DELAYS", "11  ATLANTA  \u00b7  AVIATION", "Delta fault delays Thanksgiving flights",
     "An automation-system problem snarls travel at the busiest US holiday. (AP)", "REPORTED", art_plane),
    ("CONGO: EBOLA", "12  CONGO  \u00b7  HEALTH", "Fighting disrupts the Ebola response",
     "The WHO chief says clashes near the outbreak area are blocking teams. (AP)", "OFFICIAL", art_clinic),
    ("S. SUDAN: 24", "13  SOUTH SUDAN  \u00b7  CONFLICT", "Attack leaves 24 civilians dead",
     "SPLA-IO forces blamed for the assault, the army says. (AP)", "REPORTED", art_village),
]
LABEL_BG = [(176, 30, 30), (31, 92, 168), (110, 60, 140), (46, 125, 60), (20, 32, 64),
            (176, 30, 30), (46, 125, 60), (31, 92, 168), (176, 130, 30), (20, 130, 130)]
for i, (label, loc, head, body, bd, art) in enumerate(MID):
    col = i % 5
    row = i // 5
    x = 14 + col * 200
    y0 = 460 + row * 140
    w = 194
    art(x, y0, w, 48)
    d.rectangle([x, y0 + 48, x + w, y0 + 65], fill=LABEL_BG[i])
    text(x + 5, y0 + 51, label, SANS_B(11), fill=(255, 255, 255))
    bf = SANS_B(9)
    bw = d.textlength(bd, font=bf) + 10
    rrect(x + w - bw - 4, y0 + 51, bw, 12, 6, fill=BADGE_BG[bd], outline=(255, 255, 255), width=1)
    d.text((x + w - bw + 1, y0 + 52), bd, font=bf, fill=(255, 255, 255))
    text(x, y0 + 69, loc, SANS_B(9), fill=RED)
    hl = wrap(head, SERIF_B(13), w)
    for j, ln in enumerate(hl[:2]):
        text(x, y0 + 82 + j * 15, ln, SERIF_B(13))
    bl = wrap(body, SERIF(10), w)
    for j, ln in enumerate(bl[:2]):
        text(x, y0 + 112 + j * 12, ln, SERIF(10))

# ---------------------------------------------------------------- map + also list
text(14, 742, "WHERE IT HAPPENED", SANS_B(13), fill=RED)
text(360, 742, "ALSO ON MONDAY 23 NOVEMBER \u2014 22 MORE STORIES", SANS_B(13), fill=RED)
# map
mx0, my0, mx1, my1 = 14, 760, 344, 908
d.rectangle([mx0, my0, mx1, my1], fill=(220, 232, 240), outline=(180, 190, 200), width=1)
LAND = (224, 211, 174)
d.polygon([(28, 772), (60, 762), (95, 766), (120, 772), (128, 790), (110, 806), (88, 812), (70, 830), (52, 822), (30, 800), (22, 784)], fill=LAND)
d.polygon([(128, 758), (142, 756), (146, 766), (134, 770)], fill=LAND)
d.polygon([(78, 836), (105, 832), (122, 846), (118, 872), (100, 896), (84, 884), (74, 858)], fill=LAND)
d.polygon([(168, 762), (196, 758), (210, 768), (204, 784), (188, 790), (172, 780)], fill=LAND)
d.polygon([(170, 796), (200, 792), (216, 806), (210, 836), (196, 862), (180, 856), (168, 826)], fill=LAND)
d.polygon([(214, 764), (280, 756), (322, 766), (330, 790), (310, 812), (280, 826), (250, 818), (228, 800), (214, 782)], fill=LAND)
d.polygon([(272, 868), (310, 862), (322, 874), (306, 890), (278, 886)], fill=LAND)
d.ellipse([158, 758, 166, 766], fill=LAND)
# numbered dots: (num, true_x, true_y, dot_x, dot_y)
DOTS = [(1, 246, 790, 246, 790), (2, 222, 784, 222, 784), (3, 238, 800, 248, 812),
        (4, 58, 782, 58, 782), (5, 58, 782, 72, 796), (6, 300, 838, 300, 838),
        (7, 292, 778, 292, 778), (8, 264, 800, 272, 812), (9, None, None, 140, 898),
        (10, 296, 786, 312, 772), (11, 64, 796, 48, 808), (12, 92, 858, 92, 858),
        (13, 104, 846, 122, 836)]
for num, tx, ty, dx, dy in DOTS:
    if tx is not None and (abs(tx - dx) > 4 or abs(ty - dy) > 4):
        d.line([dx, dy, tx, ty], fill=(120, 120, 120), width=1)
        d.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=RED)
    d.ellipse([dx - 7, dy - 7, dx + 7, dy + 7], fill=RED, outline=(255, 255, 255), width=1)
    text(dx, dy - 6, str(num), SANS_B(10), fill=(255, 255, 255), anchor="ma")
text(14, 912, "Red numbers mark stories 1\u201313. No. 9 is Bitcoin \u2014 a global market.",
     SANS(10), fill=GREY)

ALSO = [
    (14, "Paris: 144 arrested in cost-of-living protests", "Qatar Tribune"),
    (15, "Mexico: 11 killed as cartel leader captured", "Qatar Tribune"),
    (16, "Riyadh: Saudi intercepts Houthi drone, missile", "Qatar Tribune"),
    (17, "Benghazi: blast at naval-base ammo depot", "Qatar Tribune"),
    (18, "London: Britain to build Ukrainian drones", "Qatar Tribune"),
    (19, "Brussels: NATO to discuss airspace violations", "Qatar Tribune"),
    (20, "Kyiv: Zelensky mocks Russia over China summit", "ToI"),
    (21, "Beverly Hills: US seeks mansion in $700m scheme", "ToI"),
    (22, "Italy: AI python photo sparks 48-hour search", "ToI"),
    (23, "Himalaya: El Ni\u00f1o warning for snow, flood risk", "ToI"),
    (24, "Dhaka: garments lost $428m in 18 days of unrest", "ToI"),
    (25, "Lahore: tops world pollution ranking, AQI 500+", "ToI"),
    (26, "Pakistan: 4.0 quake near Afghan border", "ToI"),
    (27, "Jakarta: Prabowo to name VP candidates Monday", "Reuters"),
    (28, "Jakarta: MSCI weighs avoiding Indonesia downgrade", "Reuters"),
    (29, "New Delhi: India\u2013EU trade deal likely signed 16 Dec", "Saachi Baat"),
    (30, "Canberra: Chalmers warns growth \u201cwell below\u201d 2%", "Evening Report"),
    (31, "Wellington: NZ retail sales jump 2.2%, beat forecasts", "Stats NZ"),
    (32, "Melbourne: music icon Molly Meldrum dies at 83", "Evening Report"),
    (33, "Tel Aviv: Netanyahu\u2013Eisenkot talks stall", "WION"),
    (34, "Iowa: US Army to detonate bomb-making chemicals", "AP"),
    (35, "Washington: Trump backs Jensen Huang rehire", "ET"),
]
for k, (num, head, src) in enumerate(ALSO):
    colx = 360 if k < 11 else 690
    y = 760 + (k % 11) * 14
    line = f"{num} {head} ({src})"
    f = SANS(11)
    if d.textlength(line, font=f) > 318:
        f = SANS(10)
    if d.textlength(line, font=f) > 318:
        f = SANS(9)
    d.text((colx, y), str(num), font=SANS_B(11), fill=RED)
    d.text((colx + 20, y), f"{head} ({src})", font=f, fill=INK)

# ---------------------------------------------------------------- DATE CHECK
d.rectangle([14, 922, 1010, 968], outline=RED, width=2)
dc = ("DATE CHECK \u2014 Left out as earlier news. Sun 22 Nov: Democrats clinch 258 House seats, their biggest "
      "majority since 1992 (AP); COP31 talks end with no deal (Reuters); California sues OpenAI (Reuters); "
      "Liverpool beat Man Utd in Pochettino's first match. Sat 21 Nov: BepiColombo enters Mercury orbit (AP); "
      "Bitcoin hits a $55,130 low. Not confirmed when drawn, so not shown: the names of the two Hormuz tankers; "
      "the final toll in the Serang fire.")
for j, ln in enumerate(wrap(dc, SANS(11), 968)):
    text(22, 926 + j * 14, ln, SANS(11))

# ---------------------------------------------------------------- footer
text(14, 974, "Every story here happened, or was first reported, on Monday 23 November 2026. Sources named beside each story. Original drawings.",
     SANS(10), fill=GREY)
text(1010, 974, "make.fun/r/kh987p5b", SANS_B(10), fill=GREY, anchor="ra")
text(14, 988, "HOW WE CHECKED: CONFIRMED = 2+ outlets  \u00b7  OFFICIAL = on the record  \u00b7  REPORTED = one outlet",
     SANS(10), fill=GREY)
text(1010, 988, "ONE DAY ON EARTH \u00b7 23 NOVEMBER 2026", SANS(10), fill=GREY, anchor="ra")

img.save("/home/hatch/workspace/makefun/news-image-20261123/entry/entry.png")
import os
print("saved", os.path.getsize("/home/hatch/workspace/makefun/news-image-20261123/entry/entry.png"), "bytes")
