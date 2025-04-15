from geopy import Point
from geopy.distance import geodesic
from message.boat_struct import RectangularTaskArea, GPSPoint


class GeoConverter:
    def __init__(self, task_area):
        """初始化矩形任务区域，设置左上角和左下角为原点。"""
        self.top_left_origin: Point = Point(task_area.top_latitude, task_area.bottom_longitude)
        self.bottom_left_origin: Point = Point(task_area.bottom_latitude, task_area.bottom_longitude)

    def meters_to_latlon_scatter(self, x_m: float, y_m: float) -> Point:
        """
        将物理距离 (x_m, y_m) 转换为经纬度坐标，以左上角为原点。
        x_m: 东向距离（米，正为东，负为西）
        y_m: 南向距离（米，正为南，负为北）
        返回: Point(latitude, longitude)
        """
        # 步骤 1：沿东/西方向移动 x_m 米
        x_bearing = 90.0 if x_m >= 0 else 270.0  # 东: 90°, 西: 270°
        x_distance_km = abs(x_m) / 1000.0  # 转换为千米，geodesic 要求千米单位
        intermediate_point = geodesic(kilometers=x_distance_km).destination(self.top_left_origin, bearing=x_bearing)

        # 步骤 2：从中间点沿南/北方向移动 y_m 米
        y_bearing = 180.0 if y_m >= 0 else 0.0  # 南: 180°, 北: 0°
        y_distance_km = abs(y_m) / 1000.0  # 转换为千米
        final_point = geodesic(kilometers=y_distance_km).destination(intermediate_point, bearing=y_bearing)

        return final_point

    def meters_to_latlon_scatter_list(self, coord_list):
        """
        重载版本，支持列表输入。
        coord_list: 包含多个 (x_m, y_m) 坐标对的列表
        返回: 对应的 GPSPoint 对象列表
        """
        geopy_points = [self.meters_to_latlon_scatter(x_m, y_m) for x_m, y_m in coord_list]
        return [Point(latitude=point.latitude, longitude=point.longitude) for point in geopy_points]

    def meters_to_latlon_continuous(self, x_m: float, y_m: float) -> Point:
        """
        将物理距离 (x_m, y_m) 转换为经纬度坐标，以左下角为原点。
        x_m: 东向距离（米，正为东，负为西）
        y_m: 北向距离（米，正为北，负为南）
        返回: Point(latitude, longitude)
        """
        # 步骤 1：沿东/西方向移动 x_m 米
        x_bearing = 90.0 if x_m >= 0 else 270.0  # 东: 90°, 西: 270°
        x_distance_km = abs(x_m) / 1000.0  # 转换为千米，geodesic 要求千米单位
        intermediate_point = geodesic(kilometers=x_distance_km).destination(self.bottom_left_origin, bearing=x_bearing)

        # 步骤 2：从中间点沿北/南方向移动 y_m 米
        y_bearing = 0.0 if y_m >= 0 else 180.0  # 北: 0°, 南: 180°
        y_distance_km = abs(y_m) / 1000.0  # 转换为千米
        final_point = geodesic(kilometers=y_distance_km).destination(intermediate_point, bearing=y_bearing)

        return final_point

    def latlon_to_meters_scatter(self, target: Point) -> tuple[float, float]:
        """
        将经纬度坐标转换为以左上角为原点的物理距离 (x_m, y_m)。
        target: 目标点经纬度
        返回: (x_m, y_m)（米，东向正为东，南向正为南）
        """
        # 步骤 1：计算东/西距离 x_m（沿原点纬度移动）
        intermediate_point = Point(self.top_left_origin.latitude, target.longitude)
        x_distance_km = geodesic(self.top_left_origin, intermediate_point).kilometers
        x_m = x_distance_km * 1000.0
        # 确定 x_m 方向（东正，西负）
        x_m = x_m if target.longitude >= self.top_left_origin.longitude else -x_m

        # 步骤 2：计算南/北距离 y_m（沿目标经度移动）
        y_distance_km = geodesic(intermediate_point, target).kilometers
        y_m = y_distance_km * 1000.0
        # 确定 y_m 方向（南正，北负）
        y_m = y_m if target.latitude <= intermediate_point.latitude else -y_m

        return x_m, y_m

    def latlon_to_meters_continuous(self, target: Point) -> tuple[float, float]:
        """
        将经纬度坐标转换为以左下角为原点的物理距离 (x_m, y_m)。
        target: 目标点经纬度
        返回: (x_m, y_m)（米，东向正为东，北向正为北）
        """
        # 步骤 1：计算东/西距离 x_m（沿原点纬度移动）
        intermediate_point = Point(self.bottom_left_origin.latitude, target.longitude)
        x_distance_km = geodesic(self.bottom_left_origin, intermediate_point).kilometers
        x_m = x_distance_km * 1000.0
        # 确定 x_m 方向（东正，西负）
        x_m = x_m if target.longitude >= self.bottom_left_origin.longitude else -x_m

        # 步骤 2：计算北/南距离 y_m（沿目标经度移动）
        y_distance_km = geodesic(intermediate_point, target).kilometers
        y_m = y_distance_km * 1000.0
        # 确定 y_m 方向（北正，南负）
        y_m = y_m if target.latitude >= intermediate_point.latitude else -y_m

        return x_m, y_m


def main():
    task_area = RectangularTaskArea()
    converter = GeoConverter(task_area)
    x_m, y_m = 2000, 2000

    # 正向转换：左上角原点
    top_left_result = converter.meters_to_latlon_scatter(x_m, y_m)
    print(f"左上角原点：物理坐标 ({x_m}m 东, {y_m}m 南) -> 经纬度: "
          f"({top_left_result.latitude:.6f}, {top_left_result.longitude:.6f})")

    # 反向转换：左上角原点
    top_left_meters = converter.latlon_to_meters_scatter(top_left_result)
    print(f"左上角原点：经纬度 ({top_left_result.latitude:.6f}, {top_left_result.longitude:.6f}) "
          f"-> 物理坐标: ({top_left_meters[0]:.2f}m 东, {top_left_meters[1]:.2f}m 南)")

    # 正向转换：左下角原点
    bottom_left_result = converter.meters_to_latlon_continuous(x_m, y_m)
    print(f"左下角原点：物理坐标 ({x_m}m 东, {y_m}m 北) -> 经纬度: "
          f"({bottom_left_result.latitude:.6f}, {bottom_left_result.longitude:.6f})")

    # 反向转换：左下角原点
    bottom_left_meters = converter.latlon_to_meters_continuous(bottom_left_result)
    print(f"左下角原点：经纬度 ({bottom_left_result.latitude:.6f}, {bottom_left_result.longitude:.6f}) "
          f"-> 物理坐标: ({bottom_left_meters[0]:.2f}m 东, {bottom_left_meters[1]:.2f}m 北)")


# 示例使用
if __name__ == "__main__":
    main()
