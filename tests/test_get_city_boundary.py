import pytest

from src.get_city_boundaries import City, get_city_boundary


@pytest.mark.vcr()
def test_get_city_boundary_paris():
    city = City(name="Paris", aoi="2.20,48.80,2.48,48.92", level=8)
    result = get_city_boundary(city, time="2026-06-01T00:00:00Z")

    assert result.crs == "EPSG:4326"
    assert len(result) > 0
    assert result["admin_level"].eq("8").all()
