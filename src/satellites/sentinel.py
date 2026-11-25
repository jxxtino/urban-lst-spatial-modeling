import ee

class Sentinel2:

    COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"

    @staticmethod
    def _preprocess(image: ee.Image) -> ee.Image:
        scl = image.select("SCL")

        valid_mask = (
            scl.neq(1)
            .And(scl.neq(3))
            .And(scl.neq(8))
            .And(scl.neq(9))
            .And(scl.neq(10))
            .And(scl.neq(11))
        )

        reflectance = (
            image.select(["B2", "B3", "B4", "B5","B8", "B8A", "B11", "B12"])
            .multiply(0.0001)
        )

        return (
            image
            .addBands(reflectance, overwrite=True)
            .updateMask(valid_mask)
        )

    @staticmethod
    def _add_spectral_indices(image: ee.Image) -> ee.Image:
        
        ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
        ndbi = image.normalizedDifference(["B11", "B8"]).rename("NDBI")
        ndwi = image.normalizedDifference(["B3", "B8"]).rename("NDWI")
        mndwi = image.normalizedDifference(["B3", "B11"]).rename("MNDWI")
        ndmi = image.normalizedDifference(["B8", "B11"]).rename("NDMI")

        bsi = image.expression(
            "((s + r) - (n + b)) / "
            "((s + r) + (n + b))",
            {
                "s": image.select("B11"),
                "r": image.select("B4"),
                "n": image.select("B8"),
                "b": image.select("B2"),
            }
        ).rename("BSI")

        savi = image.expression(
            "1.5 * (n - r) / (n + r + 0.5)",
            {
                "n": image.select("B8"),
                "r": image.select("B4"),
            }
        ).rename("SAVI")

        indices = ee.Image.cat([ndvi, ndbi, ndwi, mndwi, ndmi, bsi, savi])
        return image.addBands(indices)

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
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", max_scene_cloud))
        )

        return collection.map(self._preprocess).map(self._add_spectral_indices)
