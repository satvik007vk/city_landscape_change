import ee
import pytest

from src.ndvi_ndwi import add_indices, add_ndbi, add_ndvi, add_ndwi
from src.preprocess.gee_auth import initialize_ee


@pytest.fixture(scope="module", autouse=True)
def _ee():
    initialize_ee()


def _pixel_value(image: ee.Image, band: str) -> float:
    point = ee.Geometry.Point([0, 0])
    return (
        image.select(band)
        .reduceRegion(
            reducer=ee.Reducer.first(), geometry=point, scale=1, crs="EPSG:4326"
        )
        .get(band)
        .getInfo()
    )


def test_add_ndvi():
    image = ee.Image.constant([0.5, 0.1]).rename(["B8", "B4"])
    result = add_ndvi(image)

    assert "NDVI" in result.bandNames().getInfo()
    assert _pixel_value(result, "NDVI") == pytest.approx((0.5 - 0.1) / (0.5 + 0.1))


def test_add_ndwi():
    image = ee.Image.constant([0.3, 0.5]).rename(["B3", "B8"])
    result = add_ndwi(image)

    assert "NDWI" in result.bandNames().getInfo()
    assert _pixel_value(result, "NDWI") == pytest.approx((0.3 - 0.5) / (0.3 + 0.5))


def test_add_ndbi():
    image = ee.Image.constant([0.4, 0.2]).rename(["B11", "B8"])
    result = add_ndbi(image)

    assert "NDBI" in result.bandNames().getInfo()
    assert _pixel_value(result, "NDBI") == pytest.approx((0.4 - 0.2) / (0.4 + 0.2))


def test_add_indices_adds_all_bands():
    image = ee.Image.constant([0.5, 0.1, 0.3, 0.4]).rename(["B8", "B4", "B3", "B11"])
    result = add_indices(image)

    assert {"NDVI", "NDWI", "NDBI"}.issubset(result.bandNames().getInfo())
