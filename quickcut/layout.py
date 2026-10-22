"""Three-zone layout math for the QuickCut template.

The frame is split into three stacked, non-overlapping zones:

    +---------------------------+
    |  TITLE   (always visible) |   ~14.5% – 29.5% of height
    +---------------------------+
    |  MATERIAL (image / card)  |   ~30.0% – 84.5% of height
    +---------------------------+
    |  CAPTION BAR              |   ~85.2% – 92.2% of height
    +---------------------------+

Material images are *fitted* (scaled to fit, never cropped, aspect ratio
preserved) and centered inside the material zone, so the source material is
on screen from frame 0 and is never covered by title or caption.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    w: int
    h: int

    @property
    def x1(self) -> int:
        return self.x + self.w

    @property
    def y1(self) -> int:
        return self.y + self.h

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2

    def overlaps(self, other: "Rect") -> bool:
        return not (
            self.x1 <= other.x or other.x1 <= self.x
            or self.y1 <= other.y or other.y1 <= self.y
        )


@dataclass(frozen=True)
class Zones:
    title: Rect
    material: Rect
    caption: Rect


# Zone boundaries as fractions of frame height (top, bottom).
_TITLE = (0.145, 0.295)
_MATERIAL = (0.300, 0.845)
_CAPTION = (0.852, 0.922)
_SIDE_MARGIN = 0.019  # fraction of width kept clear on each side


def compute_zones(width: int, height: int) -> Zones:
    """Return the three layout zones for a frame of the given size."""
    mx = round(width * _SIDE_MARGIN)
    inner_w = width - 2 * mx

    def zone(frac: tuple[float, float]) -> Rect:
        y0 = round(height * frac[0])
        y1 = round(height * frac[1])
        return Rect(mx, y0, inner_w, y1 - y0)

    return Zones(
        title=Rect(0, round(height * _TITLE[0]), width, round(height * (_TITLE[1] - _TITLE[0]))),
        material=zone(_MATERIAL),
        caption=zone(_CAPTION),
    )


def fit_rect(img_w: int, img_h: int, zone: Rect, padding: int = 0) -> Rect:
    """Largest rect with the image's aspect ratio that fits inside `zone`.

    The image is scaled to fit (never cropped) and centered in the zone.
    """
    if img_w <= 0 or img_h <= 0:
        raise ValueError("image dimensions must be positive")
    avail_w = zone.w - 2 * padding
    avail_h = zone.h - 2 * padding
    if avail_w <= 0 or avail_h <= 0:
        raise ValueError("zone too small for the requested padding")
    scale = min(avail_w / img_w, avail_h / img_h)
    w = max(1, round(img_w * scale))
    h = max(1, round(img_h * scale))
    x = zone.x + (zone.w - w) // 2
    y = zone.y + (zone.h - h) // 2
    return Rect(x, y, w, h)
