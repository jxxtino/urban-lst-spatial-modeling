import ee

class Landsat9:

    COLLECTION = "LANDSAT/LC09/C02/T1_L2"

    @staticmethod
    def _preprocess(image: ee.Image) -> ee.Image:
        qa = image.select("QA_PIXEL")

        cloud_mask = qa.bitwiseAnd(0b111111).eq(0)

        saturation_mask = (image.select("QA_RADSAT").eq(0))
        valid_mask = cloud_mask.And(saturation_mask)

        reflectance = (image.select("SR_B.").multiply(0.0000275).add(-0.2))

        lst_kelvin = (image.select("ST_B10").multiply(0.00341802).add(149.0))
        lst_celsius = (lst_kelvin.subtract(273.15).rename("LST_C"))
        lst_uncertainty = (
            image.select("ST_QA")
            .multiply(0.01)
            .rename("LST_UNCERTAINTY_K")
        )

        return (
            image
            .addBands(reflectance, overwrite=True)
            .addBands(lst_kelvin, overwrite=True)
            .addBands(lst_celsius)
            .addBands(lst_uncertainty)
            .updateMask(valid_mask)
        )

    def get_candidate_scenes(
        self,
        region: ee.Geometry,
        start_date: str = "2025-01-01",
        end_date: str = "2026-01-01",
        max_scene_cloud: int = 20,
    ) -> ee.ImageCollection:
        collection = (
            ee.ImageCollection(self.COLLECTION)
            .filterBounds(region)
            .filterDate(start_date, end_date)
            .filter(ee.Filter.eq("PROCESSING_LEVEL", "L2SP"))
            .filter(ee.Filter.gte("CLOUD_COVER", 0))
            .filter(ee.Filter.lt("CLOUD_COVER", max_scene_cloud))
        )

        return collection.map(self._preprocess)
