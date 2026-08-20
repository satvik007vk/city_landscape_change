from pathlib import Path

import ee
import geopandas as gpd
from shapely.geometry import mapping

from gee_auth import initialize_ee
from get_city_boundaries import Cities

ROOT_DIR = Path(__file__).parent.parent


def load_city_aoi(city_name: str) -> ee.Geometry:
    gdf = gpd.read_file(ROOT_DIR / f"data/{city_name}_boundary.geojson")
    geom = gdf.union_all()
    return ee.Geometry(mapping(geom))


if __name__ == "__main__":
    initialize_ee()
    aoi = load_city_aoi(Cities.PARIS.value.name)
    print("AOI area (km^2):", aoi.area().getInfo() / 1e6)
