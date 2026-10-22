# QuickCut Studio

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue.svg)](https://www.python.org/)

**Turn screenshots + one-line captions into vertical short-form videos.**

QuickCut Studio is a small Python CLI that renders screenshot-based
news/explainer clips for TikTok, Reels, Shorts and WeChat Channels. You
describe a video in one YAML file — a title, a list of images, a caption and
a duration per image — and it produces a ready-to-post **1080×1920, 30 fps
H.264 MP4**.

No video editor, no timeline, no manual framing.

## Why

Short-form creators who post screenshot-driven updates (product news, data,
announcements) repeat the same layout work for every clip: place the
screenshot, keep it readable, add a headline, add a caption. QuickCut fixes
that layout once, as a template:

- **Three-zone template** — title zone (top, always on screen), material
  zone (middle), caption bar (bottom). The zones never overlap.
- **Nothing gets cropped** — material images are fitted into their zone with
  aspect ratio preserved, and are visible from frame 0.
- **Material framed as a card** — each image gets a neon border so
  screenshots read clearly against the background.
- **Procedural background** — a dark tech-style gradient with slowly pulsing
  rings, generated per frame with Pillow. No stock footage or assets needed,
  so every project is fully reproducible from its config.

## Quickstart

Requirements: Python ≥ 3.10 and [ffmpeg](https://ffmpeg.org/) on your PATH.

```bash
pip install quickcut-studio   # or: pip install -e . from a clone
cd examples/demo
python make_samples.py        # generate the demo images (no downloads)
quickcut build config.yaml    # -> examples/demo/output.mp4
```

## Usage

```bash
quickcut build path/to/config.yaml [-o out.mp4] [--width W] [--height H] [--fps N]
```

A minimal config:

```yaml
title:
  - "Big headline"
  - "Optional second line"
segments:
  - image: shots/announcement.png
    caption: "What changed, in one line"
    duration: 3.0
  - image: shots/chart.png
    caption: "The number that matters"
    duration: 4.0
output: out.mp4   # optional; relative to the config file
```

Relative image and output paths are resolved against the config file's
directory. JSON configs with the same keys are also accepted.

## Config reference

| Key | Type | Default | Notes |
| --- | --- | --- | --- |
| `title` | string or list of strings | — (required) | 1–3 lines; line 1 is largest |
| `segments` | list | — (required) | at least one segment |
| `segments[].image` | path | — (required) | PNG/JPG/… anything Pillow reads |
| `segments[].caption` | string | `""` | shown in the bottom caption bar |
| `segments[].duration` | seconds | `3.0` | must be > 0 |
| `output` | path | `output.mp4` | |
| `width` / `height` | int | `1080` / `1920` | override for other formats |
| `fps` | int | `30` | |

## How it works

`quickcut/layout.py` computes the three zones and the uncropped fit;
`quickcut/render.py` draws each frame with Pillow (background, title,
material card, caption bar) and streams raw frames into ffmpeg for H.264
encoding. Layout invariants — zones never overlap, fitted material always
stays inside its zone — are covered by the test suite.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Roadmap

- [ ] Multiple background themes (light, minimal, custom image/video)
- [ ] Optional voiceover track mixing (pre-recorded audio per segment)
- [ ] Ken Burns / subtle zoom on material images
- [ ] Batch mode: render many configs in one run
- [ ] Custom fonts and accent colours in config

## License

MIT — see [LICENSE](LICENSE). Chinese documentation: [README.zh-CN.md](README.zh-CN.md).
