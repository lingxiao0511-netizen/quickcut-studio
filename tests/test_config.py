import json

import pytest

from quickcut.config import Config, ConfigError


def test_title_string_becomes_single_line():
    cfg = Config.from_dict({"title": "Hello", "segments": [{"image": "a.png"}]})
    assert cfg.title == ["Hello"]
    assert cfg.segments[0].duration == 3.0
    assert cfg.segments[0].caption == ""


def test_defaults_and_total_duration():
    cfg = Config.from_dict(
        {
            "title": ["A", "B"],
            "segments": [
                {"image": "a.png", "duration": 2.0},
                {"image": "b.png", "duration": 1.5},
            ],
        }
    )
    assert (cfg.width, cfg.height, cfg.fps) == (1080, 1920, 30)
    assert cfg.total_duration == 3.5


def test_missing_title_rejected():
    with pytest.raises(ConfigError):
        Config.from_dict({"segments": [{"image": "a.png"}]})


def test_missing_segments_rejected():
    with pytest.raises(ConfigError):
        Config.from_dict({"title": "x", "segments": []})


def test_segment_without_image_rejected():
    with pytest.raises(ConfigError):
        Config.from_dict({"title": "x", "segments": [{"caption": "no image"}]})


def test_non_positive_duration_rejected():
    with pytest.raises(ConfigError):
        Config.from_dict(
            {"title": "x", "segments": [{"image": "a.png", "duration": 0}]}
        )


def test_load_yaml_file(tmp_path):
    p = tmp_path / "proj.yaml"
    p.write_text(
        "title: Demo\nsegments:\n  - image: s.png\n    caption: hi\n    duration: 2\n",
        encoding="utf-8",
    )
    cfg = Config.load(p)
    assert cfg.title == ["Demo"]
    assert cfg.base_dir == tmp_path
    assert cfg.resolve("s.png") == tmp_path / "s.png"


def test_load_json_file(tmp_path):
    p = tmp_path / "proj.json"
    p.write_text(json.dumps({"title": "J", "segments": [{"image": "s.png"}]}))
    assert Config.load(p).title == ["J"]


def test_missing_file_rejected(tmp_path):
    with pytest.raises(ConfigError):
        Config.load(tmp_path / "nope.yaml")
