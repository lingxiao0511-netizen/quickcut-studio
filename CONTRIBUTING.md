# Contributing to QuickCut Studio

Thanks for your interest! Contributions of all sizes are welcome —
bug reports, layout/template ideas, docs fixes, and code.

## Getting set up

```bash
git clone https://github.com/lingxiao0511-netizen/quickcut-studio.git
cd quickcut-studio
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

You also need `ffmpeg` on your PATH
(e.g. `sudo apt install ffmpeg`, `brew install ffmpeg`).

## Running the tests

```bash
pytest
```

Please make sure the full suite passes before opening a pull request.
The render smoke test needs ffmpeg; it skips automatically when ffmpeg
is missing.

## Guidelines

- **Keep the layout invariants.** The title, material and caption zones
  must never overlap, and material must stay uncropped inside its zone.
  If you change layout math, extend `tests/test_layout.py`.
- **No heavy dependencies.** The runtime dependency list is intentionally
  tiny (Pillow + PyYAML + system ffmpeg). Please discuss before adding one.
- **Config stays simple.** New config keys need a row in the README config
  reference (both English and Chinese) and a parsing test.
- Match the existing code style; short, commented-where-it-matters code
  beats clever code.

## Reporting bugs

Open an issue with: your OS, Python version, `ffmpeg -version` output,
the config you used (redact anything private), and the full error message.
