# Changelog

All notable changes to QuickCut Studio are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/),
and the project uses [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-10-22

### Added

- `quickcut build` CLI: render a YAML/JSON project config to an H.264 MP4.
- Fixed three-zone template (title / material / caption) at 1080×1920, 30 fps,
  with width/height/fps overrides.
- Uncropped, aspect-preserving fit for material images; material visible
  from frame 0; neon border card framing.
- Procedural animated background (dark gradient + pulsing rings) drawn with
  Pillow — no external video assets required.
- Config validation with clear error messages.
- Runnable demo under `examples/demo/` with procedurally generated samples.
- Test suite covering config parsing, layout invariants and a render smoke
  test; GitHub Actions CI on Ubuntu.
