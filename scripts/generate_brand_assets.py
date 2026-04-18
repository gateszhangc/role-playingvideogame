from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "assets" / "brand"
SCENES = ROOT / "assets" / "images" / "scenes"
FONTS = ROOT / "assets" / "fonts"

PALETTE = {
    "night": "#121714",
    "night_deep": "#0B100D",
    "forest": "#1C2A25",
    "stone": "#2E3F3A",
    "mist": "#C8D8CD",
    "signal": "#D2E7BF",
    "ember": "#D9744B",
    "ember_dark": "#9F4D32",
    "slate": "#8AA29C",
}

random.seed(7)


def rgba(hex_code: str, alpha: int = 255) -> tuple[int, int, int, int]:
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size=size)


def vertical_gradient(size: tuple[int, int], top: str, bottom: str) -> Image.Image:
    width, height = size
    image = Image.new("RGBA", size)
    draw = ImageDraw.Draw(image)
    top_rgb = rgba(top)
    bottom_rgb = rgba(bottom)
    for y in range(height):
        ratio = y / max(height - 1, 1)
        color = tuple(
            int(top_rgb[i] * (1 - ratio) + bottom_rgb[i] * ratio) for i in range(4)
        )
        draw.line((0, y, width, y), fill=color)
    return image


def add_grain(image: Image.Image, strength: int = 24) -> Image.Image:
    width, height = image.size
    noise = Image.effect_noise((width, height), strength).convert("L")
    noise = ImageOps.colorize(noise, black="#09100c", white="#d6e0d8").convert("RGBA")
    noise.putalpha(40)
    return Image.alpha_composite(image, noise)


def add_topography(layer: Image.Image, *, spacing: int, offset: int, alpha: int) -> None:
    draw = ImageDraw.Draw(layer)
    width, height = layer.size
    for y in range(-height // 3, height + height // 3, spacing):
        points = []
        for x in range(-100, width + 100, 80):
            wave = math.sin((x + offset) / 180) * 18 + math.cos((y + offset) / 95) * 14
            points.append((x, y + wave + math.sin(x / 45) * 8))
        draw.line(points, fill=rgba(PALETTE["mist"], alpha), width=1)


def add_glow(base: Image.Image, bbox: tuple[int, int, int, int], color: str, alpha: int, blur: int) -> None:
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    draw.ellipse(bbox, fill=rgba(color, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(glow)


def draw_compass_mark(image: Image.Image, center: tuple[float, float], scale: float) -> None:
    draw = ImageDraw.Draw(image)
    cx, cy = center
    outer = [
        (cx, cy - 148 * scale),
        (cx + 106 * scale, cy),
        (cx, cy + 148 * scale),
        (cx - 106 * scale, cy),
    ]
    inner = [
        (cx, cy - 98 * scale),
        (cx + 68 * scale, cy),
        (cx, cy + 98 * scale),
        (cx - 68 * scale, cy),
    ]
    core = [
        (cx, cy - 46 * scale),
        (cx + 34 * scale, cy),
        (cx, cy + 46 * scale),
        (cx - 34 * scale, cy),
    ]

    draw.polygon(outer, fill=rgba(PALETTE["signal"], 208))
    draw.polygon(inner, fill=rgba(PALETTE["night"], 255))
    draw.polygon(core, fill=rgba(PALETTE["ember"], 255))
    draw.line((cx, cy - 172 * scale, cx, cy + 172 * scale), fill=rgba(PALETTE["mist"], 168), width=max(1, int(8 * scale)))
    draw.line((cx - 120 * scale, cy, cx + 120 * scale, cy), fill=rgba(PALETTE["mist"], 168), width=max(1, int(6 * scale)))
    draw.arc(
        (cx - 158 * scale, cy - 158 * scale, cx + 158 * scale, cy + 158 * scale),
        start=18,
        end=342,
        fill=rgba(PALETTE["mist"], 122),
        width=max(1, int(5 * scale)),
    )
    draw.arc(
        (cx - 118 * scale, cy - 118 * scale, cx + 118 * scale, cy + 118 * scale),
        start=198,
        end=522,
        fill=rgba(PALETTE["ember"], 150),
        width=max(1, int(3 * scale)),
    )


def save_webp(image: Image.Image, path: Path, quality: int = 92) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(path, format="WEBP", quality=quality, method=6)


def make_hero() -> None:
    size = (1800, 1200)
    base = vertical_gradient(size, PALETTE["night_deep"], PALETTE["forest"])
    paint = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(paint)

    add_glow(base, (1250, 115, 1660, 525), PALETTE["signal"], 185, 60)
    add_glow(base, (1180, 70, 1710, 600), PALETTE["mist"], 80, 100)

    for idx, color in enumerate((PALETTE["stone"], PALETTE["forest"], PALETTE["night"])):
        top = 640 + idx * 90
        points = [
            (-120, 1220),
            (0, top + random.randint(-40, 45)),
            (320, top - 90 - idx * 18),
            (610, top + random.randint(-80, 22)),
            (940, top - 110),
            (1280, top + random.randint(-70, 60)),
            (1650, top - 130),
            (1920, top + 35),
            (1920, 1220),
        ]
        draw.polygon(points, fill=rgba(color, 255))

    add_topography(paint, spacing=78, offset=70, alpha=26)

    tower_color = rgba("#111816", 255)
    for x, height in ((520, 270), (610, 330), (710, 245), (810, 300)):
        draw.rectangle((x, 410, x + 44, 410 + height), fill=tower_color)
        draw.polygon([(x - 8, 410), (x + 22, 356), (x + 52, 410)], fill=tower_color)
    draw.rectangle((486, 650, 880, 706), fill=tower_color)

    route = Image.new("RGBA", size, (0, 0, 0, 0))
    route_draw = ImageDraw.Draw(route)
    route_points = [(1060, 900), (980, 830), (915, 775), (862, 738), (800, 706), (706, 679)]
    route_draw.line(route_points, fill=rgba(PALETTE["ember"], 220), width=8)
    for x, y in route_points:
        route_draw.ellipse((x - 14, y - 14, x + 14, y + 14), fill=rgba(PALETTE["signal"], 200))
    route = route.filter(ImageFilter.GaussianBlur(6))
    base.alpha_composite(route)
    base.alpha_composite(paint)

    frame = Image.new("RGBA", size, (0, 0, 0, 0))
    frame_draw = ImageDraw.Draw(frame)
    frame_draw.rectangle((48, 48, 1752, 1152), outline=rgba(PALETTE["mist"], 88), width=1)
    frame_draw.rectangle((76, 76, 1724, 1124), outline=rgba(PALETTE["mist"], 42), width=1)
    frame_draw.arc((1230, 170, 1675, 615), 42, 336, fill=rgba(PALETTE["mist"], 108), width=2)
    frame_draw.arc((1160, 100, 1745, 685), 18, 342, fill=rgba(PALETTE["ember"], 68), width=1)
    base.alpha_composite(frame)

    label = Image.new("RGBA", size, (0, 0, 0, 0))
    draw_label = ImageDraw.Draw(label)
    title_font = load_font("YoungSerif-Regular.ttf", 90)
    mono_font = load_font("IBMPlexMono-Regular.ttf", 22)
    draw_label.text((74, 86), "Quest Atlas", font=title_font, fill=rgba(PALETTE["mist"], 225))
    draw_label.text((76, 185), "ROLE-PLAYING VIDEO GAME / EDITORIAL GUIDE", font=mono_font, fill=rgba(PALETTE["signal"], 168))
    base.alpha_composite(label)

    image = add_grain(base)
    save_webp(image, SCENES / "hero-atlas.webp")


def make_party_scene() -> None:
    size = (1280, 960)
    base = vertical_gradient(size, PALETTE["night_deep"], PALETTE["forest"])
    paint = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(paint)

    add_glow(base, (430, 600, 660, 830), PALETTE["ember"], 220, 42)
    add_glow(base, (360, 560, 730, 900), PALETTE["signal"], 40, 70)

    for idx, color in enumerate((PALETTE["stone"], PALETTE["forest"], PALETTE["night"])):
        top = 420 + idx * 120
        points = [
            (-50, 1000),
            (0, top + random.randint(0, 80)),
            (260, top - 120),
            (520, top - 30),
            (760, top - 180),
            (980, top - 40),
            (1280, top - 140),
            (1280, 1000),
        ]
        draw.polygon(points, fill=rgba(color, 255))

    for x in range(160, 1140, 110):
        y = 140 + int(math.sin(x / 70) * 18)
        draw.ellipse((x, y, x + 4, y + 4), fill=rgba(PALETTE["mist"], 170))

    for x, width in ((250, 84), (790, 96)):
        draw.polygon([(x, 700), (x + width / 2, 620), (x + width, 700)], fill=rgba(PALETTE["night"], 255))
        draw.rectangle((x + width * 0.42, 700, x + width * 0.58, 760), fill=rgba(PALETTE["night"], 255))

    for x in (490, 560, 635):
        draw.rectangle((x, 682, x + 18, 756), fill=rgba(PALETTE["night"], 255))
        draw.ellipse((x - 8, 650, x + 26, 684), fill=rgba(PALETTE["night"], 255))

    add_topography(paint, spacing=92, offset=160, alpha=22)
    base.alpha_composite(paint)
    image = add_grain(base)
    save_webp(image, SCENES / "party-camp.webp")


def make_dungeon_scene() -> None:
    size = (1280, 960)
    base = vertical_gradient(size, PALETTE["night"], PALETTE["stone"])
    paint = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(paint)

    draw.rounded_rectangle((92, 92, 1188, 868), radius=18, outline=rgba(PALETTE["mist"], 80), width=2)
    draw.rounded_rectangle((132, 132, 1148, 828), radius=14, outline=rgba(PALETTE["mist"], 44), width=1)

    cell = 88
    for x in range(140, 1141, cell):
        draw.line((x, 132, x, 828), fill=rgba(PALETTE["mist"], 34), width=1)
    for y in range(132, 829, cell):
        draw.line((132, y, 1148, y), fill=rgba(PALETTE["mist"], 34), width=1)

    walls = [
        (220, 220, 1010, 268),
        (220, 220, 268, 620),
        (474, 308, 522, 700),
        (738, 220, 786, 620),
        (308, 572, 740, 620),
        (650, 484, 1010, 532),
        (914, 356, 962, 744),
    ]
    for wall in walls:
        draw.rounded_rectangle(wall, radius=6, fill=rgba(PALETTE["night_deep"], 255))

    route_points = [(268, 268), (436, 268), (436, 576), (740, 576), (740, 508), (938, 508), (938, 744)]
    route = Image.new("RGBA", size, (0, 0, 0, 0))
    route_draw = ImageDraw.Draw(route)
    route_draw.line(route_points, fill=rgba(PALETTE["signal"], 240), width=10)
    for x, y in route_points:
        route_draw.ellipse((x - 16, y - 16, x + 16, y + 16), fill=rgba(PALETTE["ember"], 220))
    route = route.filter(ImageFilter.GaussianBlur(5))
    base.alpha_composite(route)

    add_topography(paint, spacing=128, offset=40, alpha=16)
    base.alpha_composite(paint)
    image = add_grain(base)
    save_webp(image, SCENES / "dungeon-grid.webp")


def make_map_scene() -> None:
    size = (1280, 960)
    base = vertical_gradient(size, PALETTE["forest"], PALETTE["night_deep"])
    paint = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(paint)

    land_masses = [
        [(110, 210), (330, 140), (510, 220), (460, 420), (280, 520), (140, 420)],
        [(720, 240), (980, 170), (1140, 280), (1070, 520), (870, 610), (700, 480)],
        [(420, 620), (640, 560), (850, 640), (820, 820), (540, 840), (380, 730)],
    ]
    for mass in land_masses:
        draw.polygon(mass, fill=rgba(PALETTE["stone"], 210), outline=rgba(PALETTE["mist"], 90))

    for x in range(120, 1160, 120):
        draw.line((x, 90, x, 870), fill=rgba(PALETTE["mist"], 18), width=1)
    for y in range(90, 870, 120):
        draw.line((90, y, 1190, y), fill=rgba(PALETTE["mist"], 18), width=1)

    markers = [(230, 310), (404, 360), (620, 680), (860, 420), (990, 320)]
    route = Image.new("RGBA", size, (0, 0, 0, 0))
    route_draw = ImageDraw.Draw(route)
    route_draw.line(markers, fill=rgba(PALETTE["signal"], 190), width=6)
    for x, y in markers:
        route_draw.ellipse((x - 18, y - 18, x + 18, y + 18), fill=rgba(PALETTE["ember"], 230))
    route = route.filter(ImageFilter.GaussianBlur(5))
    base.alpha_composite(route)

    add_topography(paint, spacing=108, offset=220, alpha=20)
    base.alpha_composite(paint)
    image = add_grain(base)
    save_webp(image, SCENES / "world-map.webp")


def make_logo_assets() -> None:
    BRAND.mkdir(parents=True, exist_ok=True)

    mark = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    glow = Image.new("RGBA", mark.size, (0, 0, 0, 0))
    add_glow(glow, (86, 86, 426, 426), PALETTE["signal"], 80, 44)
    mark.alpha_composite(glow)
    draw_compass_mark(mark, (256, 256), 1.0)
    border = ImageDraw.Draw(mark)
    border.rounded_rectangle((28, 28, 484, 484), radius=24, outline=rgba(PALETTE["mist"], 70), width=2)
    mark.save(BRAND / "logo-mark.png")

    favicon = Image.new("RGBA", (256, 256), rgba(PALETTE["night"]))
    add_glow(favicon, (34, 34, 222, 222), PALETTE["signal"], 70, 34)
    draw_compass_mark(favicon, (128, 128), 0.48)
    favicon.save(BRAND / "favicon.png")
    favicon.save(BRAND / "favicon.ico", sizes=[(256, 256), (128, 128), (64, 64), (32, 32)])
    favicon.resize((180, 180), Image.Resampling.LANCZOS).save(BRAND / "apple-touch-icon.png")

    wordmark = Image.new("RGBA", (1400, 360), (0, 0, 0, 0))
    draw = ImageDraw.Draw(wordmark)
    mark_small = mark.resize((240, 240), Image.Resampling.LANCZOS)
    wordmark.alpha_composite(mark_small, (18, 60))
    title_font = load_font("YoungSerif-Regular.ttf", 132)
    sub_font = load_font("IBMPlexMono-Regular.ttf", 34)
    draw.text((290, 86), "Quest Atlas", font=title_font, fill=rgba("#EEF4EF"))
    draw.text((296, 238), "ROLE-PLAYING VIDEO GAME GUIDE", font=sub_font, fill=rgba(PALETTE["signal"], 204))
    draw.line((296, 226, 1332, 226), fill=rgba(PALETTE["mist"], 72), width=2)
    wordmark.save(BRAND / "logo-wordmark.png")

    social = vertical_gradient((1200, 630), PALETTE["night_deep"], PALETTE["forest"])
    add_glow(social, (750, 80, 1120, 450), PALETTE["signal"], 90, 54)
    social_overlay = Image.new("RGBA", (1200, 630), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(social_overlay)
    add_topography(social_overlay, spacing=82, offset=44, alpha=24)
    overlay_draw.rectangle((28, 28, 1172, 602), outline=rgba(PALETTE["mist"], 72), width=1)
    overlay_draw.rectangle((60, 60, 1140, 570), outline=rgba(PALETTE["mist"], 38), width=1)
    social.alpha_composite(social_overlay)
    social.alpha_composite(mark.resize((250, 250), Image.Resampling.LANCZOS), (780, 196))
    draw = ImageDraw.Draw(social)
    mono_font = load_font("IBMPlexMono-Regular.ttf", 24)
    title_font = load_font("YoungSerif-Regular.ttf", 76)
    text_font = load_font("InstrumentSans-Regular.ttf", 28)
    draw.text((76, 88), "QUEST ATLAS", font=mono_font, fill=rgba(PALETTE["signal"], 188))
    draw.text((76, 148), "Role-Playing\nVideo Game", font=title_font, fill=rgba("#EEF4EF"))
    draw.text(
        (80, 382),
        "Worlds, progression, combat, and choice.\nA clear guide to how RPGs create identity through systems.",
        font=text_font,
        fill=rgba("#DCE7DF"),
        spacing=12,
    )
    social = add_grain(social, 18)
    social.save(BRAND / "social-card.png")


def main() -> None:
    make_logo_assets()
    make_hero()
    make_party_scene()
    make_dungeon_scene()
    make_map_scene()


if __name__ == "__main__":
    main()
