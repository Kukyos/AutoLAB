"""Generate the local image assets Ex4's CSS3 demo needs, all drawn with
PIL -- no network image fetches (project rule). Run once from this folder:

    python generate_assets.py

Produces: border_deco.png, bg_emblem.png, bg_pattern.png,
icon_blade.png, icon_shield.png, icon_potion.png
"""
from PIL import Image, ImageDraw

ORANGE = (232, 121, 44, 255)
LIGHT_ORANGE = (243, 161, 92, 255)
GREEN = (127, 174, 90, 255)
DARK = (28, 27, 24, 255)

# border-image source: 60x60 tile, orange corner medallions + green edge bars,
# transparent center (border-image only ever samples the outer band anyway).
im = Image.new("RGBA", (60, 60), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
d.rectangle([0, 0, 14, 14], fill=ORANGE)
d.rectangle([45, 0, 59, 14], fill=ORANGE)
d.rectangle([0, 45, 14, 59], fill=ORANGE)
d.rectangle([45, 45, 59, 59], fill=ORANGE)
d.rectangle([15, 0, 44, 14], fill=GREEN)
d.rectangle([15, 45, 44, 59], fill=GREEN)
d.rectangle([0, 15, 14, 44], fill=GREEN)
d.rectangle([45, 15, 59, 44], fill=GREEN)
im.save("border_deco.png")

# background layer 1: crest emblem, transparent bg, sits no-repeat bottom-right
im = Image.new("RGBA", (140, 140), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
d.ellipse([10, 10, 130, 130], fill=(36, 34, 32, 235), outline=ORANGE, width=6)
d.polygon([(70, 35), (95, 75), (75, 75), (85, 110), (55, 68), (72, 68)], fill=GREEN)
im.save("bg_emblem.png")

# background layer 2: small diagonal-stripe tile, repeats to fill behind the emblem
im = Image.new("RGBA", (28, 28), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
d.line([(0, 28), (28, 0)], fill=(127, 174, 90, 90), width=6)
d.line([(-14, 14), (14, -14)], fill=(127, 174, 90, 90), width=6)
d.line([(14, 42), (42, 14)], fill=(127, 174, 90, 90), width=6)
im.save("bg_pattern.png")


def icon(name, draw_fn):
    im = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([2, 2, 61, 61], radius=12, fill=(36, 34, 32, 255), outline=(58, 55, 47, 255), width=2)
    draw_fn(d)
    im.save(name)


def blade(d):
    d.polygon([(18, 50), (44, 14), (50, 20), (24, 56)], fill=ORANGE)
    d.line([(14, 54), (22, 46)], fill=LIGHT_ORANGE, width=4)


def shield(d):
    d.polygon([(32, 12), (50, 20), (50, 36), (32, 54), (14, 36), (14, 20)], fill=GREEN)
    d.polygon([(32, 20), (43, 25), (43, 35), (32, 46), (21, 35), (21, 25)], fill=(36, 34, 32, 255))


def potion(d):
    d.rectangle([27, 12, 37, 22], fill=(180, 176, 164, 255))
    d.polygon([(24, 22), (40, 22), (48, 44), (36, 54), (28, 54), (16, 44)], fill=ORANGE)
    d.ellipse([26, 26, 38, 36], fill=LIGHT_ORANGE)


icon("icon_blade.png", blade)
icon("icon_shield.png", shield)
icon("icon_potion.png", potion)

print("wrote border_deco.png, bg_emblem.png, bg_pattern.png, icon_blade/shield/potion.png")
