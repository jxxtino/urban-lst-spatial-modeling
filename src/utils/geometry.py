import ee

def create_square_region(lat: float,
                         lon: float,
                         size_meters: float = 120
                         ) -> ee.Geometry:

    utm_zone = min(60, int((lon + 180) // 6) + 1)
    epsg = (32600 if lat >= 0 else 32700) + utm_zone
    projection = ee.Projection(f"EPSG:{epsg}")

    point = ee.Geometry.Point([lon, lat])
    point_utm = point.transform(projection, 0.01)

    coordinates = point_utm.coordinates()

    x = ee.Number(coordinates.get(0))
    y = ee.Number(coordinates.get(1))

    half_size = size_meters / 2

    return ee.Geometry.Rectangle(
        coords=[x.subtract(half_size),
                y.subtract(half_size),
                x.add(half_size),
                y.add(half_size)
                ],
        proj=projection,
        geodesic=False
    )
