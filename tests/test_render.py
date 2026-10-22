import shutil
import subprocess

import pytest
from PIL import Image

from quickcut.config import Config
from quickcut.render import render

pytestmark = pytest.mark.skipif(
    shutil.which("ffmpeg") is None, reason="ffmpeg not installed"
)


def _probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,avg_frame_rate",
         "-show_entries", "format=duration", "-of", "json", str(path)],
        capture_output=True, text=True, check=True,
    )
    import json

    return json.loads(out.stdout)


def test_smoke_render_tiny_video(tmp_path):
    img = tmp_path / "shot.png"
    Image.new("RGB", (600, 700), (30, 60, 120)).save(img)
    cfg = Config.from_dict(
        {
            "title": ["Smoke", "test"],
            "segments": [{"image": "shot.png", "caption": "hello", "duration": 1.0}],
            "width": 270,
            "height": 480,
            "fps": 10,
        },
        base_dir=tmp_path,
    )
    out = render(cfg, tmp_path / "out.mp4")
    assert out.is_file() and out.stat().st_size > 0
    info = _probe(out)
    stream = info["streams"][0]
    assert (stream["width"], stream["height"]) == (270, 480)
    num, den = stream["avg_frame_rate"].split("/")
    assert int(num) / int(den) == pytest.approx(10, abs=0.5)
    assert float(info["format"]["duration"]) == pytest.approx(1.0, abs=0.25)
