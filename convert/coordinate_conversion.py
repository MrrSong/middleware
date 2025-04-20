from typing import List, Tuple
from geopy import Point
from geopy.distance import geodesic
class RectangularTaskArea:
    bottom_longitude: float = 122.745196
    bottom_latitude: float = 30.796787
    top_longitude: float = 122.766097
    top_latitude: float = 30.814828


class GeoConverter:
    def __init__(self, task_area):
        """
        初始化矩形任务区域，设置左上角和左下角为原点。

        :param task_area: 矩形任务区域对象
        """
        self.top_left_origin: Point = Point(task_area.top_latitude, task_area.bottom_longitude)
        self.bottom_left_origin: Point = Point(task_area.bottom_latitude, task_area.bottom_longitude)

    def meters_to_latlon_scatter(self, x_m: float, y_m: float) -> Point:
        """
        将物理距离 (x_m, y_m) 转换为经纬度坐标，以左上角为原点。

        :param x_m: 东向距离（米，正为东，负为西）
        :param y_m: 南向距离（米，正为南，负为北）
        :return: 经纬度坐标点对象
        """
        x_bearing = 90.0 if x_m >= 0 else 270.0
        x_distance_km = abs(x_m) / 1000.0
        intermediate_point = geodesic(kilometers=x_distance_km).destination(self.top_left_origin, bearing=x_bearing)

        y_bearing = 180.0 if y_m >= 0 else 0.0
        y_distance_km = abs(y_m) / 1000.0
        final_point = geodesic(kilometers=y_distance_km).destination(intermediate_point, bearing=y_bearing)

        return final_point

    def meters_to_latlon_scatter_list(self, coord_list: List[Tuple[float, float]]) -> List[Point]:
        """
        重载版本，支持列表输入，以左上角为原点。

        :param coord_list: 包含多个 (x_m, y_m) 坐标对的列表
        :return: 对应的经纬度坐标点对象列表
        """
        return [self.meters_to_latlon_scatter(x_m, y_m) for x_m, y_m in coord_list]

    def meters_to_latlon_continuous(self, x_m: float, y_m: float) -> Point:
        """
        将物理距离 (x_m, y_m) 转换为经纬度坐标，以左下角为原点。

        :param x_m: 东向距离（米，正为东，负为西）
        :param y_m: 北向距离（米，正为北，负为南）
        :return: 经纬度坐标点对象
        """
        x_bearing = 90.0 if x_m >= 0 else 270.0
        x_distance_km = abs(x_m) / 1000.0
        intermediate_point = geodesic(kilometers=x_distance_km).destination(self.bottom_left_origin, bearing=x_bearing)

        y_bearing = 0.0 if y_m >= 0 else 180.0
        y_distance_km = abs(y_m) / 1000.0
        final_point = geodesic(kilometers=y_distance_km).destination(intermediate_point, bearing=y_bearing)

        return final_point

    def meters_to_latlon_continuous_list(self, coord_list: List[Tuple[float, float]]) -> List[Point]:
        """
        重载版本，支持列表输入，以左下角为原点。

        :param coord_list: 包含多个 (x_m, y_m) 坐标对的列表
        :return: 对应的经纬度坐标点对象列表
        """
        return [self.meters_to_latlon_continuous(x_m, y_m) for x_m, y_m in coord_list]

    def latlon_to_meters_scatter(self, target: Point) -> Tuple[float, float]:
        """
        将经纬度坐标转换为以左上角为原点的物理距离 (x_m, y_m)。

        :param target: 目标点经纬度
        :return: (x_m, y_m)（米，东向正为东，南向正为南）
        """
        intermediate_point = Point(self.top_left_origin.latitude, target.longitude)
        x_distance_km = geodesic(self.top_left_origin, intermediate_point).kilometers
        x_m = x_distance_km * 1000.0
        x_m = x_m if target.longitude >= self.top_left_origin.longitude else -x_m

        y_distance_km = geodesic(intermediate_point, target).kilometers
        y_m = y_distance_km * 1000.0
        y_m = y_m if target.latitude <= intermediate_point.latitude else -y_m

        return x_m, y_m

    def latlon_to_meters_scatter_list(self, target_list: List[Point]) -> List[Tuple[float, float]]:
        """
        重载版本，支持列表输入，以左上角为原点。

        :param target_list: 目标点经纬度列表
        :return: 对应的物理距离 (x_m, y_m) 列表
        """
        return [self.latlon_to_meters_scatter(target) for target in target_list]

    def latlon_to_meters_continuous(self, target: Point) -> Tuple[float, float]:
        """
        将经纬度坐标转换为以左下角为原点的物理距离 (x_m, y_m)。

        :param target: 目标点经纬度
        :return: (x_m, y_m)（米，东向正为东，北向正为北）
        """
        intermediate_point = Point(self.bottom_left_origin.latitude, target.longitude)
        x_distance_km = geodesic(self.bottom_left_origin, intermediate_point).kilometers
        x_m = x_distance_km * 1000.0
        x_m = x_m if target.longitude >= self.bottom_left_origin.longitude else -x_m

        y_distance_km = geodesic(intermediate_point, target).kilometers
        y_m = y_distance_km * 1000.0
        y_m = y_m if target.latitude >= intermediate_point.latitude else -y_m

        return x_m, y_m

    def latlon_to_meters_continuous_list(self, target_list: List[Point]) -> List[Tuple[float, float]]:
        """
        重载版本，支持列表输入，以左下角为原点。

        :param target_list: 目标点经纬度列表
        :return: 对应的物理距离 (x_m, y_m) 列表
        """
        return [self.latlon_to_meters_continuous(target) for target in target_list]


def main():
    task_area = RectangularTaskArea()
    converter = GeoConverter(task_area)

    # 测试以左上角为原点的米坐标转经纬度坐标（列表输入）
    meters_coord_list_top_left = [(0, 0), (0, 2000)]
    top_left_result_list = converter.meters_to_latlon_scatter_list(meters_coord_list_top_left)
    for i, result in enumerate(top_left_result_list):
        print(f"左上角原点：物理坐标 ({meters_coord_list_top_left[i][0]}m 东, {meters_coord_list_top_left[i][1]}m 南) -> 经纬度: "
              f"({result.latitude:.6f}, {result.longitude:.6f})")

    # 测试以左下角为原点的米坐标转经纬度坐标（列表输入）
    meters_coord_list_bottom_left = [(0, 0), (0, 2000)]
    bottom_left_result_list = converter.meters_to_latlon_continuous_list(meters_coord_list_bottom_left)
    for i, result in enumerate(bottom_left_result_list):
        print(f"左下角原点：物理坐标 ({meters_coord_list_bottom_left[i][0]}m 东, {meters_coord_list_bottom_left[i][1]}m 北) -> 经纬度: "
              f"({result.latitude:.6f}, {result.longitude:.6f})")

    # 测试以左上角为原点的经纬度坐标转米坐标（列表输入）
    latlon_points_top_left = [Point(30.796787, 122.745196), Point(30.814828, 122.745196)]
    top_left_meters_list = converter.latlon_to_meters_scatter_list(latlon_points_top_left)
    for i, (x_m, y_m) in enumerate(top_left_meters_list):
        print(f"左上角原点：经纬度 ({latlon_points_top_left[i].latitude:.6f}, {latlon_points_top_left[i].longitude:.6f}) -> 物理坐标: "
              f"({x_m:.2f}m 东, {y_m:.2f}m 南)")

    # 测试以左下角为原点的经纬度坐标转米坐标（列表输入）
    latlon_points_bottom_left = [Point(30.796787, 122.745196), Point(30.814828, 122.745196)]
    bottom_left_meters_list = converter.latlon_to_meters_continuous_list(latlon_points_bottom_left)
    for i, (x_m, y_m) in enumerate(bottom_left_meters_list):
        print(f"左下角原点：经纬度 ({latlon_points_bottom_left[i].latitude:.6f}, {latlon_points_bottom_left[i].longitude:.6f}) -> 物理坐标: "
              f"({x_m:.2f}m 东, {y_m:.2f}m 北)")


if __name__ == "__main__":
    main()