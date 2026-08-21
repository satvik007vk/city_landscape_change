import ee

from aoi import load_city_aoi
from gee_auth import initialize_ee
from get_city_boundaries import Cities
from ndvi_ndwi import add_indices

CLOUD_PROB_THRESHOLD = 20  # MSK_CLDPRB units: percent (0-100)
S2_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"  # 5 day revisit, 10-60m resolution

START_YEAR = 2018  # Global L2A coverage in this collection starts in 2018
END_YEAR = 2025


def combine_yearly_composites(
    aoi: ee.Geometry, start_year: int = START_YEAR, end_year: int = END_YEAR
) -> ee.ImageCollection:
    images = [
        get_one_year_composite(aoi, year) for year in range(start_year, end_year + 1)
    ]
    return ee.ImageCollection(images)


def get_one_year_composite(aoi: ee.Geometry, year: int) -> ee.Image:
    start = ee.Date.fromYMD(year, 1, 1)
    end = start.advance(1, "year")
    collection = (
        ee.ImageCollection(S2_COLLECTION).filterBounds(aoi).filterDate(start, end)
    )
    masked = collection.map(mask_s2_clouds)
    return masked.median().clip(aoi).set("year", year, "image_count", collection.size())


def mask_s2_clouds(image: ee.Image) -> ee.Image:
    clear_mask = image.select("MSK_CLDPRB").lt(CLOUD_PROB_THRESHOLD)
    optical_bands = image.select("B.*").divide(10000)
    return image.addBands(optical_bands, overwrite=True).updateMask(clear_mask)


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
