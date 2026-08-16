from pathlib import Path
from dotenv import dotenv_values
import requests
import geopandas as gpd
from shapely import from_wkb
import io, pyarrow.parquet as pq
from dataclasses import dataclass
from enum import Enum

ROOT_DIR = Path(__file__).parent.parent
config = dotenv_values(ROOT_DIR/".env")
KEY = config["OHSOME_API_KEY"]
OHSOME_V2_URL = config["OHSOME_V2_URL"]

@dataclass(frozen=True)
class City:
    name: str
    aoi: str
    level: int

class Cities(Enum):
    KARLSRUHE = City("Karlsruhe", "8.27,48.93,8.56,49.10", level=8)
    BERLIN    = City("Berlin",    "13.05,52.32,13.80,52.70", level=4)
    PARIS     = City("Paris",     "2.20,48.80,2.48,48.92",  level=8)

def get_city_boundary(city: City,  time="2026-06-01T00:00:00Z", save_file: bool = False) -> gpd.GeoDataFrame:

    filter = f"type:relation and boundary=administrative and name={city.name}"
    if city.level:
        filter += f" and admin_level={city.level}"


    r = requests.get(
        url=f"{OHSOME_V2_URL}/extraction/features.parquet",
        headers={"authorization": KEY,"accept": "*/*"},
        params={"filter": filter, "aoi": city.aoi, "clip": "false", "time": time},
        timeout=120,
        )
    r.raise_for_status()
    df = pq.read_table(io.BytesIO(r.content)).to_pandas()
    city_boundary = gpd.GeoDataFrame(df, geometry=from_wkb(df["geom"]), crs="EPSG:4326")
    city_boundary["tags"] = df["osm_tags"].apply(dict)
    city_boundary["admin_level"] = city_boundary["tags"].apply(lambda t: t.get("admin_level"))

    if save_file:
        city_boundary.to_file(filename=(ROOT_DIR / f'data/{city.name}_boundary.geojson'), driver='GEOJSON')

    return city_boundary



if __name__ == "__main__":
    for city in Cities:
        city_boundary_gdf = get_city_boundary(city=city.value, save_file=False)
        print(city.value.name, len(city_boundary_gdf))

