import math
import geopy
from geopy import distance as geo_dist

def get_coordinates(start, end, distance_meters):
    """
    Calculates the new coordinates between two points depending
    of the specified distance and the calculated bearing.

    Parameters
    ----------
    start_point: tuple(latitude, longitude)
    end_point: tuple(latitude, longitude)
    distance_meters: float

    Returns
    -------
    point: geopy.Point
        A new point between the start and the end points.
    """

    start_point = geopy.Point(start[0], start[1])
    end_point = geopy.Point(end[0], end[1])

    bearing = get_bearing(start_point, end_point)

    distance_km = distance_meters / 1000
    d = geo_dist.distance(kilometers=distance_km)
    destination = d.destination(point=start_point, bearing=bearing)

    return (destination.latitude, destination.longitude) 

def get_bearing(start_point, end_point):
    """
    Calculates the bearing between two points.

    Parameters
    ----------
    start_point: geopy.Point
    end_point: geopy.Point

    Returns
    -------
    point: int
        Bearing in degrees between the start and end points.
    """
    start_lat = math.radians(start_point.latitude)
    start_lng = math.radians(start_point.longitude)
    end_lat = math.radians(end_point.latitude)
    end_lng = math.radians(end_point.longitude)

    d_lng = end_lng - start_lng
    if abs(d_lng) > math.pi:
        if d_lng > 0.0:
            d_lng = -(2.0 * math.pi - d_lng)
        else:
            d_lng = (2.0 * math.pi + d_lng)

    tan_start = math.tan(start_lat / 2.0 + math.pi / 4.0)
    tan_end = math.tan(end_lat / 2.0 + math.pi / 4.0)
    d_phi = math.log(tan_end / tan_start)
    bearing = (math.degrees(math.atan2(d_lng, d_phi)) + 360.0) % 360.0

    return bearing