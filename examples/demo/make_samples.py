#!/usr/bin/env python3
"""Generate the demo's sample images procedurally (no external assets).

Creates three screenshot-style cards so the demo project runs out of the box:
  shot1_post.png   - a mock social-media post card
  shot2_chart.png  - a simple bar-chart card
  shot3_quote.png  - a big-quote card

Run:  python make_samples.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def card(w, h, bg):
    img = Image.new("RGB", (w, h), bg)
    return img, ImageDraw.Draw(img)


def post_card():
    img, d = card(900, 1000, (16, 20, 28))
    d.ellipse([48, 48, 128, 128], fill=(64, 140, 255))
    d.text((60, 68), "D", font=font(52, True), fill=(255, 255, 255))
    d.text((152, 56), "Demo Creator", font=font(38, True), fill=(255, 255, 255))
    d.text((152, 104), "@demo · 2h", font=font(30), fill=(150, 160, 175))
    lines = [
        "We shipped a new feature today:",
        "longer memory for your projects.",
        "",
        "Start a chat in the morning,",
        "come back after lunch — it picks up",
        "right where you left off.",
    ]
    y = 190
    for line in lines:
        d.text((48, y), line, font=font(40), fill=(235, 238, 242))
        y += 58
    d.rounded_rectangle([48, 640, 852, 920], 24, fill=(24, 90, 70))
    d.text((84, 690), "FEATURE DROP", font=font(34, True), fill=(140, 255, 200))
    d.text((84, 750), "Context that lasts", font=font(52, True), fill=(255, 255, 255))
    d.text((84, 824), "all day long", font=font(52, True), fill=(255, 255, 255))
    d.text((48, 944), "1.2K likes · 340 replies", font=font(28), fill=(150, 160, 175))
    img.save(HERE / "shot1_post.png")


def chart_card():
    img, d = card(900, 1000, (250, 250, 248))
    d.text((48, 48), "Weekly active creators", font=font(40, True), fill=(20, 24, 32))
    d.text((48, 104), "Demo data — generated locally", font=font(28), fill=(110, 118, 130))
    values = [42, 55, 51, 68, 74, 88, 97]
    labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    base_y, max_h = 860, 560
    for i, (v, lab) in enumerate(zip(values, labels)):
        x0 = 70 + i * 112
        bh = max_h * v / 100
        d.rounded_rectangle([x0, base_y - bh, x0 + 72, base_y], 10, fill=(64, 140, 255))
        d.text((x0 + 8, base_y - bh - 44), str(v), font=font(30, True), fill=(20, 24, 32))
        d.text((x0 + 4, base_y + 16), lab, font=font(26), fill=(110, 118, 130))
    d.line([48, base_y, 852, base_y], fill=(200, 205, 212), width=3)
    img.save(HERE / "shot2_chart.png")


def quote_card():
    img, d = card(900, 1000, (30, 24, 64))
    d.text((64, 90), '"', font=font(180, True), fill=(120, 110, 255))
    lines = ["Edit the config,", "not the video.", "", "One YAML file in,", "one MP4 out."]
    y = 320
    for line in lines:
        d.text((64, y), line, font=font(58, True), fill=(255, 255, 255))
        y += 78
    d.text((64, 880), "— the QuickCut idea", font=font(30), fill=(170, 165, 220))
    img.save(HERE / "shot3_quote.png")


if __name__ == "__main__":
    post_card()
    chart_card()
    quote_card()
    print("sample images written to", HERE)
