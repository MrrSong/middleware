from geopy import Point
from los.link_list import ListNode, LinkList
from los.tool import (
    GPSPoint,
    NavigationData,
    BoatData,
    PathPoint,
    TaskPath,
    InsData,
    NavigationInfo,
    SinglePathInfo,
    NavigationControl,
    to_kn,
    to_mps,
    calculate_angle_error_180
)
from los.los_controller import LOSController


def main():
    los = LOSController()
    los.tick()


if __name__ == "__main__":
    main()
