"""Command line interface: `quickcut build config.yaml [-o out.mp4]`."""
from __future__ import annotations

import argparse
import sys

from . import __version__
from .config import Config, ConfigError
from .render import render


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="quickcut",
        description="Turn screenshots + captions into vertical short-form videos.",
    )
    parser.add_argument("--version", action="version", version=f"quickcut {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="render a project config to MP4")
    build.add_argument("config", help="path to the project YAML/JSON config")
    build.add_argument("-o", "--output", help="output MP4 path (overrides config)")
    build.add_argument("--width", type=int, help="override frame width")
    build.add_argument("--height", type=int, help="override frame height")
    build.add_argument("--fps", type=int, help="override frames per second")

    args = parser.parse_args(argv)

    if args.command == "build":
        try:
            cfg = Config.load(args.config)
            if args.width:
                cfg.width = args.width
            if args.height:
                cfg.height = args.height
            if args.fps:
                cfg.fps = args.fps
            out = render(cfg, args.output)
        except (ConfigError, RuntimeError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(f"done -> {out} ({cfg.total_duration:.1f}s, "
              f"{cfg.width}x{cfg.height} @ {cfg.fps}fps)")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
