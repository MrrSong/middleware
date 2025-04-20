from pyproj import Geod
import math


def calculate_azimuth(lon1, lat1, lon2, lat2):
    """
    Calculate azimuth (bearing) between two points in degrees.
    North = 0°, clockwise to 360°.

    Args:
        lon1, lat1: Longitude and latitude of first point (degrees)
        lon2, lat2: Longitude and latitude of second point (degrees)

    Returns:
        Azimuth in degrees (0-360)
    """
    geod = Geod(ellps='WGS84')
    azimuth, _, _ = geod.inv(lon1, lat1, lon2, lat2)

    # Normalize to 0-360 range, ensuring North = 0°, clockwise
    azimuth = (azimuth + 360) % 360
    return azimuth


# Test with provided coordinates
if __name__ == "__main__":
    point1_lon = 122.7464500716987
    point1_lat = 30.81392600035107
    point2_lon = 122.74665908364842
    point2_lat = 30.81392599596936

    result = calculate_azimuth(point1_lon, point1_lat, point2_lon, point2_lat)
    print(f"Azimuth from point1 to point2: {result:.2f}°")