import ee

from src.satellites.landsat import Landsat9
from src.satellites.sentinel import Sentinel2
from src.utils.geometry import create_square_region


def main() -> None:
    ee.Authenticate()
    ee.Initialize(project="projetointegrador-469501")

    region = create_square_region(lat=-23.9589, lon=-46.3327, size_meters=120)
    max_scene_cloud = 10

    sentinel_images = Sentinel2().get_candidate_scenes(
        region=region,
        max_scene_cloud=max_scene_cloud,
    )
    
    landsat_images = Landsat9().get_candidate_scenes(
        region=region,
        max_scene_cloud=max_scene_cloud,
    )

    print(f"Sentinel-2 candidate scenes: {sentinel_images.size().getInfo()}")
    print(f"Landsat 9 candidate scenes: {landsat_images.size().getInfo()}")


if __name__ == "__main__":
    main()
