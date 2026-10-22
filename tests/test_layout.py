import pytest

from quickcut.layout import compute_zones, fit_rect

SIZES = [(1080, 1920), (720, 1280), (270, 480), (1080, 1080), (360, 640)]


@pytest.mark.parametrize("w,h", SIZES)
def test_zones_never_overlap(w, h):
    z = compute_zones(w, h)
    assert not z.title.overlaps(z.material)
    assert not z.material.overlaps(z.caption)
    assert not z.title.overlaps(z.caption)


@pytest.mark.parametrize("w,h", SIZES)
def test_zones_stacked_top_to_bottom(w, h):
    z = compute_zones(w, h)
    assert z.title.y1 <= z.material.y
    assert z.material.y1 <= z.caption.y
    for zone in (z.title, z.material, z.caption):
        assert 0 <= zone.x and zone.x1 <= w
        assert 0 <= zone.y and zone.y1 <= h


@pytest.mark.parametrize("w,h", SIZES)
def test_fit_stays_inside_material_zone(w, h):
    z = compute_zones(w, h)
    for img_w, img_h in [(1179, 1373), (1920, 1080), (800, 800), (400, 1200)]:
        r = fit_rect(img_w, img_h, z.material)
        assert z.material.x <= r.x and r.x1 <= z.material.x1
        assert z.material.y <= r.y and r.y1 <= z.material.y1


def test_fit_preserves_aspect_ratio():
    z = compute_zones(1080, 1920)
    r = fit_rect(1600, 900, z.material)
    assert abs(r.w / r.h - 1600 / 900) < 0.02


def test_fit_is_centered():
    z = compute_zones(1080, 1920)
    r = fit_rect(500, 500, z.material)
    assert abs(r.cx - z.material.cx) <= 1
    assert abs(r.cy - z.material.cy) <= 1


def test_fit_rejects_bad_image_size():
    z = compute_zones(1080, 1920)
    with pytest.raises(ValueError):
        fit_rect(0, 100, z.material)
