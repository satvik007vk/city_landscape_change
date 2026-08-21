import ee
import pytest

from src.gee_auth import initialize_ee
from src.ndvi_ndwi import add_indices, add_ndvi, add_ndwi


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


def test_add_ndvi_adds_band_with_expected_value():
    image = ee.Image.constant([0.5, 0.1]).rename(["B8", "B4"])
    result = add_ndvi(image)

    assert "NDVI" in result.bandNames().getInfo()
    assert _pixel_value(result, "NDVI") == pytest.approx((0.5 - 0.1) / (0.5 + 0.1))


def test_add_ndwi_adds_band_with_expected_value():
    image = ee.Image.constant([0.3, 0.5]).rename(["B3", "B8"])
    result = add_ndwi(image)

    assert "NDWI" in result.bandNames().getInfo()
    assert _pixel_value(result, "NDWI") == pytest.approx((0.3 - 0.5) / (0.3 + 0.5))


def test_add_indices_adds_both_bands():
    image = ee.Image.constant([0.5, 0.1, 0.3]).rename(["B8", "B4", "B3"])
    result = add_indices(image)

    assert {"NDVI", "NDWI"}.issubset(result.bandNames().getInfo())
