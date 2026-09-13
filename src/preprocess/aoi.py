from pathlib import Path

import ee
import geemap
import geopandas as gpd
import numpy as np
from shapely.geometry import mapping

from src.preprocess.gee_auth import initialize_ee
from src.preprocess.get_city_boundaries import Cities

ROOT_DIR = Path(__file__).parent.parent.parent


def load_city_aoi(city_name: str) -> ee.Geometry:
    gdf = gpd.read_file(ROOT_DIR / f"data/{city_name}_boundary.geojson")
    geom = gdf.union_all()
    return ee.Geometry(mapping(geom))


def get_true_color_array(
    city_name: str,
    buffer_meters: int = 5000,
    year: int = 2025,
    start_month: int = 6,
    end_month: int = 8,
    scale: int = 30,
) -> tuple[np.ndarray, list[float]]:
    from src.preprocess.load_and_preprocess_image import get_one_year_composite

    city_aoi = load_city_aoi(city_name)
    buffered_aoi = city_aoi.buffer(buffer_meters)
    composite = get_one_year_composite(
        buffered_aoi, year, start_month=start_month, end_month=end_month
    )
    rgb_array = geemap.ee_to_numpy(
        composite, region=buffered_aoi, bands=["B4", "B3", "B2"], scale=scale
    )
    rgb_array = np.clip(rgb_array * 3.5, 0, 1)

    bounds = buffered_aoi.bounds().getInfo()["coordinates"][0]
    lons = [pt[0] for pt in bounds]
    lats = [pt[1] for pt in bounds]
    extent = [min(lons), max(lons), min(lats), max(lats)]
    return rgb_array, extent


def get_city_boundary_rings(city_name: str) -> list[list[tuple[float, float]]]:
    city_aoi = load_city_aoi(city_name)
    geojson = city_aoi.getInfo()
    polygons = (
        [geojson["coordinates"]]
        if geojson["type"] == "Polygon"
        else geojson["coordinates"]
    )
    return [[(pt[0], pt[1]) for pt in polygon[0]] for polygon in polygons]


if __name__ == "__main__":
    initialize_ee()
    aoi = load_city_aoi(Cities.PARIS.value.name)
    print("AOI area (km^2):", aoi.area().getInfo() / 1e6)
