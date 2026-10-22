"""Configuration loading and validation for QuickCut Studio.

A project is described by a single YAML (or JSON) file:

    title:
      - "Big headline"
      - "Optional second line"
    segments:
      - image: shots/post.png
        caption: "What the viewer should take away"
        duration: 3.0
    output: out.mp4        # optional
    width: 1080            # optional overrides
    height: 1920
    fps: 30

Relative image/output paths are resolved against the config file's folder.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import yaml


class ConfigError(ValueError):
    """Raised when a project config is missing or invalid."""


@dataclass
class Segment:
    image: str
    caption: str = ""
    duration: float = 3.0


@dataclass
class Config:
    title: list[str]
    segments: list[Segment]
    output: str = "output.mp4"
    width: int = 1080
    height: int = 1920
    fps: int = 30
    base_dir: Path = field(default_factory=lambda: Path("."))

    # -- loading ---------------------------------------------------------
    @classmethod
    def load(cls, path: str | Path) -> "Config":
        path = Path(path)
        if not path.is_file():
            raise ConfigError(f"config file not found: {path}")
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".json":
            data = json.loads(text)
        else:
            data = yaml.safe_load(text)
        if not isinstance(data, dict):
            raise ConfigError("config root must be a mapping")
        return cls.from_dict(data, base_dir=path.parent)

    @classmethod
    def from_dict(cls, data: dict, base_dir: Path = Path(".")) -> "Config":
        title = data.get("title")
        if isinstance(title, str):
            title = [title]
        if not title or not all(isinstance(t, str) and t.strip() for t in title):
            raise ConfigError("config needs a non-empty 'title' (string or list of strings)")
        if len(title) > 3:
            raise ConfigError("title supports at most 3 lines")

        raw_segments = data.get("segments")
        if not raw_segments or not isinstance(raw_segments, list):
            raise ConfigError("config needs a non-empty 'segments' list")
        segments: list[Segment] = []
        for i, raw in enumerate(raw_segments):
            if not isinstance(raw, dict) or not raw.get("image"):
                raise ConfigError(f"segment #{i + 1} is missing its 'image' path")
            duration = float(raw.get("duration", 3.0))
            if duration <= 0:
                raise ConfigError(f"segment #{i + 1} duration must be > 0")
            segments.append(
                Segment(
                    image=str(raw["image"]),
                    caption=str(raw.get("caption", "")),
                    duration=duration,
                )
            )

        width = int(data.get("width", 1080))
        height = int(data.get("height", 1920))
        fps = int(data.get("fps", 30))
        if width <= 0 or height <= 0 or fps <= 0:
            raise ConfigError("width/height/fps must be positive")

        return cls(
            title=list(title),
            segments=segments,
            output=str(data.get("output", "output.mp4")),
            width=width,
            height=height,
            fps=fps,
            base_dir=Path(base_dir),
        )

    # -- helpers ---------------------------------------------------------
    def resolve(self, rel: str) -> Path:
        """Resolve a config-relative path against the config's directory."""
        p = Path(rel)
        return p if p.is_absolute() else (self.base_dir / p)

    @property
    def total_duration(self) -> float:
        return sum(s.duration for s in self.segments)

    def validate_images(self) -> None:
        for i, seg in enumerate(self.segments):
            if not self.resolve(seg.image).is_file():
                raise ConfigError(
                    f"segment #{i + 1} image not found: {self.resolve(seg.image)}"
                )
