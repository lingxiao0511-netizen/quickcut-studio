"""Frame rendering: procedural animated background + template compositing.

Each frame is drawn with Pillow and piped as raw RGB into ffmpeg, which
encodes H.264. No external video assets are required: the dark "tech"
background (vertical gradient + slowly pulsing rings) is generated
procedurally, so a project is fully reproducible from its config + images.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .config import Config
from .layout import Rect, compute_zones, fit_rect

# Colours (RGB)
BG_TOP = (8, 14, 30)
BG_BOTTOM = (16, 32, 64)
RING = (64, 140, 255)
NEON_OUTER = (110, 110, 255)
NEON_INNER = (50, 215, 255)
GOLD = (251, 191, 36)
WHITE = (255, 255, 255)
CAPTION_BG = (0, 0, 0)

_FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in _FONT_CANDIDATES:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _gradient(width: int, height: int) -> Image.Image:
    """Pre-rendered vertical gradient background (rings drawn per frame)."""
    base = Image.new("RGB", (width, height))
    px = base.load()
    for y in range(height):
        t = y / max(1, height - 1)
        row = tuple(round(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3))
        for x in range(width):
            px[x, y] = row
    return base


def _draw_rings(draw: ImageDraw.ImageDraw, width: int, height: int, t: float) -> None:
    """Slowly expanding concentric rings behind the material zone."""
    cx, cy = width / 2, height * 0.42
    max_r = width * 0.75
    for k in range(6):
        phase = (t * 0.07 + k / 6) % 1.0
        r = 40 + phase * max_r
        alpha = int(90 * (1 - phase))
        if alpha <= 0:
            continue
        col = tuple(min(255, c + alpha // 2) for c in RING)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=2)


def _centered(draw: ImageDraw.ImageDraw, cx: float, y: float, text: str,
              font: ImageFont.FreeTypeFont, fill, shadow: bool = True) -> None:
    tw = draw.textlength(text, font=font)
    if shadow:
        draw.text((cx - tw / 2 + 3, y + 3), text, font=font, fill=(0, 0, 0))
    draw.text((cx - tw / 2, y), text, font=font, fill=fill)


def _draw_title(draw: ImageDraw.ImageDraw, cfg: Config, zones) -> None:
    w = cfg.width
    zone = zones.title
    sizes = [0.061, 0.041, 0.034]  # fraction of width, per title line
    fills = [WHITE, GOLD, WHITE]
    total_h = sum(w * s * 1.25 for s in sizes[: len(cfg.title)])
    y = zone.cy - total_h / 2
    for i, line in enumerate(cfg.title):
        size = round(w * sizes[i])
        _centered(draw, w / 2, y, line, load_font(size), fills[i])
        y += size * 1.25


def _draw_caption(draw: ImageDraw.ImageDraw, cfg: Config, zones, text: str) -> None:
    if not text:
        return
    zone = zones.caption
    bar = Rect(zone.x + round(cfg.width * 0.037), zone.y,
               zone.w - round(cfg.width * 0.074), zone.h)
    draw.rounded_rectangle([bar.x, bar.y, bar.x1, bar.y1], radius=bar.h // 4,
                           fill=CAPTION_BG, outline=NEON_INNER, width=2)
    font = load_font(round(cfg.width * 0.033))
    tw = draw.textlength(text, font=font)
    th = font.size
    draw.text((bar.cx - tw / 2, bar.cy - th / 2), text, font=font, fill=WHITE)


def _draw_material(base: Image.Image, draw: ImageDraw.ImageDraw,
                   img: Image.Image, zone: Rect) -> None:
    rect = fit_rect(img.width, img.height, zone)
    fitted = img.resize((rect.w, rect.h), Image.LANCZOS)
    base.paste(fitted, (rect.x, rect.y))
    pad = max(4, round(base.width * 0.006))
    draw.rounded_rectangle(
        [rect.x - pad, rect.y - pad, rect.x1 + pad, rect.y1 + pad],
        radius=pad * 3, outline=NEON_OUTER, width=pad + 4)
    draw.rounded_rectangle(
        [rect.x - pad, rect.y - pad, rect.x1 + pad, rect.y1 + pad],
        radius=pad * 3, outline=NEON_INNER, width=max(2, pad // 2))


def render(cfg: Config, output: str | Path | None = None) -> Path:
    """Render the project described by `cfg` to an H.264 MP4. Returns the path."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg not found on PATH — install ffmpeg to render")
    cfg.validate_images()
    out = cfg.resolve(output or cfg.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    zones = compute_zones(cfg.width, cfg.height)
    background = _gradient(cfg.width, cfg.height)
    images = [Image.open(cfg.resolve(seg.image)).convert("RGB") for seg in cfg.segments]

    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{cfg.width}x{cfg.height}", "-r", str(cfg.fps),
        "-i", "-",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "medium", "-crf", "18",
        "-movflags", "+faststart",
        str(out),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        frame_no = 0
        for seg, img in zip(cfg.segments, images):
            seg_frames = max(1, round(seg.duration * cfg.fps))
            for _ in range(seg_frames):
                t = frame_no / cfg.fps
                frame = background.copy()
                draw = ImageDraw.Draw(frame)
                _draw_rings(draw, cfg.width, cfg.height, t)
                _draw_title(draw, cfg, zones)
                _draw_material(frame, draw, img, zones.material)
                _draw_caption(draw, cfg, zones, seg.caption)
                proc.stdin.write(frame.tobytes())
                frame_no += 1
    finally:
        proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg failed while writing {out}")
    return out
