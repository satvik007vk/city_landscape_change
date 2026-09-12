import ee

from src.ndvi_ndwi import add_indices
from src.preprocess.aoi import load_city_aoi
from src.preprocess.gee_auth import initialize_ee
from src.preprocess.get_city_boundaries import Cities

CLOUD_PROB_THRESHOLD = 20  # MSK_CLDPRB units: percent (0-100)
S2_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"  # 5 day revisit, 10-60m resolution

LANDSAT_COLLECTION = "LANDSAT/LC08/C02/T1_L2"  # Landsat 8, Collection 2 Level 2
LST_CLOUD_BIT = 1 << 3
LST_SHADOW_BIT = 1 << 4

MODIS_LST_COLLECTION = "MODIS/061/MOD11A2"  # 8-day composite, 1km, no scene seams
MODIS_LST_SCALE = 0.02  # official DN -> Kelvin scale factor

START_YEAR = 2018  # Global L2A coverage in this collection starts in 2018
END_YEAR = 2025


def combine_yearly_composites(
    aoi: ee.Geometry, start_year: int = START_YEAR, end_year: int = END_YEAR
) -> ee.ImageCollection:
    images = [
        get_one_year_composite(aoi, year) for year in range(start_year, end_year + 1)
    ]
    return ee.ImageCollection(images)


def get_one_year_composite(
    aoi: ee.Geometry,
    year: int,
    start_month: int = 1,
    end_month: int = 12,
) -> ee.Image:
    start = ee.Date.fromYMD(year, start_month, 1)
    end = ee.Date.fromYMD(year, end_month, 1).advance(1, "month")
    collection = (
        ee.ImageCollection(S2_COLLECTION).filterBounds(aoi).filterDate(start, end)
    )
    band_order = collection.first().bandNames()
    masked = collection.map(mask_s2_clouds).map(lambda image: image.select(band_order))
    return masked.median().clip(aoi).set("year", year, "image_count", collection.size())


def mask_s2_clouds(image: ee.Image) -> ee.Image:
    clear_mask = image.select("MSK_CLDPRB").lt(CLOUD_PROB_THRESHOLD)
    optical_bands = image.select("B.*").divide(10000)
    return image.addBands(optical_bands, overwrite=True).updateMask(clear_mask)


def get_one_year_lst_composite(
    aoi: ee.Geometry,
    year: int,
    start_month: int = 1,
    end_month: int = 12,
    source: str = "landsat",
) -> ee.Image:
    """source: "landsat" or "modis"."""
    if source == "landsat":
        return _get_one_year_lst_composite_landsat(aoi, year, start_month, end_month)
    if source == "modis":
        return _get_one_year_lst_composite_modis(aoi, year, start_month, end_month)
    raise ValueError(f"Unknown LST source: {source!r}. Choose 'landsat' or 'modis'.")


def _get_one_year_lst_composite_landsat(
    aoi: ee.Geometry, year: int, start_month: int, end_month: int
) -> ee.Image:
    start = ee.Date.fromYMD(year, start_month, 1)
    end = ee.Date.fromYMD(year, end_month, 1).advance(1, "month")
    collection = (
        ee.ImageCollection(LANDSAT_COLLECTION).filterBounds(aoi).filterDate(start, end)
    )
    masked = collection.map(mask_landsat_clouds)
    return masked.median().clip(aoi).set("year", year, "image_count", collection.size())


def mask_landsat_clouds(image: ee.Image) -> ee.Image:
    qa = image.select("QA_PIXEL")
    clear_mask = (
        qa.bitwiseAnd(LST_CLOUD_BIT).eq(0).And(qa.bitwiseAnd(LST_SHADOW_BIT).eq(0))
    )
    lst_celsius = (
        image.select("ST_B10")
        .multiply(0.00341802)  # DN -> Kelvin scale factor (Landsat C2 L2 spec)
        .add(149.0)  # DN -> Kelvin offset (Landsat C2 L2 spec)
        .subtract(273.15)  # Kelvin -> Celsius
        .rename("LST")
    )
    return lst_celsius.updateMask(clear_mask)


def _get_one_year_lst_composite_modis(
    aoi: ee.Geometry, year: int, start_month: int, end_month: int
) -> ee.Image:
    start = ee.Date.fromYMD(year, start_month, 1)
    end = ee.Date.fromYMD(year, end_month, 1).advance(1, "month")
    collection = (
        ee.ImageCollection(MODIS_LST_COLLECTION)
        .filterBounds(aoi)
        .filterDate(start, end)
    )
    masked = collection.map(scale_modis_lst)
    return masked.median().clip(aoi).set("year", year, "image_count", collection.size())


def scale_modis_lst(image: ee.Image) -> ee.Image:
    raw = image.select("LST_Day_1km")
    lst_celsius = raw.multiply(MODIS_LST_SCALE).subtract(273.15).rename("LST")
    return lst_celsius.updateMask(raw.gt(0))  # MOD11A2 fill value is 0


if __name__ == "__main__":
    initialize_ee()
    aoi = load_city_aoi(Cities.PARIS.value.name)
    composites = combine_yearly_composites(aoi)
    composites_with_indices = composites.map(add_indices)

    for year in range(START_YEAR, END_YEAR + 1):
        img = ee.Image(composites.filter(ee.Filter.eq("year", year)).first())
        info = img.get("image_count").getInfo()
        print(f"{year}: {info} raw S2 images before cloud masking")

    first = ee.Image(composites_with_indices.first())
    print("Bands:", first.bandNames().getInfo())
