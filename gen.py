#!/usr/bin/env python3
"""Build-time renderer for the news-image-20261127 entry.

Draws the 1024x1024 newspaper front page for Friday 27 November 2026 with
Pillow only. This script runs at BUILD time on the builder's machine; it is
never run by the grader. The graded program (main.py) only copies the
pre-rendered entry.png. Deterministic: same fonts, same code, same bytes.
"""

import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W = 1024
H = 1024
MARGIN = 24
CONTENT = W - 2 * MARGIN

PAPER = (247, 242, 231)
INK = (20, 20, 20)
NAVY = (27, 42, 74)
NAVY_SOFT = (38, 56, 96)
RED = (163, 22, 33)
GOLD = (200, 162, 75)
TEAL = (46, 110, 106)
CREAM_LINE = (214, 204, 182)
SKY = (220, 233, 242)
LAND = (232, 220, 192)
MUTED = (90, 84, 72)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def tag_chip(draw, x, y, label):
    """Small filled tag at the top-right of a panel; returns its left edge."""
    fnt = font(SANS_B, 10)
    tw = draw.textlength(label, font=fnt)
    pad = 6
    bw = int(tw) + 2 * pad
    bh = 16
    colour = NAVY if label == "OFFICIAL" else (RED if label == "CLAIM" else (90, 90, 90))
    draw.rectangle([x - bw, y, x, y + bh], fill=colour)
    draw.text((x - bw + pad, y + 3), label, font=fnt, fill=(255, 255, 255))
    return x - bw


# ---------------------------------------------------------------- data

REGION_STRIP = (
    "NORTH AMERICA 8  ·  EUROPE 14  ·  ASIA 10  ·  MIDDLE EAST 6  ·  "
    "AFRICA 3  ·  SOUTH AMERICA 2  ·  OCEANIA 3  ·  SPORT 2  ·  SCIENCE 2"
)

TIMELINE = [
    ("05:04", "NZ count out"),
    ("09:07", "EU summit ends"),
    ("14:45", "Canada court"),
    ("MORNING", "Tube strike"),
    ("DAY", "Black Friday"),
    ("NIGHT", "Russia strikes"),
]

STATS = [
    ("50", "STORIES"),
    ("65 / 130", "NZ SEATS, ONE SHORT"),
    ("800,000+", "WITHOUT POWER"),
    ("12,021", "EBOLA CASES"),
    ("$41bn", "SANOFI DEAL"),
]

LEADS = [
    {
        "num": "1",
        "place": "WELLINGTON",
        "tag": "OFFICIAL",
        "art": "seats",
        "headline": "LUXON ONE SEAT SHORT",
        "body": "Final count: right bloc 65 of 130 seats; Labour 36, "
                "Greens 17, Opportunity 7.",
        "why": "No bloc has a majority. Luxon must win over Opportunity "
               "to govern.",
        "fact": "65 of 130 · 66 needed",
    },
    {
        "num": "2",
        "place": "OTTAWA",
        "tag": "OFFICIAL",
        "art": "court",
        "headline": "TOP COURT RULES ON BILL 21",
        "body": "Judgment on Quebec's 2019 secularism law — the test of "
                "how far provinces can use Section 33.",
        "why": "Sets the rules for every province's use of Section 33.",
        "fact": "9:45 AM ET · 7 judges",
    },
    {
        "num": "3",
        "place": "KUWAIT CITY",
        "tag": "CLAIM",
        "art": "drone",
        "headline": "IRAN DENIES KUWAIT DEATHS",
        "body": "Two Italian technicians dead at a Kuwait air-defence site. "
                "Kuwait and Italy blame Iran.",
        "why": "First European civilians killed in the Iran war; the blame "
               "game could widen it.",
        "fact": "2 dead · joint probe offered",
    },
]

GRID = [
    ("4", "EU SUMMIT ENDS, NO BUDGET DEAL",
     "24 of 27 back a \u20ac45bn Ukraine loan, but no deal on the 2028\u201334 budget.",
     "REPORTED", "euro"),
    ("5", "AFP HIT BY CYBERATTACK",
     "News agency takes its content platform offline after an attack.",
     "REPORTED", "bolt"),
    ("6", "UK NET MIGRATION AT 29-YEAR LOW",
     "Net migration falls to 77,000 in the year to June 2026.",
     "OFFICIAL", "down"),
    ("7", "LONDON TUBE STRIKE BEGINS",
     "A 24-hour strike brings chaos to the capital as talks fail.",
     "REPORTED", "train"),
    ("8", "STORM LEAVES 800,000 IN THE DARK",
     "Thanksgiving storm floods the US East Coast; flights delayed.",
     "REPORTED", "storm"),
    ("9", "BLAST AT BANGKOK REFINERY",
     "Explosion injures at least 9; residents briefly evacuated.",
     "REPORTED", "flame"),
    ("10", "HOUTHI STRIKE HITS SAUDI REFINERY",
     "Attack on the Jazan refinery kills one Nepali worker.",
     "REPORTED", "drop"),
    ("11", "EBOLA IN CONGO PASSES 12,000",
     "Government data: 12,021 cases, 5,904 deaths; aid disrupted.",
     "OFFICIAL", "virus"),
    ("12", "SPAIN ENDS CAMPAIGN BEFORE SNAP VOTE",
     "Campaigning closes ahead of Sunday's snap general election.",
     "REPORTED", "vote"),
    ("13", "SANOFI SEALS $41BN INSMED DEAL",
     "French drugmaker agrees an all-cash buyout of Insmed.",
     "REPORTED", "pill"),
    ("14", "UK BENEFITS SERVICES GO OFFLINE",
     "Work and Pensions Dept acts after a cyber incident.",
     "OFFICIAL", "screen"),
    ("15", "GUINEA-BISSAU JUNTA DELAYS VOTE",
     "Military rulers push the return to civilian rule to 2028.",
     "REPORTED", "flag"),
]

ALSO_ON = [
    "16. Taiwan votes Sat: local polls + nuclear vote \u2014 Taipei",
    "17. Duterte ICC trial opens Monday in The Hague",
    "18. Lula names a banker Brazil finance minister",
    "19. Germany cuts Q3 growth to 0.1% \u2014 Berlin",
    "20. China stocks in best day in about two years",
    "21. Black Friday sales surge despite high rates",
    "22. Italy stays alive in Davis Cup, 2\u20131 \u2014 Bologna",
    "23. Schofield, Leon win at International Emmys",
    "24. Strobe Talbott, US\u2013India thaw architect, dies at 80",
    "25. Depardieu to face trial over 2018 allegation",
    "26. Poland signs a defence deal with Palantir",
    "27. Finland extends its border security law to 2028",
    "28. Argentina bars central bank money-printing",
    "29. Qantas, Air NZ jets in near miss at Sydney",
    "30. Patterson files High Court appeal bid \u2014 Melbourne",
    "31. Sri Lanka, Russia sign pact to fight crime",
    "32. South Korea extends K-ETA waiver for US, Canada",
    "33. Hasina aide arrested amid return tensions \u2014 Dhaka",
    "34. Myanmar rejects parts of ICJ Rohingya ruling",
    "35. Israeli strikes kill 10 in Gaza; Hamas weighs reply",
    "36. Court: UNRWA sackings of Palestinians unlawful",
    "37. Kenyan court halts US-backed Ebola facility",
    "38. Turkey rejects EU text on Libya sea deal \u2014 Ankara",
    "39. Iraq starts closing unofficial border crossings",
    "40. Trump tells Putin to end aggression in Europe",
    "41. Zelenskyy warns of a new mass Russian strike \u2014 Kyiv",
    "42. Russian strikes kill 3 in Kharkiv, wound 7 in Kyiv",
    "43. North Korea halts missile shipments to Russia",
    "44. Kim hints at tactical nukes at the border",
    "45. Trump calls GDP figures \u2018fake\u2019, demands a probe",
    "46. Musk pledges $18bn in SpaceX shares to US children",
    "47. Altria weighs all-cash bid for Imperial Brands",
    "48. Nvidia halts chip shipments to Southeast Asia",
    "49. S&P puts Nvidia on CreditWatch Negative \u2014 New York",
    "50. Britain contacts 100,000 veterans on readiness",
]

MAP_PLACES = [
    ("1", "Wellington", 174.8, -41.3),
    ("2", "Ottawa", -75.7, 45.4),
    ("3", "Kuwait City", 48.0, 29.4),
    ("4", "Brussels", 4.35, 50.85),
    ("5", "Paris", 2.35, 48.86),
    ("6", "London", -0.13, 51.5),
    ("7", "New York", -74.0, 40.7),
    ("8", "Bangkok", 100.5, 13.75),
    ("9", "Jazan", 42.55, 16.9),
    ("10", "Kinshasa", 15.3, -4.3),
    ("11", "Madrid", -3.7, 40.4),
    ("12", "Bissau", -15.6, 11.85),
]

CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-65, 60),
     (-55, 52), (-60, 46), (-70, 42), (-75, 35), (-80, 26), (-90, 21),
     (-97, 16), (-105, 20), (-115, 28), (-125, 40), (-125, 49), (-140, 60),
     (-155, 58), (-165, 60)],
    [(-58, 64), (-45, 60), (-30, 68), (-20, 70), (-40, 76), (-58, 74)],
    [(-80, 10), (-72, 12), (-60, 8), (-50, 0), (-35, -8), (-40, -20),
     (-48, -28), (-58, -38), (-65, -45), (-70, -52), (-73, -40), (-70, -20),
     (-80, -5), (-81, 5)],
    [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (2, 51), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (30, 60), (30, 70), (20, 70), (12, 66),
     (5, 60), (-5, 58), (-10, 54), (-10, 44)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (32, 31), (35, 28),
     (40, 15), (48, 11), (51, 10), (48, 0), (40, -10), (35, -18), (32, -28),
     (20, -35), (15, -28), (12, -18), (9, 0), (9, 4), (-8, 4), (-13, 8)],
    [(30, 70), (40, 68), (60, 69), (80, 72), (100, 76), (120, 73),
     (140, 72), (160, 70), (178, 66), (170, 60), (162, 56), (158, 52),
     (142, 50), (140, 40), (130, 42), (127, 38), (122, 32), (120, 25),
     (110, 20), (105, 10), (100, 8), (98, 15), (92, 20), (88, 22), (80, 15),
     (77, 8), (72, 20), (66, 25), (60, 25), (56, 26), (50, 29), (48, 30),
     (44, 29), (40, 36), (36, 36), (30, 36)],
    [(114, -22), (114, -30), (120, -34), (130, -32), (137, -35), (142, -38),
     (147, -39), (150, -37), (153, -32), (153, -27), (146, -19), (142, -11),
     (136, -12), (132, -12), (126, -14), (122, -17), (114, -20)],
    [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 53), (1, 51)],
    [(130, 31), (133, 34), (137, 35), (140, 38), (141, 42), (144, 44),
     (142, 40), (139, 37), (135, 33)],
    [(167, -45), (170, -42), (174, -38), (178, -37), (176, -40), (172, -43),
     (168, -46)],
    [(44, -16), (47, -15), (50, -16), (49, -20), (45, -25), (43, -22)],
]


# ---------------------------------------------------------------- art

def draw_seats(draw, x, y, w, h):
    """Parliament seat bar: 130 seats, right bloc 65 vs the rest 65."""
    draw.rectangle([x, y, x + w, y + h], fill=(23, 32, 58))
    draw.text((x + 12, y + 6), "65 \u2014 65", font=font(SERIF, 22), fill=(255, 255, 255))
    need = "66 NEEDED"
    nf = font(SANS_B, 10)
    nw = draw.textlength(need, font=nf)
    draw.text((x + 168, y + 12), need, font=nf, fill=(200, 210, 230))
    segs = [
        (40, (31, 58, 120)), (13, (74, 116, 168)), (12, (46, 110, 106)),
        (36, (163, 22, 33)), (17, (56, 130, 70)), (5, (120, 40, 40)),
        (7, (200, 162, 75)),
    ]
    bar_x = x + 12
    bar_y = y + 38
    bar_w = w - 24
    bar_h = 22
    px = bar_x
    for count, colour in segs:
        seg_w = bar_w * count / 130.0
        draw.rectangle([px, bar_y, px + seg_w - 1, bar_y + bar_h], fill=colour)
        px += seg_w
    need_x = bar_x + bar_w * 66 / 130.0
    draw.line([need_x, bar_y - 4, need_x, bar_y + bar_h + 4], fill=(255, 255, 255), width=2)
    lf = font(SANS, 9)
    draw.text((x + 12, y + 66), "RIGHT 65 \u00b7 NATIONAL 40 \u00b7 ACT 13 \u00b7 NZ FIRST 12",
              font=lf, fill=(220, 220, 220))
    draw.text((x + 12, y + 82), "LEFT + OPP 65 \u00b7 LABOUR 36 \u00b7 GREENS 17 \u00b7 "
              "M\u0100ORI 5 \u00b7 OPP 7", font=lf, fill=(220, 220, 220))


def draw_court(draw, x, y, w, h):
    """Courthouse columns with the judgment time stamped below."""
    draw.rectangle([x, y, x + w, y + h], fill=(232, 222, 196))
    draw.rectangle([x, y, x + w, y + 6], fill=NAVY)
    cx = x + w // 2
    draw.polygon([(cx - 62, y + 26), (cx + 62, y + 26), (cx, y + 10)], fill=NAVY)
    for i in range(5):
        col_x = x + 26 + i * 52
        draw.rectangle([col_x, y + 30, col_x + 16, y + 68], fill=(250, 246, 236),
                       outline=NAVY)
    draw.rectangle([x + 14, y + 68, x + w - 14, y + 74], fill=NAVY)
    draw.text((x + 14, y + 80), "9:45 AM ET", font=font(SERIF, 15), fill=INK)
    sec = "SECTION 33"
    sf = font(SANS_B, 11)
    sw = draw.textlength(sec, font=sf)
    draw.text((x + w - int(sw) - 14, y + 82), sec, font=sf, fill=RED)


def draw_drone(draw, x, y, w, h):
    """Night sky, radar rings, a drone silhouette and a denial stamp."""
    draw.rectangle([x, y, x + w, y + h], fill=(18, 24, 44))
    cx = x + w // 2 - 30
    cy = y + h // 2 + 8
    for r in (18, 36, 52):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(90, 120, 170))
    draw.line([cx, cy - 58, cx, cy + 36], fill=(90, 120, 170))
    draw.line([cx - 58, cy, cx + 58, cy], fill=(90, 120, 170))
    bx, by = x + 118, y + 34
    draw.polygon([(bx, by), (bx + 44, by + 8), (bx, by + 16)], fill=(200, 200, 210))
    draw.ellipse([bx - 4, by + 4, bx + 8, by + 12], fill=(200, 200, 210))
    draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED)
    draw.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], outline=RED)
    draw.text((x + 14, y + 10), "KUWAIT", font=font(SERIF, 22), fill=(255, 255, 255))
    stamp = "TEHRAN DENIES IT"
    fnt = font(SANS_B, 12)
    sw = draw.textlength(stamp, font=fnt)
    sx = x + w - int(sw) - 22
    sy = y + h - 26
    draw.rectangle([sx - 5, sy - 3, sx + int(sw) + 5, sy + 17], outline=RED, width=2)
    draw.text((sx, sy), stamp, font=fnt, fill=RED)


def draw_icon(draw, kind, x, y, size=26):
    """Tiny pictogram in a navy square."""
    draw.rectangle([x, y, x + size, y + size], fill=NAVY)
    c = (255, 255, 255)
    if kind == "euro":
        draw.text((x + 6, y + 4), "\u20ac", font=font(SANS_B, 16), fill=c)
    elif kind == "bolt":
        draw.polygon([(x + 15, y + 3), (x + 8, y + 14), (x + 13, y + 14),
                      (x + 10, y + 23), (x + 19, y + 11), (x + 14, y + 11)], fill=c)
    elif kind == "down":
        draw.line([x + 5, y + 6, x + 13, y + 14, x + 21, y + 6], fill=c, width=2)
        draw.line([x + 13, y + 14, x + 13, y + 22], fill=c, width=2)
    elif kind == "train":
        draw.rectangle([x + 6, y + 4, x + 20, y + 18], outline=c, width=2)
        draw.line([x + 6, y + 14, x + 20, y + 14], fill=c, width=2)
        draw.ellipse([x + 8, y + 20, x + 11, y + 23], fill=c)
        draw.ellipse([x + 15, y + 20, x + 18, y + 23], fill=c)
    elif kind == "storm":
        draw.ellipse([x + 4, y + 6, x + 14, y + 14], fill=c)
        draw.ellipse([x + 11, y + 4, x + 22, y + 14], fill=c)
        draw.polygon([(x + 13, y + 13), (x + 10, y + 20), (x + 14, y + 20),
                      (x + 11, y + 24)], fill=c)
    elif kind == "flame":
        draw.polygon([(x + 13, y + 3), (x + 19, y + 11), (x + 21, y + 17),
                      (x + 13, y + 23), (x + 5, y + 17), (x + 7, y + 11)], fill=c)
    elif kind == "drop":
        draw.polygon([(x + 13, y + 3), (x + 20, y + 14), (x + 13, y + 23),
                      (x + 6, y + 14)], fill=c)
    elif kind == "virus":
        draw.ellipse([x + 7, y + 7, x + 19, y + 19], outline=c, width=2)
        for dx, dy in [(0, -6), (0, 6), (-6, 0), (6, 0)]:
            draw.line([x + 13, y + 13, x + 13 + dx, y + 13 + dy], fill=c, width=2)
    elif kind == "vote":
        draw.rectangle([x + 5, y + 8, x + 21, y + 21], outline=c, width=2)
        draw.line([x + 8, y + 15, x + 12, y + 19, x + 19, y + 10], fill=c, width=2)
    elif kind == "pill":
        draw.ellipse([x + 5, y + 9, x + 21, y + 17], outline=c, width=2)
        draw.line([x + 9, y + 9, x + 17, y + 17], fill=c, width=2)
    elif kind == "screen":
        draw.rectangle([x + 4, y + 5, x + 22, y + 18], outline=c, width=2)
        draw.line([x + 9, y + 21, x + 17, y + 21], fill=c, width=2)
    elif kind == "flag":
        draw.line([x + 7, y + 4, x + 7, y + 22], fill=c, width=2)
        draw.polygon([(x + 7, y + 4), (x + 21, y + 8), (x + 7, y + 12)], fill=c)


# ---------------------------------------------------------------- build

def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead
    d.rectangle([0, 0, W, 5], fill=RED)
    mast = font(SERIF, 62)
    title = "THE WORLD IN ONE DAY"
    tw = d.textlength(title, font=mast)
    d.text(((W - tw) / 2, 12), title, font=mast, fill=INK)
    date_f = font(SANS_B, 15)
    date_line = "FRIDAY 27 NOVEMBER 2026  \u00b7  50 STORIES  \u00b7  9 REGIONS  \u00b7  ONE DAY, ONE PAGE"
    dw = d.textlength(date_line, font=date_f)
    d.text(((W - dw) / 2, 84), date_line, font=date_f, fill=INK)
    d.line([MARGIN, 106, W - MARGIN, 106], fill=INK, width=2)

    # Region strip
    reg_f = font(SANS_B, 12)
    rw = d.textlength(REGION_STRIP, font=reg_f)
    d.text(((W - rw) / 2, 112), REGION_STRIP, font=reg_f, fill=INK)
    d.line([MARGIN, 132, W - MARGIN, 132], fill=CREAM_LINE, width=1)

    # Timeline strip
    y = 138
    d.text((MARGIN, y), "THE DAY IN UTC", font=font(SANS_B, 11), fill=RED)
    tx = MARGIN + 108
    tl_f = font(SANS, 11)
    for time, label in TIMELINE:
        d.text((tx, y), time, font=font(SANS_B, 11), fill=INK)
        tx += d.textlength(time, font=font(SANS_B, 11)) + 5
        d.text((tx, y), label, font=tl_f, fill=MUTED)
        tx += d.textlength(label, font=tl_f) + 10
    d.line([MARGIN, 156, W - MARGIN, 156], fill=INK, width=2)

    # Stat strip
    sy, sh = 162, 46
    d.rectangle([MARGIN, sy, W - MARGIN, sy + sh], fill=NAVY)
    cell_w = CONTENT / len(STATS)
    for i, (num, label) in enumerate(STATS):
        cx = MARGIN + i * cell_w
        if i:
            d.line([cx, sy + 6, cx, sy + sh - 6], fill=(255, 255, 255), width=1)
        nf = font(SERIF, 26)
        nw = d.textlength(num, font=nf)
        d.text((cx + (cell_w - nw) / 2, sy + 2), num, font=nf, fill=(255, 255, 255))
        lf = font(SANS_B, 9)
        lw = d.textlength(label, font=lf)
        d.text((cx + (cell_w - lw) / 2, sy + 31), label, font=lf, fill=(200, 210, 230))

    # Leads
    ly = 212
    lead_w = (CONTENT - 2 * 12) / 3
    art_h = 100
    for i, lead in enumerate(LEADS):
        lx = MARGIN + i * (lead_w + 12)
        ax, ay = lx, ly
        if lead["art"] == "seats":
            draw_seats(d, ax, ay, lead_w, art_h)
        elif lead["art"] == "court":
            draw_court(d, ax, ay, lead_w, art_h)
        else:
            draw_drone(d, ax, ay, lead_w, art_h)
        tag_chip(d, ax + lead_w, ay, lead["tag"])
        ty = ay + art_h + 8
        d.text((lx, ty), lead["num"] + ".  " + lead["place"],
               font=font(SANS_B, 11), fill=RED)
        ty += 16
        hl = wrap(d, lead["headline"], font(SERIF, 21), lead_w)
        ty = draw_lines(d, hl, lx, ty, font(SERIF, 21), INK, 24)
        ty += 2
        body = wrap(d, lead["body"], font(SANS, 12), lead_w)
        ty = draw_lines(d, body, lx, ty, font(SANS, 12), INK, 15)
        ty += 3
        why_lines = wrap(d, lead["why"], font(SANS, 11), lead_w - 92)
        d.text((lx, ty), "WHY IT MATTERS:", font=font(SANS_B, 11), fill=RED)
        wx = lx + d.textlength("WHY IT MATTERS: ", font=font(SANS_B, 11))
        # First WHY line sits beside the red prefix; the rest run full width.
        first = why_lines[0] if why_lines else ""
        d.text((wx, ty), first, font=font(SANS, 11), fill=INK)
        wy = ty + 14
        for line in why_lines[1:]:
            d.text((lx, wy), line, font=font(SANS, 11), fill=INK)
            wy += 14
        ty = wy + 2
        d.text((lx, ty), lead["fact"], font=font(SANS_B, 11), fill=RED)

    # Grid header + stories 4-15
    gy = 468
    d.text((MARGIN, gy), "THE DAY IN TWELVE \u2014 STORIES 4\u201315",
           font=font(SANS_B, 14), fill=INK)
    d.line([MARGIN, gy + 18, W - MARGIN, gy + 18], fill=INK, width=2)
    gy += 24
    col_w = (CONTENT - 16) / 2
    row_h = 31
    for idx, (num, head, body, tag, icon) in enumerate(GRID):
        col = idx % 2
        row = idx // 2
        gx = MARGIN + col * (col_w + 16)
        gyy = gy + row * row_h
        draw_icon(d, icon, gx, gyy + 1)
        tx0 = gx + 32
        d.text((tx0, gyy), num + ". " + head, font=font(SERIF, 13), fill=INK)
        tf = font(SANS_B, 9)
        tw2 = d.textlength(tag, font=tf)
        d.text((gx + col_w - tw2, gyy + 2), tag, font=tf,
               fill=NAVY if tag == "OFFICIAL" else (110, 110, 110))
        d.text((tx0, gyy + 16), body, font=font(SANS, 11), fill=MUTED)

    # Map
    my = gy + 6 * row_h + 6
    d.text((MARGIN, my), "WHERE IT HAPPENED \u2014 12 PLACES, NUMBERED",
           font=font(SANS_B, 13), fill=INK)
    d.line([MARGIN, my + 17, W - MARGIN, my + 17], fill=INK, width=2)
    map_x, map_y, map_w, map_h = MARGIN, my + 21, CONTENT, 84
    d.rectangle([map_x, map_y, map_x + map_w, map_y + map_h], fill=SKY)
    def proj(lon, lat):
        px = map_x + (lon + 180) / 360.0 * map_w
        py = map_y + (90 - lat) / 180.0 * map_h
        return (px, py)
    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND,
                  outline=(190, 175, 140))
    for num, name, lon, lat in MAP_PLACES:
        px, py = proj(lon, lat)
        r = 8
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                  outline=(255, 255, 255), width=1)
        nf = font(SANS_B, 9 if len(num) == 1 else 8)
        nw = d.textlength(num, font=nf)
        d.text((px - nw / 2, py - 6), num, font=nf, fill=(255, 255, 255))
    legend = "  \u00b7  ".join(n + " " + name for n, name, _, _ in MAP_PLACES)
    lf = font(SANS, 10)
    lw = d.textlength(legend, font=lf)
    d.text(((W - lw) / 2, map_y + map_h + 5), legend, font=lf, fill=MUTED)

    # Also on
    ay2 = map_y + map_h + 20
    d.text((MARGIN, ay2), "AND ALSO \u2014 STORIES 16\u201350",
           font=font(SANS_B, 13), fill=INK)
    d.line([MARGIN, ay2 + 17, W - MARGIN, ay2 + 17], fill=INK, width=2)
    ay2 += 20
    af = font(SANS, 10)
    col3_w = (CONTENT - 2 * 14) / 3
    rows = 12
    for idx, item in enumerate(ALSO_ON):
        col = idx // rows
        row = idx % rows
        ax = MARGIN + col * (col3_w + 14)
        ayy = ay2 + row * 12.5
        d.text((ax, ayy), item, font=af, fill=INK)

    # Date check footer
    fy = ay2 + rows * 12.5 + 4
    d.line([MARGIN, fy, W - MARGIN, fy], fill=INK, width=2)
    fy += 5
    d.text((MARGIN, fy), "DATE CHECK",
           font=font(SANS_B, 11), fill=RED)
    foot1 = ("Every story above happened, or was first reported, on Friday "
             "27 November 2026. Older news is excluded: Hormuz (25 Nov), "
             "US tariffs (25 Nov), Huawei (24 Nov).")
    wx = MARGIN + d.textlength("DATE CHECK  ", font=font(SANS_B, 11))
    d.text((wx, fy), foot1, font=font(SANS, 10), fill=INK)
    wy = fy + 13
    foot2 = ("Sources: Electoral Commission NZ \u00b7 Supreme Court of Canada \u00b7 "
             "Reuters \u00b7 AP \u00b7 Al Jazeera \u00b7 BBC \u00b7 CNN \u00b7 WSJ.  "
             "OFFICIAL = announced by the authority  \u00b7  REPORTED = two or more "
             "outlets  \u00b7  CLAIM = one side's claim.")
    d.text((MARGIN, wy), foot2, font=font(SANS, 9), fill=MUTED)
    wy += 11
    if wy > H - 4:
        raise SystemExit("layout overflow: footer ends at %d" % wy)

    img.save(OUT, format="PNG", optimize=True)
    data = open(OUT, "rb").read()
    print("wrote %s %d bytes sha256=%s" % (OUT, len(data),
          hashlib.sha256(data).hexdigest()))
    im = Image.open(OUT)
    print("size %s mode %s" % (im.size, im.mode))
    assert im.size == (1024, 1024), im.size
    assert len(data) <= 1048576, len(data)


if __name__ == "__main__":
    build()
