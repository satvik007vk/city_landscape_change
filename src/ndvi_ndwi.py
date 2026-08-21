import ee


def add_ndvi(image: ee.Image) -> ee.Image:
    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
    return image.addBands(ndvi)


def add_ndwi(image: ee.Image) -> ee.Image:
    ndwi = image.normalizedDifference(["B3", "B8"]).rename("NDWI")
    return image.addBands(ndwi)


def add_indices(image: ee.Image) -> ee.Image:
    return add_ndwi(add_ndvi(image))
