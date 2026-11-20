"""news-image-20261120 v2 — 'THE WORLD ATLAS'.

Sums up Friday 20 November 2026 in one 1024x1024 image, drawn from scratch
with pure Python stdlib (zlib + struct for PNG). No network, no third-party
deps, deterministic: two runs write byte-identical files.

Concept (new for v2; v1 was a dark 'night desk' storm chart led by the
cyclone): a light-paper world atlas. A stylised world map carries numbered
pins for the day's places; the lead story is the ICJ genocide verdict — the
day's most consequential news — with the cyclone (true 20 Nov landfall) as
the second story with fresher 20 Nov figures.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py   -> out/entry.png
"""
import os
import struct
import zlib

W, H = 1024, 1024

# --- palette (light paper atlas; deliberately unlike v1's dark navy) ---
PAPER = (246, 241, 231)
INK = (25, 23, 19)
VERMILION = (194, 59, 30)
TEAL = (14, 90, 86)
OCHRE = (217, 160, 63)
SLATE = (70, 97, 122)
FAINT = (214, 205, 188)

# --- 5x7 bitmap font, authored in this session ---
# Each glyph: 7 rows, bit 4 = leftmost pixel. 5 px wide + 1 px gap.
FONT = {
    " ": [0, 0, 0, 0, 0, 0, 0],
    "A": [14, 17, 17, 31, 17, 17, 17],
    "B": [30, 17, 17, 30, 17, 17, 30],
    "C": [14, 17, 16, 16, 16, 17, 14],
    "D": [30, 17, 17, 17, 17, 17, 30],
    "E": [31, 16, 16, 30, 16, 16, 31],
    "F": [31, 16, 16, 30, 16, 16, 16],
    "G": [14, 17, 16, 23, 17, 17, 15],
    "H": [17, 17, 17, 31, 17, 17, 17],
    "I": [14, 4, 4, 4, 4, 4, 14],
    "J": [7, 2, 2, 2, 2, 18, 12],
    "K": [17, 18, 20, 24, 20, 18, 17],
    "L": [16, 16, 16, 16, 16, 16, 31],
    "M": [17, 27, 21, 21, 17, 17, 17],
    "N": [17, 25, 21, 19, 17, 17, 17],
    "O": [14, 17, 17, 17, 17, 17, 14],
    "P": [30, 17, 17, 30, 16, 16, 16],
    "Q": [14, 17, 17, 17, 21, 18, 13],
    "R": [30, 17, 17, 30, 20, 18, 17],
    "S": [15, 16, 16, 14, 1, 1, 30],
    "T": [31, 4, 4, 4, 4, 4, 4],
    "U": [17, 17, 17, 17, 17, 17, 14],
    "V": [17, 17, 17, 17, 17, 10, 4],
    "W": [17, 17, 17, 21, 21, 27, 17],
    "X": [17, 17, 10, 4, 10, 17, 17],
    "Y": [17, 17, 10, 4, 4, 4, 4],
    "Z": [31, 1, 2, 4, 8, 16, 31],
    "0": [14, 17, 19, 21, 25, 17, 14],
    "1": [4, 12, 4, 4, 4, 4, 14],
    "2": [14, 17, 1, 6, 8, 16, 31],
    "3": [31, 2, 4, 2, 1, 17, 14],
    "4": [2, 6, 10, 18, 31, 2, 2],
    "5": [31, 16, 30, 1, 1, 17, 14],
    "6": [6, 8, 16, 30, 17, 17, 14],
    "7": [31, 1, 2, 4, 8, 8, 8],
    "8": [14, 17, 17, 14, 17, 17, 14],
    "9": [14, 17, 17, 15, 1, 2, 12],
    ".": [0, 0, 0, 0, 0, 12, 12],
    ",": [0, 0, 0, 0, 12, 4, 8],
    ":": [0, 12, 12, 0, 12, 12, 0],
    ";": [0, 12, 12, 0, 12, 4, 8],
    "'": [4, 4, 8, 0, 0, 0, 0],
    "!": [4, 4, 4, 4, 4, 0, 4],
    "?": [14, 17, 1, 2, 4, 0, 4],
    "-": [0, 0, 0, 14, 0, 0, 0],
    "/": [1, 2, 2, 4, 8, 8, 16],
    "(": [2, 4, 8, 8, 8, 4, 2],
    ")": [8, 4, 2, 2, 2, 4, 8],
    "&": [12, 18, 20, 8, 21, 18, 13],
    "%": [25, 26, 2, 4, 8, 11, 19],
    "+": [0, 4, 4, 31, 4, 4, 0],
    "=": [0, 0, 31, 0, 31, 0, 0],
    '"': [10, 10, 0, 0, 0, 0, 0],
}

# --- copy (all caps; every string rendered on the image) ---
MASTHEAD_KICKER = "THE WORLD IN ONE PICTURE"
MASTHEAD_DATE = "FRIDAY 20 NOVEMBER 2026"
MASTHEAD_SUB = "ONE DAY - EVERY CONTINENT - THE STORIES THAT MATTERED"
LEAD_HEADLINE = "MYANMAR GUILTY OF GENOCIDE"
LEAD_BODY = ("THE WORLD COURT FINDS A STATE GUILTY OF GENOCIDE FOR THE FIRST "
             "TIME - 1.2M ROHINGYA IN EXILE - REPARATIONS ORDERED - BRITAIN "
             "EXPELS MYANMAR'S DEFENCE ATTACHE")
LEAD_TAG = "VERDICT 19 NOV - THE WORLD REACTS 20 NOV"
LEAD_VOTE = "9-6"
COL_A_HEAD = "SHENZHEN"
COL_A_BODY = ("TRUMP, XI AND PUTIN MEET FOR THE FIRST TIME - 90 MINUTES AT "
              "APEC. THEIR PEACE DECLARATION: A NUCLEAR WAR CANNOT BE WON "
              "AND MUST NEVER BE FOUGHT. NO TIMELINES, NO UKRAINE DEAL.")
COL_A_TAG = "19 NOV - FULL TEXT 20 NOV"
COL_B_HEAD = "ODISHA"
COL_B_BODY = ("CYCLONE AKVAN COMES ASHORE AT NOON NEAR GOPALPUR. WINDS "
              "90-100 KM/H, GUSTS 110. 3 LAKH EVACUATED, 423 RESCUE TEAMS, "
              "69 TRAINS CANCELLED.")
COL_B_TAG = "TODAY 20 NOV - NOON IST"
COL_C_HEAD = "SEOUL + MARKETS"
COL_C_BODY = ("SOUTH KOREA'S TOP COURT OVERTURNS EX-PM HAN'S 15-YEAR TERM "
              "AND ORDERS A RETRIAL. SENSEX +1.21%, NIFTY +1.14%.")
COL_C_TAG = "19 NOV"
FOOTER_HEAD = "ALSO TODAY"
FOOTER_BODY = ("APEC ADOPTS SHENZHEN OUTLOOK - NVIDIA CEO AFFAIR SHADOWS "
               "APEC - FIJI DROUGHT DISASTER - WOMEN'S ASIAN HOCKEY TROPHY "
               "OPENS - INDIA V NZ TEST GOES ON")
FOOTER_LINE = "THE WORLD IN ONE PICTURE - FRIDAY 20 NOVEMBER 2026"

TEXT_STRINGS = [
    MASTHEAD_KICKER, MASTHEAD_DATE, MASTHEAD_SUB,
    LEAD_HEADLINE, LEAD_BODY, LEAD_TAG, LEAD_VOTE,
    COL_A_HEAD, COL_A_BODY, COL_A_TAG,
    COL_B_HEAD, COL_B_BODY, COL_B_TAG,
    COL_C_HEAD, COL_C_BODY, COL_C_TAG,
    FOOTER_HEAD, FOOTER_BODY, FOOTER_LINE,
    "1", "2", "3", "4", "THE HAGUE", "SHENZHEN", "GOPALPUR",
    "SEOUL", "AKVAN",
]

WRAP_CHECKS = [
    (LEAD_BODY, 2, 640),
    (COL_A_BODY, 2, 296),
    (COL_B_BODY, 2, 296),
    (COL_C_BODY, 2, 296),
    (FOOTER_BODY, 2, 944),
]


def text_width(text, scale):
    return len(text) * 6 * scale


def wrap_text(text, scale, max_width):
    """Greedy word wrap; every line fits max_width. Words are never split."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if text_width(trial, scale) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.fill_rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def fill_poly(self, pts, color):
        """Scanline fill for a simple polygon (list of (x, y))."""
        if not pts:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                xa, xb = int(xs[j]), int(xs[j + 1])
                self.fill_rect(xa, y, max(0, xb - xa), 1, color)

    def poly_outline(self, pts, color):
        n = len(pts)
        for i in range(n):
            self.line(pts[i][0], pts[i][1], pts[(i + 1) % n][0], pts[(i + 1) % n][1], color)

    def circle(self, cx, cy, r, color, fill=False):
        import math
        for a in range(360):
            t = math.radians(a)
            self.set(round(cx + r * math.cos(t)), round(cy + r * math.sin(t)), color)
        if fill:
            for dy in range(-r, r + 1):
                half = int((r * r - dy * dy) ** 0.5)
                self.fill_rect(cx - half, cy + dy, 2 * half, 1, color)

    def draw_text(self, x, y, text, scale, color):
        """Draw text; raises if the text box would leave the canvas."""
        tw = text_width(text, scale)
        th = 7 * scale
        if x < 0 or y < 0 or x + tw > self.w or y + th > self.h:
            raise ValueError(f"text {text!r} at ({x},{y}) scale {scale} leaves canvas")
        cx = x
        for ch in text:
            glyph = FONT[ch]
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (16 >> col):
                        self.fill_rect(cx + col * scale, y + row * scale, scale, scale, color)
            cx += 6 * scale

    def draw_text_block(self, x, y, text, scale, max_width, color, leading=None):
        lines = wrap_text(text, scale, max_width)
        lh = leading if leading is not None else 7 * scale + 4
        for i, line in enumerate(lines):
            self.draw_text(x, y + i * lh, line, scale, color)
        return len(lines)


# --- stylised world map: rough equirectangular continent outlines (lon, lat) ---
CONTINENTS = [
    [(-168, 66), (-145, 70), (-130, 71), (-115, 73), (-105, 72), (-95, 80),
     (-85, 74), (-82, 66), (-88, 62), (-85, 55), (-80, 58), (-76, 62),
     (-70, 58), (-65, 60), (-60, 52), (-55, 47), (-60, 45), (-65, 44),
     (-70, 42), (-75, 38), (-76, 34), (-80, 32), (-81, 26), (-84, 30),
     (-90, 21), (-91, 19), (-97, 16), (-92, 15), (-95, 16), (-102, 18),
     (-105, 21), (-110, 24), (-114, 29), (-120, 34), (-124, 40), (-124, 48),
     (-125, 49), (-130, 55), (-140, 60), (-155, 58), (-162, 55), (-168, 60)],
    [(-58, 64), (-45, 60), (-30, 68), (-40, 76), (-58, 76), (-60, 70)],
    [(-80, 10), (-72, 12), (-60, 8), (-50, 0), (-40, -5), (-35, -10),
     (-40, -20), (-48, -28), (-58, -35), (-65, -41), (-70, -50),
     (-73, -40), (-72, -20), (-80, -5), (-81, 5)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (32, 31),
     (35, 28), (43, 12), (51, 10), (48, 0), (40, -10), (35, -18),
     (32, -26), (20, -35), (15, -30), (12, -18), (9, 4), (-8, 5)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (12, 55),
     (18, 56), (21, 60), (25, 65), (30, 70), (35, 68), (40, 60), (35, 50),
     (28, 45), (23, 40), (18, 40), (12, 44), (8, 44), (3, 42), (-2, 37)],
    [(35, 36), (40, 42), (48, 44), (55, 47), (60, 55), (68, 68), (75, 73),
     (90, 75), (110, 76), (130, 72), (150, 70), (170, 66), (178, 65),
     (170, 60), (162, 56), (158, 52), (142, 50), (140, 40), (135, 35),
     (130, 32), (127, 35), (122, 38), (120, 30), (115, 22), (108, 18),
     (105, 10), (100, 8), (97, 15), (92, 21), (88, 22), (85, 19),
     (80, 13), (77, 8), (72, 20), (66, 25), (60, 25), (55, 26), (50, 29),
     (48, 30), (43, 35), (40, 36)],
    [(113, -22), (114, -30), (115, -35), (124, -33), (130, -32), (137, -35),
     (140, -38), (147, -39), (150, -37), (153, -27), (153, -20), (146, -19),
     (142, -15), (142, -11), (136, -12), (132, -12), (126, -14), (122, -17),
     (118, -20)],
]

MAP_X0, MAP_Y0, MAP_X1, MAP_Y1 = 40, 168, 984, 452


def lonlat_to_xy(lon, lat):
    x = MAP_X0 + (lon + 170) / 360.0 * (MAP_X1 - MAP_X0)
    y = MAP_Y0 + (75 - lat) / 130.0 * (MAP_Y1 - MAP_Y0)
    return int(round(x)), int(round(y))


def draw_spiral(c, cx, cy, color, turns=2, r_step=8):
    """Cyclone spiral: expanding arcs (vermilion)."""
    import math
    for turn in range(turns):
        r0 = 5 + turn * r_step
        r1 = r0 + r_step
        steps = 60
        prev = None
        for i in range(steps + 1):
            a = math.radians(i * 300.0 / steps + turn * 40)
            r = r0 + (r1 - r0) * i / steps
            p = (round(cx + r * math.cos(a)), round(cy + r * math.sin(a)))
            if prev is not None:
                c.line(prev[0], prev[1], p[0], p[1], color)
            prev = p


def draw_pin(c, lon, lat, num, label, label_xy, label_color=INK):
    x, y = lonlat_to_xy(lon, lat)
    c.circle(x, y, 13, VERMILION, fill=True)
    c.circle(x, y, 13, INK)
    # number inside the pin (scale 2, centred)
    c.draw_text(x - 6, y - 7, num, 2, PAPER)
    lx, ly = label_xy
    c.line(x, y + 13, lx, ly + 7, INK)
    c.draw_text(lx, ly, label, 2, label_color)
    return x, y


def build_canvas():
    c = Canvas(W, H, PAPER)

    # --- top vermilion rule + masthead ---
    c.fill_rect(0, 0, W, 8, VERMILION)
    c.draw_text(40, 26, MASTHEAD_KICKER, 2, VERMILION)
    c.draw_text(40, 52, MASTHEAD_DATE, 5, INK)
    c.draw_text(40, 108, MASTHEAD_SUB, 2, SLATE)
    c.hline(40, 140, 944, INK, 3)

    # --- world map band ---
    c.fill_rect(40, 156, 944, 288, (233, 226, 210))  # map sea tint
    for poly in CONTINENTS:
        pts = [lonlat_to_xy(lon, lat) for lon, lat in poly]
        c.fill_poly(pts, TEAL)
        c.poly_outline(pts, INK)
    # graticule: faint equator + tropics
    _, eq_y = lonlat_to_xy(0, 0)
    c.hline(40, eq_y, 944, FAINT, 1)
    # cyclone spiral offshore in the Bay of Bengal (Akvan), clear of pin 3
    sx, sy = lonlat_to_xy(88, 16)
    draw_spiral(c, sx + 30, sy + 18, VERMILION)
    c.draw_text(sx + 54, sy + 12, "AKVAN", 2, VERMILION)
    # numbered pins: 1 The Hague, 2 Shenzhen, 3 Gopalpur, 4 Seoul
    # (labels placed to avoid every other label, pin and the spiral)
    draw_pin(c, 4.3, 52.1, "1", "THE HAGUE", (596, 168))
    draw_pin(c, 114.1, 22.5, "2", "SHENZHEN", (812, 262))
    draw_pin(c, 84.9, 19.3, "3", "GOPALPUR", (620, 330))
    draw_pin(c, 127.0, 37.5, "4", "SEOUL", (840, 236))
    c.hline(40, 452, 944, INK, 3)

    # --- lead story: ICJ verdict ---
    c.fill_rect(40, 468, 12, 160, VERMILION)
    c.draw_text(72, 484, LEAD_HEADLINE, 4, INK)
    vx = 1024 - 40 - text_width(LEAD_VOTE, 6)
    c.draw_text(vx, 478, LEAD_VOTE, 6, VERMILION)
    c.draw_text_block(72, 540, LEAD_BODY, 2, 640, INK)
    c.draw_text(72, 606, LEAD_TAG, 2, VERMILION)
    c.hline(40, 644, 944, INK, 3)

    # --- three columns ---
    cols = [
        (40, COL_A_HEAD, COL_A_BODY, COL_A_TAG, TEAL),
        (360, COL_B_HEAD, COL_B_BODY, COL_B_TAG, VERMILION),
        (680, COL_C_HEAD, COL_C_BODY, COL_C_TAG, SLATE),
    ]
    for x, head, body, tag, color in cols:
        c.fill_rect(x, 664, 296, 34, color)
        c.draw_text(x + 10, 672, head, 3, PAPER)
        c.draw_text_block(x, 714, body, 2, 296, INK)
        c.draw_text(x, 868, tag, 2, color)
    c.hline(40, 896, 944, INK, 3)

    # --- footer: also today ---
    c.draw_text(40, 916, FOOTER_HEAD, 2, VERMILION)
    c.draw_text_block(40, 944, FOOTER_BODY, 2, 944, INK)
    c.draw_text(40, 992, FOOTER_LINE, 1, SLATE)
    c.fill_rect(0, 1016, W, 8, INK)
    return c


def encode_png(width, height, rgb):
    def chunk(ctype, payload):
        return (struct.pack(">I", len(payload)) + ctype + payload
                + struct.pack(">I", zlib.crc32(ctype + payload) & 0xFFFFFFFF))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def render_png():
    c = build_canvas()
    return encode_png(c.w, c.h, bytes(c.px))


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(render_png())
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
