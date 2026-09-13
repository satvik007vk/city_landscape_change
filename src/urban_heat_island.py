import ee
import geemap
import numpy as np

from src.ndvi_ndwi import add_indices
from src.preprocess.load_and_preprocess_image import (
    get_one_year_composite,
    get_one_year_lst_composite,
)


def compute_suhi_trend(
    aoi: ee.Geometry,
    start_year: int,
    end_year: int,
    source: str = "landsat",
    ring_width_meters: int = 5000,
) -> dict[str, list]:
    """source: "landsat" or "modis"."""
    outer_boundary = aoi.buffer(ring_width_meters)
    rural_ring = outer_boundary.difference(aoi)
    years = list(range(start_year, end_year + 1))
    urban_means, rural_means, suhi_values = [], [], []

    for year in years:
        lst_image = get_one_year_lst_composite(
            outer_boundary, year, start_month=6, end_month=8, source=source
        ).select("LST")

        urban_mean = (
            lst_image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=aoi,
                scale=30,
                bestEffort=True,
                maxPixels=1e9,
            )
            .get("LST")
            .getInfo()
        )
        rural_mean = (
            lst_image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=rural_ring,
                scale=30,
                bestEffort=True,
                maxPixels=1e9,
            )
            .get("LST")
            .getInfo()
        )

        urban_means.append(urban_mean)
        rural_means.append(rural_mean)
        suhi_values.append(urban_mean - rural_mean)

    return {
        "years": years,
        "urban_lst": urban_means,
        "rural_lst": rural_means,
        "suhi_intensity": suhi_values,
        "ring_width_meters": ring_width_meters,
    }


def compute_lst_index_correlation(
    aoi: ee.Geometry,
    year: int,
    index: str,
    source: str = "landsat",
    scale: int = 30,
) -> dict:
    """source: "landsat" or "modis"."""
    composite = add_indices(
        get_one_year_composite(aoi, year, start_month=6, end_month=8)
    )
    lst_image = get_one_year_lst_composite(
        aoi, year, start_month=6, end_month=8, source=source
    )
    combined = composite.select(index).addBands(lst_image.select("LST"))
    array = geemap.ee_to_numpy(combined, region=aoi, bands=[index, "LST"], scale=scale)

    index_values = array[:, :, 0].flatten()
    lst_values = array[:, :, 1].flatten()

    # 0 = no-data fill for both bands (same convention used elsewhere in this project)
    valid = (index_values != 0) & (lst_values != 0)
    index_values = index_values[valid]
    lst_values = lst_values[valid]

    correlation = float(np.corrcoef(index_values, lst_values)[0, 1])

    return {
        "index": index,
        "year": year,
        "index_values": index_values,
        "lst_values": lst_values,
        "correlation": correlation,
    }
