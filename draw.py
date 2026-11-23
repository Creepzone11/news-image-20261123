"""Front page for Monday 23 November 2026, drawn from scratch with PIL.

The sheet is a 1024x1024 newspaper front page: a masthead carrying the
date, a strip of six figures, a seven-segment bar showing how the 35
stories split across regions, three large picture stories, ten smaller
picture stories, a numbered map marking where the first thirteen stories
happened, a list of the other twenty-two stories, and a DATE CHECK box
naming the weekend news this page deliberately leaves out. Every picture
on the page is drawn with plain PIL shapes -- no photographs, no art
fetched from anywhere.

The code is organised around data, not around one function per picture.
Each picture is a list of small drawing commands ("ops") that one
interpreter executes; each story is a row in a table; one generic card
painter lays out heroes and mid cards alike from those rows. To change
the page you edit a table row or an op list; the drawing machinery stays
the same.

Run it from this directory:  python3 draw.py
It writes entry.png next to itself."""

from pathlib import Path

from PIL import Image as _Image
from PIL import ImageDraw as _Draw
from PIL import ImageFont as _Font

PAGE_W, PAGE_H = 1024, 1024
PAPER_RGB = (247, 243, 232)
INK_RGB = (22, 22, 22)
RED_RGB = (176, 30, 30)
DARKRED_RGB = (140, 20, 20)
GREY_RGB = (110, 108, 100)
WHITE = (255, 255, 255)
LAND_RGB = (224, 211, 174)
SEA_RGB = (220, 232, 240)

_FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
_FONT_FILES = {
    "serif-bold": "DejaVuSerif-Bold.ttf",
    "serif": "DejaVuSerif.ttf",
    "serif-italic": "DejaVuSerif-Italic.ttf",
    "sans-bold": "DejaVuSans-Bold.ttf",
    "sans": "DejaVuSans.ttf",
}
_FONT_CACHE = {}


def _load_font(kind, size):
    """Fetch a DejaVu face at a size, caching it; fall back to plain sans."""
    key = (kind, size)
    if key not in _FONT_CACHE:
        try:
            _FONT_CACHE[key] = _Font.truetype(_FONT_DIR + _FONT_FILES[kind], size)
        except OSError:
            _FONT_CACHE[key] = _Font.truetype(_FONT_DIR + "DejaVuSans.ttf", size)
    return _FONT_CACHE[key]


# Flame colours shared by every fire drawn on the page.
FLAME_OUTER = (240, 120, 20)
FLAME_INNER = (250, 200, 40)


class Canvas:
    """A 1024x1024 sheet plus the pen that draws on it.

    Primitives take absolute page coordinates. ``scene`` takes a list of
    ops whose coordinates are relative to a picture's top-left corner and
    executes them in order, so a picture can be placed anywhere by
    changing only its origin.
    """

    def __init__(self, width, height, background):
        self.image = _Image.new("RGB", (width, height), background)
        self.pen = _Draw.Draw(self.image)

    # -- primitives ------------------------------------------------------
    def box(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        self.pen.rectangle([x0, y0, x1, y1], fill=fill, outline=outline, width=width)

    def rbox(self, x, y, w, h, radius, fill=None, outline=None, width=1):
        self.pen.rounded_rectangle(
            [x, y, x + w, y + h], radius=radius, fill=fill, outline=outline, width=width
        )

    def seg(self, points, fill, width=1):
        self.pen.line(points, fill=fill, width=width)

    def poly(self, points, fill=None, outline=None):
        self.pen.polygon(points, fill=fill, outline=outline)

    def ell(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        self.pen.ellipse([x0, y0, x1, y1], fill=fill, outline=outline, width=width)

    def txt(self, x, y, s, kind, size, fill=INK_RGB, anchor="la"):
        self.pen.text((x, y), s, font=_load_font(kind, size), fill=fill, anchor=anchor)

    def measure(self, s, kind, size):
        return self.pen.textlength(s, font=_load_font(kind, size))

    def wrap_lines(self, s, kind, size, max_w):
        """Greedy word wrap: pack as many words per line as fit."""
        fnt = _load_font(kind, size)
        out = []
        current = ""
        for word in s.split():
            trial = word if not current else current + " " + word
            if self.pen.textlength(trial, font=fnt) <= max_w:
                current = trial
            else:
                if current:
                    out.append(current)
                current = word
        if current:
            out.append(current)
        return out

    def save(self, path):
        self.image.save(path)

    # -- scene interpreter ------------------------------------------------
    def scene(self, ops, ox, oy):
        for op in ops:
            verb = op[0]
            if verb == "rect":
                _, x0, y0, x1, y1, fill = op
                self.pen.rectangle([ox + x0, oy + y0, ox + x1, oy + y1], fill=fill)
            elif verb == "recto":
                _, x0, y0, x1, y1, fill, outline, width = op
                self.pen.rectangle(
                    [ox + x0, oy + y0, ox + x1, oy + y1],
                    fill=fill, outline=outline, width=width,
                )
            elif verb == "rrect":
                _, x, y, w, h, r, fill, outline, width = op
                self.pen.rounded_rectangle(
                    [ox + x, oy + y, ox + x + w, oy + y + h],
                    radius=r, fill=fill, outline=outline, width=width,
                )
            elif verb == "line":
                _, pts, fill, width = op
                self.pen.line(
                    [(ox + px, oy + py) for px, py in pts], fill=fill, width=width
                )
            elif verb == "poly":
                _, pts, fill = op
                self.pen.polygon([(ox + px, oy + py) for px, py in pts], fill=fill)
            elif verb == "polyo":
                _, pts, fill, outline = op
                self.pen.polygon(
                    [(ox + px, oy + py) for px, py in pts], fill=fill, outline=outline
                )
            elif verb == "ell":
                _, x0, y0, x1, y1, fill = op
                self.pen.ellipse([ox + x0, oy + y0, ox + x1, oy + y1], fill=fill)
            elif verb == "ello":
                _, x0, y0, x1, y1, fill, outline, width = op
                self.pen.ellipse(
                    [ox + x0, oy + y0, ox + x1, oy + y1],
                    fill=fill, outline=outline, width=width,
                )
            elif verb == "arc":
                _, x0, y0, x1, y1, a0, a1, fill, width = op
                self.pen.arc(
                    [ox + x0, oy + y0, ox + x1, oy + y1],
                    a0, a1, fill=fill, width=width,
                )
            elif verb == "slice":
                _, x0, y0, x1, y1, a0, a1, fill, outline = op
                self.pen.pieslice(
                    [ox + x0, oy + y0, ox + x1, oy + y1],
                    a0, a1, fill=fill, outline=outline,
                )
            elif verb == "text":
                _, x, y, s, kind, size, fill, anchor = op
                self.pen.text(
                    (ox + x, oy + y), s, font=_load_font(kind, size),
                    fill=fill, anchor=anchor,
                )
            elif verb == "flames":
                _, spikes, base, lift = op
                for fx, fh in spikes:
                    self.pen.polygon(
                        [(ox + fx, oy + base), (ox + fx + 8, oy + base - fh),
                         (ox + fx + 16, oy + base)],
                        fill=FLAME_OUTER,
                    )
                    self.pen.polygon(
                        [(ox + fx + 4, oy + base), (ox + fx + 8, oy + base - fh + lift),
                         (ox + fx + 12, oy + base)],
                        fill=FLAME_INNER,
                    )
            elif verb == "flames1":
                # One narrow single-colour flame per spike: a 12-wide
                # triangle, apex 6 across, base at base_y.
                _, spikes, base = op
                for fx, fh in spikes:
                    self.pen.polygon(
                        [(ox + fx, oy + base), (ox + fx + 6, oy + base - fh),
                         (ox + fx + 12, oy + base)],
                        fill=FLAME_OUTER,
                    )
            elif verb == "smoke":
                _, puffs, fill = op
                for sx, sy, sr in puffs:
                    self.pen.ellipse(
                        [ox + sx - sr, oy + sy - sr, ox + sx + sr, oy + sy + sr],
                        fill=fill,
                    )
            elif verb == "pill":
                _, x, y, s, kind, size, bg, fg, outline, width, h, r = op
                fnt = _load_font(kind, size)
                pw = self.pen.textlength(s, font=fnt) + 14
                self.pen.rounded_rectangle(
                    [ox + x, oy + y, ox + x + pw, oy + y + h],
                    radius=r, fill=bg, outline=outline, width=width,
                )
                self.pen.text((ox + x + 7, oy + y + 2), s, font=fnt, fill=fg)
            elif verb == "tag":
                _, x, y, s, kind, size, bg, fg = op
                fnt = _load_font(kind, size)
                bw = self.pen.textlength(s, font=fnt) + 12
                self.pen.rounded_rectangle(
                    [ox + x, oy + y, ox + x + bw, oy + y + 15],
                    radius=3, fill=bg,
                )
                self.pen.text((ox + x + 6, oy + y + 2), s, font=fnt, fill=fg)
            elif verb == "grid":
                _, x0, x1, sx, y0, y1, sy, w, h, fill = op
                for gy in range(y0, y1, sy):
                    for gx in range(x0, x1, sx):
                        self.pen.rectangle(
                            [ox + gx, oy + gy, ox + gx + w, oy + gy + h], fill=fill
                        )
            elif verb == "waves":
                _, x0, x1, step, y0, y1, fill, width = op
                for wx in range(x0, x1, step):
                    self.pen.arc(
                        [ox + wx, oy + y0, ox + wx + 22, oy + y1],
                        180, 360, fill=fill, width=width,
                    )
            elif verb == "chart":
                _, pts, fill, width, dot = op
                self.pen.line(
                    [(ox + px, oy + py) for px, py in pts], fill=fill, width=width
                )
                for px, py in pts:
                    self.pen.ellipse(
                        [ox + px - dot, oy + py - dot, ox + px + dot, oy + py + dot],
                        fill=fill,
                    )
            else:
                raise ValueError("unknown scene verb %r" % (verb,))


# --------------------------------------------------------------------------
# Picture scenes. Each list is one picture, 326x100 for heroes and 194x48
# for mid cards, drawn relative to its own top-left corner. Op shapes:
#   ("rect", x0, y0, x1, y1, fill)            filled rectangle
#   ("recto", x0, y0, x1, y1, fill, outline, width)
#   ("rrect", x, y, w, h, radius, fill, outline, width)
#   ("line", [(x, y), ...], fill, width)
#   ("poly", [(x, y), ...], fill) / ("polyo", ..., fill, outline)
#   ("ell", x0, y0, x1, y1, fill) / ("ello", ..., fill, outline, width)
#   ("arc", x0, y0, x1, y1, a0, a1, fill, width)
#   ("slice", x0, y0, x1, y1, a0, a1, fill, outline)
#   ("text", x, y, string, font, size, fill, anchor)
#   ("flames", [(x, height), ...], base_y, inner_lift)
#   ("flames1", [(x, height), ...], base_y)   narrow single flames
#   ("smoke", [(x, y, radius), ...], fill)
#   ("pill", x, y, string, font, size, bg, fg, outline, width, h, radius)
#   ("tag", x, y, string, font, size, bg, fg)   red badge sized to text
#   ("grid", x0, x1, step_x, y0, y1, step_y, w, h, fill)
#   ("waves", x0, x1, step, y0, y1, fill, width)
#   ("chart", [(x, y), ...], fill, width, dot_radius)
# --------------------------------------------------------------------------

# Two tankers burning at night in the Strait of Hormuz.
HORMUZ_OPS = [
    ("rect", 0, 0, 326, 100, (30, 40, 60)),
    ("rect", 0, 46, 326, 100, (40, 80, 120)),
    ("waves", 6, 320, 26, 52, 62, (180, 210, 235), 2),
    ("poly", [(18, 52), (130, 52), (122, 74), (26, 74)], (30, 30, 36)),
    ("rect", 36, 38, 56, 52, (200, 60, 40)),
    ("rect", 60, 38, 80, 52, (40, 120, 200)),
    ("rect", 84, 38, 104, 52, (220, 170, 40)),
    ("rect", 112, 34, 126, 52, (230, 230, 230)),
    ("flames", [(44, 22), (62, 30), (82, 20), (100, 26)], 38, 10),
    ("smoke", [(60, 8, 8), (84, 2, 10), (106, 6, 7)], (90, 90, 100)),
    ("poly", [(190, 60), (300, 60), (292, 78), (198, 78)], (25, 25, 30)),
    ("rect", 210, 46, 232, 60, (200, 60, 40)),
    ("rect", 238, 48, 258, 60, (40, 120, 200)),
    ("flames1", [(214, 14), (230, 18), (246, 12)], 46),
    ("pill", 8, 6, "2 TANKERS ABLAZE", "sans-bold", 11,
     WHITE, RED_RGB, RED_RGB, 1, 17, 8),
]

# A globe, a torn draft deal, a NO DEAL stamp and a thermometer at 1.5C.
COP31_OPS = [
    ("rect", 0, 0, 326, 100, (207, 232, 228)),
    ("ello", 18, 16, 86, 84, (58, 123, 213), (30, 80, 160), 2),
    ("ell", 30, 32, 50, 52, (80, 180, 90)),
    ("ell", 46, 58, 72, 76, (80, 180, 90)),
    ("ell", 60, 26, 76, 42, (80, 180, 90)),
    ("polyo", [(118, 12), (210, 12), (210, 78), (196, 66), (182, 80),
               (168, 66), (150, 80), (132, 66), (118, 78)],
     WHITE, INK_RGB),
    ("line", [(128, 24), (200, 24)], (150, 150, 150), 2),
    ("line", [(128, 34), (200, 34)], (150, 150, 150), 2),
    ("line", [(128, 44), (200, 44)], (150, 150, 150), 2),
    ("line", [(128, 54), (200, 54)], (150, 150, 150), 2),
    ("recto", 216, 26, 312, 56, None, RED_RGB, 3),
    ("text", 264, 31, "NO DEAL", "sans-bold", 20, RED_RGB, "ma"),
    ("rrect", 118, 22, 18, 62, 9, WHITE, INK_RGB, 2),
    ("rect", 122, 44, 132, 80, (220, 40, 40)),
    ("ello", 112, 76, 142, 106, (220, 40, 40), INK_RGB, 2),
    ("text", 148, 26, "1.5°C", "sans-bold", 13, DARKRED_RGB, "la"),
    ("text", 148, 42, "LIMIT", "sans-bold", 11, INK_RGB, "la"),
    ("text", 148, 56, "AT RISK", "sans-bold", 11, INK_RGB, "la"),
    ("pill", 8, 6, "BLAME GAME BEGINS", "sans-bold", 11,
     WHITE, RED_RGB, RED_RGB, 1, 17, 8),
]

# A damaged apartment block, flames on the roof, a mourning candle.
KYIV_OPS = [
    ("rect", 0, 0, 326, 100, (226, 228, 232)),
    ("rect", 60, 12, 150, 100, (150, 145, 135)),
    ("rect", 60, 12, 150, 18, (110, 108, 100)),
    ("grid", 66, 146, 12, 22, 96, 9, 6, 5, (70, 68, 75)),
    ("poly", [(150, 12), (150, 58), (128, 58), (138, 30)], (40, 38, 44)),
    ("flames", [(68, 16), (86, 24), (104, 15), (120, 20)], 12, 9),
    ("smoke", [(76, 0, 8), (96, -4, 10), (116, 0, 8)], (120, 120, 125)),
    ("rect", 240, 44, 252, 92, (245, 240, 225)),
    ("ell", 242, 32, 250, 46, (255, 200, 60)),
    ("ell", 244, 36, 248, 44, (255, 240, 150)),
    ("tag", 8, 82, "11 KILLED", "sans-bold", 10, RED_RGB, WHITE),
]


# Trump at a podium between the US and Russian flags.
PUTIN_OPS = [
    ("rect", 0, 0, 194, 48, (240, 234, 214)),
    ("rect", 12, 8, 66, 28, (180, 30, 40)),
    ("rect", 12, 12, 66, 15, WHITE),
    ("rect", 12, 20, 66, 23, WHITE),
    ("rect", 12, 8, 30, 20, (20, 40, 120)),
    ("line", [(12, 8), (12, 48)], INK_RGB, 2),
    ("recto", 128, 8, 182, 14, WHITE, INK_RGB, 1),
    ("rect", 128, 14, 182, 21, (0, 60, 180)),
    ("rect", 128, 21, 182, 28, (200, 30, 30)),
    ("line", [(182, 8), (182, 48)], INK_RGB, 2),
    ("ell", 88, 14, 106, 32, (240, 200, 160)),
    ("poly", [(78, 36), (116, 36), (122, 48), (72, 48)], (40, 60, 110)),
    ("poly", [(66, 36), (128, 36), (124, 48), (70, 48)], (120, 85, 50)),
    ("rrect", 118, 30, 66, 14, 7, WHITE, RED_RGB, 1),
    ("text", 151, 31, "“FRIEND”", "sans-bold", 10, RED_RGB, "ma"),
]

# The Capitol dome with a falling red chart and a $6tn tag.
CAPITOL_OPS = [
    ("rect", 0, 0, 194, 48, (214, 228, 240)),
    ("recto", 62, 26, 132, 48, (245, 242, 230), (150, 140, 120), 1),
    ("slice", 72, 2, 122, 34, 180, 360, (245, 242, 230), (150, 140, 120)),
    ("line", [(97, 2), (97, -6)], INK_RGB, 2),
    ("rect", 70, 30, 76, 44, (180, 170, 140)),
    ("rect", 86, 30, 92, 44, (180, 170, 140)),
    ("rect", 102, 30, 108, 44, (180, 170, 140)),
    ("rect", 118, 30, 124, 44, (180, 170, 140)),
    ("chart", [(138, 8), (152, 14), (166, 12), (180, 24), (190, 30)],
     (200, 30, 30), 3, 2),
    ("rrect", 8, 6, 62, 15, 3, RED_RGB, None, 1),
    ("text", 14, 8, "$6 TRILLION", "sans-bold", 10, WHITE, "la"),
]

# A candy factory with a sawtooth roof on fire, chimney at the side.
FACTORY_OPS = [
    ("rect", 0, 0, 194, 48, (226, 228, 232)),
    ("rect", 30, 22, 164, 48, (150, 145, 135)),
    ("poly", [(30, 22), (60, 8), (90, 22), (120, 8), (150, 22), (164, 22)],
     (110, 108, 100)),
    ("rect", 40, 30, 56, 46, (60, 60, 70)),
    ("rect", 140, 30, 156, 46, (60, 60, 70)),
    ("flames", [(48, 16), (72, 22), (96, 14), (120, 20)], 12, 9),
    ("smoke", [(70, 0, 7), (92, -4, 9), (114, 0, 7)], (120, 120, 125)),
    ("rect", 168, 6, 180, 48, (130, 125, 118)),
    ("tag", 8, 30, "3 KILLED · 34 MISSING", "sans-bold", 10, RED_RGB, WHITE),
]

# An exam desk, a paper, and a small robot head peeking over it.
EXAM_OPS = [
    ("rect", 0, 0, 194, 48, (240, 234, 214)),
    ("rect", 40, 36, 154, 48, (120, 80, 50)),
    ("recto", 58, 16, 118, 36, WHITE, INK_RGB, 1),
    ("line", [(64, 24), (112, 24)], (150, 150, 150), 2),
    ("line", [(64, 32), (112, 32)], (150, 150, 150), 2),
    ("line", [(64, 40), (112, 40)], (150, 150, 150), 2),
    ("line", [(64, 48), (96, 48)], (200, 30, 30), 2),
    ("recto", 126, 22, 156, 44, (180, 190, 200), INK_RGB, 1),
    ("ell", 132, 28, 138, 34, (31, 92, 168)),
    ("ell", 144, 28, 150, 34, (31, 92, 168)),
    ("line", [(141, 22), (141, 16)], INK_RGB, 2),
    ("ell", 138, 13, 144, 19, RED_RGB),
    ("rrect", 118, 2, 68, 14, 3, RED_RGB, None, 1),
    ("text", 152, 3, "RESIGNS", "sans-bold", 10, WHITE, "ma"),
]

# A train running between the Nepal and India flags.
TRAIN_OPS = [
    ("rect", 0, 0, 194, 48, (214, 232, 200)),
    ("poly", [(12, 8), (44, 14), (12, 22)], (220, 20, 60)),
    ("line", [(12, 8), (12, 48)], INK_RGB, 2),
    ("rect", 150, 8, 182, 14, (255, 153, 51)),
    ("rect", 150, 14, 182, 20, WHITE),
    ("rect", 150, 20, 182, 26, (19, 136, 8)),
    ("ell", 162, 14, 170, 20, (0, 0, 128)),
    ("line", [(182, 8), (182, 48)], INK_RGB, 2),
    ("rect", 40, 30, 154, 44, (200, 40, 40)),
    ("rect", 40, 30, 70, 44, (20, 40, 120)),
    ("rect", 46, 34, 54, 40, WHITE),
    ("rect", 60, 34, 68, 40, WHITE),
    ("rect", 74, 34, 82, 40, WHITE),
    ("rect", 88, 34, 96, 40, WHITE),
    ("rect", 102, 34, 110, 40, WHITE),
    ("rect", 116, 34, 124, 40, WHITE),
    ("rect", 130, 34, 138, 40, WHITE),
    ("rect", 144, 34, 152, 40, WHITE),
    ("ell", 52, 44, 62, 48, (30, 30, 30)),
    ("ell", 128, 44, 138, 48, (30, 30, 30)),
    ("line", [(0, 48), (194, 48)], (90, 90, 95), 2),
]

# A rising green chart and a gold bitcoin.
BITCOIN_OPS = [
    ("rect", 0, 0, 194, 48, (250, 240, 200)),
    ("chart", [(12, 34), (40, 30), (68, 32), (96, 18), (120, 10)],
     (34, 120, 60), 3, 3),
    ("ello", 138, 6, 178, 46, (247, 147, 26), (180, 110, 10), 2),
    ("text", 158, 13, "₿", "sans-bold", 24, WHITE, "ma"),
]

# An AI chip on dark blue, a red down arrow, falling bars.
CHIP_OPS = [
    ("rect", 0, 0, 194, 48, (20, 32, 64)),
    ("recto", 66, 8, 128, 40, (38, 54, 96), (120, 140, 190), 2),
    ("rect", 82, 16, 112, 32, (90, 220, 120)),
    ("line", [(74, 8), (74, 2)], (150, 170, 210), 2),
    ("line", [(74, 40), (74, 46)], (150, 170, 210), 2),
    ("line", [(90, 8), (90, 2)], (150, 170, 210), 2),
    ("line", [(90, 40), (90, 46)], (150, 170, 210), 2),
    ("line", [(106, 8), (106, 2)], (150, 170, 210), 2),
    ("line", [(106, 40), (106, 46)], (150, 170, 210), 2),
    ("line", [(122, 8), (122, 2)], (150, 170, 210), 2),
    ("line", [(122, 40), (122, 46)], (150, 170, 210), 2),
    ("line", [(150, 8), (150, 34)], (240, 60, 60), 4),
    ("poly", [(142, 28), (158, 28), (150, 42)], (240, 60, 60)),
    ("rect", 18, 34, 26, 44, (240, 60, 60)),
    ("rect", 30, 28, 38, 44, (240, 60, 60)),
    ("rect", 42, 20, 50, 44, (240, 60, 60)),
]

# A departure board, a clock, a plane waiting on the ground.
PLANE_OPS = [
    ("rect", 0, 0, 194, 48, (205, 226, 240)),
    ("rect", 12, 8, 110, 30, (30, 30, 36)),
    ("text", 16, 11, "DELAYED", "sans-bold", 12, (255, 200, 60), "la"),
    ("ello", 155, 7, 181, 33, WHITE, INK_RGB, 2),
    ("line", [(168, 20), (162, 14)], INK_RGB, 2),
    ("line", [(168, 20), (170, 11)], INK_RGB, 2),
    ("ello", 40, 30, 130, 42, (245, 245, 245), (80, 80, 90), 1),
    ("poly", [(118, 31), (144, 22), (148, 31)], (200, 40, 40)),
    ("poly", [(80, 39), (100, 50), (112, 39)], (180, 180, 190)),
    ("ell", 46, 34, 56, 38, (70, 130, 180)),
]

# A medical tent, a red cross, a warning triangle.
CLINIC_OPS = [
    ("rect", 0, 0, 194, 48, (240, 234, 214)),
    ("polyo", [(40, 14), (97, 4), (154, 14), (154, 48), (40, 48)],
     WHITE, INK_RGB),
    ("rect", 84, 22, 110, 34, (200, 30, 30)),
    ("rect", 92, 16, 102, 40, (200, 30, 30)),
    ("polyo", [(162, 14), (178, 38), (146, 38)], (255, 200, 0), INK_RGB),
    ("text", 162, 24, "!", "sans-bold", 14, INK_RGB, "ma"),
    ("rect", 52, 34, 142, 40, (120, 140, 170)),
]

# Three huts with thatched roofs.
VILLAGE_OPS = [
    ("rect", 0, 0, 194, 48, (232, 220, 192)),
    ("recto", 24, 26, 68, 42, (200, 170, 120), (120, 80, 40), 1),
    ("poly", [(20, 26), (46, 10), (72, 26)], (176, 60, 30)),
    ("rect", 42, 34, 52, 42, (90, 60, 30)),
    ("recto", 84, 26, 128, 42, (200, 170, 120), (120, 80, 40), 1),
    ("poly", [(80, 26), (106, 10), (132, 26)], (176, 60, 30)),
    ("rect", 102, 34, 112, 42, (90, 60, 30)),
    ("recto", 138, 26, 182, 42, (200, 170, 120), (120, 80, 40), 1),
    ("poly", [(134, 26), (160, 10), (186, 26)], (176, 60, 30)),
    ("rect", 156, 34, 166, 42, (90, 60, 30)),
    ("tag", 8, 30, "24 CIVILIANS DEAD", "sans-bold", 10, RED_RGB, WHITE),
]


# --------------------------------------------------------------------------
# Story tables. "badge" is the verification level: CONFIRMED means two or
# more outlets, OFFICIAL means on the record, REPORTED means one outlet.
# --------------------------------------------------------------------------

BADGE_FILL = {
    "CONFIRMED": (34, 120, 60),
    "OFFICIAL": (31, 92, 168),
    "REPORTED": (176, 110, 20),
}

HERO_CARDS = [
    {"tag": "HORMUZ: ON FIRE",
     "place": "1  STRAIT OF HORMUZ  ·  WAR",
     "head": "Two oil tankers ablaze after entering a restricted zone",
     "body": "Iran's Revolutionary Guard says the tankers caught fire east of "
             "the strait; oil prices fell anyway as the AI sell-off spread. (WION)",
     "badge": "REPORTED",
     "art": HORMUZ_OPS},
    {"tag": "COP31: NO DEAL",
     "place": "2  ANTALYA, TÜRKIYE  ·  CLIMATE",
     "head": "Climate talks collapse — the blame game begins",
     "body": "Nearly 200 countries left Antalya on Sunday with no cover deal; "
             "on Monday Australia and Pacific nations vented their despair. (Reuters)",
     "badge": "CONFIRMED",
     "art": COP31_OPS},
    {"tag": "KYIV: 11 KILLED",
     "place": "3  KYIV REGION  ·  WAR",
     "head": "Strikes kill 11; the region marks a day of mourning",
     "body": "Rescuers pulled a child alive from a ruined five-storey block in "
             "Dymer as the toll rose; Monday is a day of mourning. (AFP)",
     "badge": "CONFIRMED",
     "art": KYIV_OPS},
]

MID_CARDS = [
    {"tag": "TRUMP: PUTIN",
     "place": "4  WASHINGTON  ·  POLITICS",
     "head": "Trump calls Putin “friend” again",
     "body": "His intelligence chief calls the word “entirely appropriate”. (AP)",
     "badge": "REPORTED",
     "art": PUTIN_OPS},
    {"tag": "TRUMP: DEMS",
     "place": "5  WASHINGTON  ·  POLITICS",
     "head": "Trump blames Democrats for $6tn wipeout",
     "body": "He also blames them for Iran's escalation and calls oil prices "
             "“a giant hoax”. (WION)",
     "badge": "REPORTED",
     "art": CAPITOL_OPS},
    {"tag": "SERANG: FIRE",
     "place": "6  SERANG, INDONESIA  ·  DISASTER",
     "head": "Candy-factory fire: 3 dead, 34 missing",
     "body": "Rescuers keep digging at the Milkita sweets plant in Banten. (AP)",
     "badge": "CONFIRMED",
     "art": FACTORY_OPS},
    {"tag": "SEOUL: RESIGNS",
     "place": "7  SEOUL  ·  EDUCATION",
     "head": "Minister quits over AI cheating scandal",
     "body": "Days before the Suneung college exam, the cheating row claims "
             "its first scalp. (Dawn)",
     "badge": "REPORTED",
     "art": EXAM_OPS},
    {"tag": "DELHI: NEPAL PM",
     "place": "8  NEW DELHI  ·  DIPLOMACY",
     "head": "Nepal's PM makes his first trip abroad",
     "body": "Balendra Shah meets Modi and flags off the Ayodhya–Janakpur Express. (PTI)",
     "badge": "OFFICIAL",
     "art": TRAIN_OPS},
    {"tag": "BITCOIN: $61,590",
     "place": "9  WORLD  ·  MARKETS",
     "head": "Bitcoin rebounds above $61,000",
     "body": "Up 4.4% in a day, clawing back from Saturday's $55,130 low. "
             "(Finnhub, 06:28 UTC)",
     "badge": "CONFIRMED",
     "art": BITCOIN_OPS},
    {"tag": "AI: SELL-OFF",
     "place": "10  ASIA  ·  MARKETS",
     "head": "AI rout deepens across Asian markets",
     "body": "Korea, Taiwan and Hong Kong sink again; Brent slides to $92.29 "
             "a barrel. (WION)",
     "badge": "CONFIRMED",
     "art": CHIP_OPS},
    {"tag": "DELTA: DELAYS",
     "place": "11  ATLANTA  ·  AVIATION",
     "head": "Delta fault delays Thanksgiving flights",
     "body": "An automation-system problem snarls travel at the busiest US holiday. (AP)",
     "badge": "REPORTED",
     "art": PLANE_OPS},
    {"tag": "CONGO: EBOLA",
     "place": "12  CONGO  ·  HEALTH",
     "head": "Fighting disrupts the Ebola response",
     "body": "The WHO chief says clashes near the outbreak area are blocking teams. (AP)",
     "badge": "OFFICIAL",
     "art": CLINIC_OPS},
    {"tag": "S. SUDAN: 24",
     "place": "13  SOUTH SUDAN  ·  CONFLICT",
     "head": "Attack leaves 24 civilians dead",
     "body": "SPLA-IO forces blamed for the assault, the army says. (AP)",
     "badge": "REPORTED",
     "art": VILLAGE_OPS},
]

# Bar colours for the ten mid-card label strips, in card order.
LABEL_FILL = [
    (176, 30, 30), (31, 92, 168), (110, 60, 140), (46, 125, 60), (20, 32, 64),
    (176, 30, 30), (46, 125, 60), (31, 92, 168), (176, 130, 30), (20, 130, 130),
]

# The six-figure strip under the masthead: big figure plus two caption lines.
NUMBER_CELLS = [
    {"figure": "2", "line1": "OIL TANKERS ABLAZE", "line2": "IN THE HORMUZ ZONE"},
    {"figure": "11", "line1": "KILLED BY RUSSIAN", "line2": "STRIKES, KYIV REGION"},
    {"figure": "34", "line1": "MISSING AFTER THE", "line2": "SERANG FACTORY FIRE"},
    {"figure": "144", "line1": "ARRESTED IN FRANCE'S", "line2": "COST-OF-LIVING PROTESTS"},
    {"figure": "24", "line1": "CIVILIANS KILLED IN", "line2": "SOUTH SUDAN ATTACK"},
    {"figure": "$61,590", "line1": "BITCOIN EARLY MONDAY,", "line2": "UP 4.4% IN A DAY"},
]

# Region split of the 35 stories: Europe 7, Asia 11, Middle East 3,
# Africa 3, Americas 7, Oceania 3, and Global 1.
REGION_SLICES = [
    {"name": "EUROPE 7", "color": (31, 92, 168), "count": 7},
    {"name": "ASIA 11", "color": (176, 30, 30), "count": 11},
    {"name": "MIDDLE EAST 3", "color": (176, 130, 30), "count": 3},
    {"name": "AFRICA 3", "color": (46, 125, 60), "count": 3},
    {"name": "AMERICAS 7", "color": (110, 60, 140), "count": 7},
    {"name": "OCEANIA 3", "color": (20, 130, 130), "count": 3},
    {"name": "GLOBAL 1", "color": (110, 110, 110), "count": 1},
]

# Land masses of the small world map, as rough polygons in page coordinates.
LAND_SHAPES = [
    [(28, 772), (60, 762), (95, 766), (120, 772), (128, 790), (110, 806),
     (88, 812), (70, 830), (52, 822), (30, 800), (22, 784)],
    [(128, 758), (142, 756), (146, 766), (134, 770)],
    [(78, 836), (105, 832), (122, 846), (118, 872), (100, 896), (84, 884),
     (74, 858)],
    [(168, 762), (196, 758), (210, 768), (204, 784), (188, 790), (172, 780)],
    [(170, 796), (200, 792), (216, 806), (210, 836), (196, 862), (180, 856),
     (168, 826)],
    [(214, 764), (280, 756), (322, 766), (330, 790), (310, 812), (280, 826),
     (250, 818), (228, 800), (214, 782)],
    [(272, 868), (310, 862), (322, 874), (306, 890), (278, 886)],
]

# Numbered dots on the map: (story, true x, true y, dot x, dot y).
# A dot is drawn at (dot x, dot y); when the true spot is far from the dot
# a leader line joins them. Story 9 has no true spot: it is a global market.
MAP_DOTS = [
    (1, 246, 790, 246, 790),
    (2, 222, 784, 222, 784),
    (3, 238, 800, 248, 812),
    (4, 58, 782, 58, 782),
    (5, 58, 782, 72, 796),
    (6, 300, 838, 300, 838),
    (7, 292, 778, 292, 778),
    (8, 264, 800, 272, 812),
    (9, None, None, 140, 898),
    (10, 296, 786, 312, 772),
    (11, 64, 796, 48, 808),
    (12, 92, 858, 92, 858),
    (13, 104, 846, 122, 836),
]

# Stories 14-35, two columns of eleven.
ALSO_ITEMS = [
    {"num": 14, "head": "Paris: 144 arrested in cost-of-living protests",
     "src": "Qatar Tribune"},
    {"num": 15, "head": "Mexico: 11 killed as cartel leader captured",
     "src": "Qatar Tribune"},
    {"num": 16, "head": "Riyadh: Saudi intercepts Houthi drone, missile",
     "src": "Qatar Tribune"},
    {"num": 17, "head": "Benghazi: blast at naval-base ammo depot",
     "src": "Qatar Tribune"},
    {"num": 18, "head": "London: Britain to build Ukrainian drones",
     "src": "Qatar Tribune"},
    {"num": 19, "head": "Brussels: NATO to discuss airspace violations",
     "src": "Qatar Tribune"},
    {"num": 20, "head": "Kyiv: Zelensky mocks Russia over China summit",
     "src": "ToI"},
    {"num": 21, "head": "Beverly Hills: US seeks mansion in $700m scheme",
     "src": "ToI"},
    {"num": 22, "head": "Italy: AI python photo sparks 48-hour search",
     "src": "ToI"},
    {"num": 23, "head": "Himalaya: El Niño warning for snow, flood risk",
     "src": "ToI"},
    {"num": 24, "head": "Dhaka: garments lost $428m in 18 days of unrest",
     "src": "ToI"},
    {"num": 25, "head": "Lahore: tops world pollution ranking, AQI 500+",
     "src": "ToI"},
    {"num": 26, "head": "Pakistan: 4.0 quake near Afghan border",
     "src": "ToI"},
    {"num": 27, "head": "Jakarta: Prabowo to name VP candidates Monday",
     "src": "Reuters"},
    {"num": 28, "head": "Jakarta: MSCI weighs avoiding Indonesia downgrade",
     "src": "Reuters"},
    {"num": 29, "head": "New Delhi: India–EU trade deal likely signed 16 Dec",
     "src": "Saachi Baat"},
    {"num": 30, "head": "Canberra: Chalmers warns growth “well below” 2%",
     "src": "Evening Report"},
    {"num": 31, "head": "Wellington: NZ retail sales jump 2.2%, beat forecasts",
     "src": "Stats NZ"},
    {"num": 32, "head": "Melbourne: music icon Molly Meldrum dies at 83",
     "src": "Evening Report"},
    {"num": 33, "head": "Tel Aviv: Netanyahu–Eisenkot talks stall",
     "src": "WION"},
    {"num": 34, "head": "Iowa: US Army to detonate bomb-making chemicals",
     "src": "AP"},
    {"num": 35, "head": "Washington: Trump backs Jensen Huang rehire",
     "src": "ET"},
]

DATE_CHECK_TEXT = (
    "DATE CHECK — Left out as earlier news. "
    "Sun 22 Nov: Democrats clinch 258 House seats, their biggest majority since 1992 (AP); "
    "COP31 talks end with no deal (Reuters); California sues OpenAI (Reuters); "
    "Liverpool beat Man Utd in Pochettino's first match. "
    "Sat 21 Nov: BepiColombo enters Mercury orbit (AP); Bitcoin hits a $55,130 low. "
    "Not confirmed when drawn, so not shown: the names of the two Hormuz tankers; "
    "the final toll in the Serang fire."
)


# --------------------------------------------------------------------------
# Page assembly
# --------------------------------------------------------------------------

def paint_top(page):
    """Masthead, date, standfirst and the rule under them."""
    page.box(0, 0, PAGE_W, 5, fill=RED_RGB)
    page.txt(14, 12, "ONE DAY ON EARTH", "sans-bold", 20, RED_RGB)
    page.txt(1010, 14,
             "35 STORIES  ·  7 REGIONS  ·  13 PICTURED  ·  "
             "EVERY ONE DATED MONDAY 23 NOVEMBER 2026",
             "sans-bold", 13, INK_RGB, "ra")
    page.txt(512, 34, "Monday 23 November 2026", "serif-bold", 62, INK_RGB, "ma")
    page.txt(512, 100,
             "Two tankers ablaze in Hormuz  ·  COP31 blame game begins  ·  "
             "Kyiv region mourns 11",
             "serif-italic", 19, INK_RGB, "ma")
    page.seg([14, 122, 1010, 122], fill=INK_RGB, width=2)


def paint_numbers(page):
    """The six-figure strip: big red figures, two caption lines each."""
    cell = 996 / 6
    for i, item in enumerate(NUMBER_CELLS):
        x = 14 + i * cell
        if i:
            page.seg([x - 3, 130, x - 3, 168], fill=(200, 195, 180), width=1)
        page.txt(x + cell / 2, 124, item["figure"], "serif-bold", 32, RED_RGB, "ma")
        page.txt(x + cell / 2, 156, item["line1"], "sans-bold", 10, INK_RGB, "ma")
        page.txt(x + cell / 2, 167, item["line2"], "sans-bold", 10, INK_RGB, "ma")


def paint_regions(page):
    """The seven-segment region bar. Short segments get a minimum width;
    the space that costs is taken back from the two longest segments."""
    spans = []
    for entry in REGION_SLICES:
        spans.append(996 * entry["count"] / 35)
    for k, entry in enumerate(REGION_SLICES):
        if entry["count"] <= 1:
            spans[k] = max(spans[k], 64)
        elif entry["count"] == 3:
            spans[k] = max(spans[k], 88)
    over = sum(spans) - 996
    spans[4] -= over * 0.6
    spans[1] -= over * 0.4
    rx = 14
    for entry, w in zip(REGION_SLICES, spans):
        page.box(rx, 180, rx + w - 1, 200, fill=entry["color"])
        page.txt(rx + w / 2, 184, entry["name"], "sans-bold", 11, WHITE, "ma")
        rx += w


def paint_hero(page, slot, card):
    """One of the three big stories: picture, red label strip, text."""
    x = 14 + slot * 335
    page.scene(card["art"], x, 206)
    page.box(x, 306, x + 326, 328, fill=RED_RGB)
    page.txt(x + 8, 309, card["tag"], "sans-bold", 13, WHITE)
    badge_w = page.measure(card["badge"], "sans-bold", 10) + 12
    page.rbox(x + 326 - badge_w - 6, 310, badge_w, 14, 7,
              fill=BADGE_FILL[card["badge"]], outline=WHITE, width=1)
    page.txt(x + 326 - badge_w, 312, card["badge"], "sans-bold", 10, WHITE)
    page.txt(x, 332, card["place"], "sans-bold", 11, RED_RGB)
    for j, line in enumerate(page.wrap_lines(card["head"], "serif-bold", 19, 326)[:2]):
        page.txt(x, 348 + j * 22, line, "serif-bold", 19)
    for j, line in enumerate(page.wrap_lines(card["body"], "serif", 12, 326)[:3]):
        page.txt(x, 394 + j * 15, line, "serif", 12)


def paint_mid(page, slot, card):
    """One of the ten smaller stories, in a five-across grid, two rows."""
    x = 14 + 200 * (slot % 5)
    y0 = 460 + 140 * (slot // 5)
    page.scene(card["art"], x, y0)
    page.box(x, y0 + 48, x + 194, y0 + 65, fill=LABEL_FILL[slot])
    page.txt(x + 5, y0 + 51, card["tag"], "sans-bold", 11, WHITE)
    badge_w = page.measure(card["badge"], "sans-bold", 9) + 10
    page.rbox(x + 194 - badge_w - 4, y0 + 51, badge_w, 12, 6,
              fill=BADGE_FILL[card["badge"]], outline=WHITE, width=1)
    page.txt(x + 194 - badge_w + 1, y0 + 52, card["badge"], "sans-bold", 9, WHITE)
    page.txt(x, y0 + 69, card["place"], "sans-bold", 9, RED_RGB)
    for j, line in enumerate(page.wrap_lines(card["head"], "serif-bold", 13, 194)[:2]):
        page.txt(x, y0 + 82 + j * 15, line, "serif-bold", 13)
    for j, line in enumerate(page.wrap_lines(card["body"], "serif", 10, 194)[:2]):
        page.txt(x, y0 + 112 + j * 12, line, "serif", 10)


def paint_map(page):
    """Numbered world map for stories 1-13, with a caption underneath."""
    page.txt(14, 742, "WHERE IT HAPPENED", "sans-bold", 13, RED_RGB)
    page.txt(360, 742, "ALSO ON MONDAY 23 NOVEMBER — 22 MORE STORIES",
             "sans-bold", 13, RED_RGB)
    page.box(14, 760, 344, 908, fill=SEA_RGB, outline=(180, 190, 200), width=1)
    for shape in LAND_SHAPES:
        page.poly(shape, fill=LAND_RGB)
    page.ell(158, 758, 166, 766, fill=LAND_RGB)
    for num, tx, ty, dx, dy in MAP_DOTS:
        if tx is not None and (abs(tx - dx) > 4 or abs(ty - dy) > 4):
            page.seg([dx, dy, tx, ty], fill=(120, 120, 120), width=1)
            page.ell(tx - 2, ty - 2, tx + 2, ty + 2, fill=RED_RGB)
        page.ell(dx - 7, dy - 7, dx + 7, dy + 7, fill=RED_RGB, outline=WHITE, width=1)
        page.txt(dx, dy - 6, str(num), "sans-bold", 10, WHITE, "ma")
    page.txt(14, 912,
             "Red numbers mark stories 1–13. No. 9 is Bitcoin — a global market.",
             "sans", 10, GREY_RGB)


def paint_also(page):
    """Stories 14-35 in two columns; long lines shrink a point or two."""
    for k, item in enumerate(ALSO_ITEMS):
        colx = 360 if k < 11 else 690
        y = 760 + (k % 11) * 14
        full = "%d %s (%s)" % (item["num"], item["head"], item["src"])
        size = 11
        while page.measure(full, "sans", size) > 318 and size > 9:
            size -= 1
        page.txt(colx, y, str(item["num"]), "sans-bold", 11, RED_RGB)
        page.txt(colx + 20, y, "%s (%s)" % (item["head"], item["src"]),
                 "sans", size)


def paint_date_check(page):
    """The red-outlined box listing the weekend news left out on purpose."""
    page.box(14, 922, 1010, 968, outline=RED_RGB, width=2)
    for j, line in enumerate(page.wrap_lines(DATE_CHECK_TEXT, "sans", 11, 968)):
        page.txt(22, 926 + j * 14, line, "sans", 11)


def paint_footer(page):
    """Source note, short link, the checking key and the dateline."""
    page.txt(14, 974,
             "Every story here happened, or was first reported, on Monday "
             "23 November 2026. Sources named beside each story. Original drawings.",
             "sans", 10, GREY_RGB)
    page.txt(1010, 974, "make.fun/r/kh987p5b", "sans-bold", 10, GREY_RGB, "ra")
    page.txt(14, 988,
             "HOW WE CHECKED: CONFIRMED = 2+ outlets  ·  OFFICIAL = on the "
             "record  ·  REPORTED = one outlet",
             "sans", 10, GREY_RGB)
    page.txt(1010, 988, "ONE DAY ON EARTH · 23 NOVEMBER 2026",
             "sans", 10, GREY_RGB, "ra")


def build_front_page():
    page = Canvas(PAGE_W, PAGE_H, PAPER_RGB)
    paint_top(page)
    paint_numbers(page)
    paint_regions(page)
    for slot, card in enumerate(HERO_CARDS):
        paint_hero(page, slot, card)
    for slot, card in enumerate(MID_CARDS):
        paint_mid(page, slot, card)
    paint_map(page)
    paint_also(page)
    paint_date_check(page)
    paint_footer(page)
    return page


if __name__ == "__main__":
    out_path = Path(__file__).resolve().parent / "entry.png"
    front = build_front_page()
    front.save(out_path)
    print("entry.png written: %d bytes" % out_path.stat().st_size)
