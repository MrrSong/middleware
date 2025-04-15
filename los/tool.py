from los.link_list import ListNode, LinkList
from dataclasses import dataclass
from geopy import Point


def to_mps(x: float) -> float:
    """
    速度由 kn 转化为 m/s
    :param x: 速度 kn
    :return: 速度 m/s
    """
    return x * 0.5144


def to_kn(x: float) -> float:
    """
    速度由 m/s 转化为 kn
    :param x: 速度 m/s
    :return: 速度 kn
    """
    return x * 1.9438


def calculate_angle_error_180(angle1: float, angle2: float) -> float:
    """
    计算两个角度之间的误差，并将误差值调整到 -180 度到 180 度的范围内。

    :param angle1: 当前角度，单位为度。
    :param angle2: 前一个角度，单位为度。
    :return: 调整后的角度误差，范围在 -180 度到 180 度之间。
    """
    # 计算当前角度与前一个角度的差值
    angle_error = angle1 - angle2

    # 如果角度误差大于 180 度，将其减去 360 度以调整到 -180 度到 180 度的范围
    if angle_error > 180.0:
        angle_error -= 360
    # 如果角度误差小于 -180 度，将其加上 360 度以调整到 -180 度到 180 度的范围
    if angle_error < -180.0:
        angle_error += 360

    return angle_error


@dataclass
class GPSPoint:
    fLongitude: float  # 经度
    fLatitude: float  # 纬度
    sHeight: int  # 高度 [-5000 8000]米
    usVelocity: int  # 速度 [1 50]节
    flag: int


@dataclass
class NavigationData:
    fFromPoint: Point = Point()  # 上一航点
    fDestPoint: Point = Point()  # 下一航点（目标航点）
    fTrackLineAngle: float = 0   # 上一航点到下一航点的角度（以正北方向为基准）
    fTrackLineDist: float = 0    # 上一航点到下一航点的距离


@dataclass
class BoatData:
    stGpsMyBoat: Point = Point  # 无人艇位置
    fCurBoatSpeed: float = 0    # 无人艇当前航速m/s
    fCurBoatYaw: float = 0      # 无人艇当前艏向
    fPreBoatYaw: float = 0      # 前一时刻艏向角
    fToDestAngle: float = 0     # 无人艇当前位置到目标航点的角度（以正北方向为基准）
    fToDestDist: float = 0      # 无人艇当前位置到目标航点的距离
    fLatDist: float = 0         # 无人艇离航迹线的侧偏距
    fAngErr: float = 0          # 表示当前点到目标点直线与起始点到目标点直线的夹角，区别fYawErr
    fLatDist_I: float = 0       # 侧偏距离积分
    fPreLatDist: float = 0      # 前一时刻侧偏距离
    fYawErr: float = 0          # 无人艇艏向角偏差
    fYawRate: float = 0
    fCourse: float = 0          # 无人艇航向


@dataclass
class PathPoint:
    fLongitude: float    # 经度
    fLatitude: float     # 维度
    fSpeedK: float       # 单位：节
    fRadius: float       # 曲线环绕半径 单位：米 (为0表示非曲线路径)
    fAzimuth: float      # 曲线路径切入点，相当于曲线起点位置
    fTurns: float        # 曲线环绕圈数，可为小数
    ucSurroundDire: int  # 环绕方向 1-顺时针 2-逆时针


@dataclass
class TaskPath:
    roadId: int = 0               # 航路id
    state: int = 0                # 编队航行状态，0无效，1开始，2完成
    end_flag: int = 0             # 所有航点完成结束标志 0-已完成 1-未完成
    PathPointNum: int = 0         # 航线航点数
    path: LinkList = None

    def __post_init__(self):
        if self.path is None:
            self.path = LinkList()


@dataclass
class InsData:
    fPoint: Point = Point()    # 经纬度点
    fHeight: float = 0         # 高度：米
    fHeading: float = 0        # 艏向角：[0,360]度
    fHeadingRate: float = 0    # 艏向角速度，度/秒
    fPitch: float = 0          # 俯仰角：度
    fPitchRate: float = 0      # 俯仰角速度：度/秒
    fRoll: float = 0           # 横滚角：度
    fRollRate: float = 0       # 横滚角速度
    fHeave: float = 0          # 升沉，m
    fSpeedM: float = 0         # 速度：m/s
    fSpeedK: float = 0         # 速度：节
    fCourse: float = 0         # 航向角：[0,360]度
    fCourseRate: float = 0     # 航向角速度：度/秒
    flag: int = 0


@dataclass
class NavigationInfo:
    tid: int = 0                     # 编号
    cLineTrackingType: int = 0       # 路径跟踪类型　１－直线　２－曲线
    fCurLineCompRate: float = 0      # 当前航段完成率　％　０～１００
    fLatDistToMiddleWare: float = 0  # 计算发送至中间件的侧偏距　左侧为负，右侧为正
    fToDestDist: float = 0           # 相对当前终点距离 米
    fToDestAngle: float = 0          # 相对当前终点角度 度
    fLineAngle: float = 0            # 航线角度 度
    fLineDist: float = 0             # 航线长度
    fLatDist: float = 0              # 侧偏距 米　直线：左正右负　　曲线：外正内负
    fToCenterDist: float = 0         # 曲线跟随时保存的是无人艇到圆心的距离
    fToCurveStartAngle: float = 0    # 相对曲线起点角度
    fToCurveDestAngle: float = 0     # 相对曲线终点角度
    fToCurveDestDist: float = 0      # 相对曲线终点的曲线距离


@dataclass
class SinglePathInfo:
    usCurTaskNum: int = 0                # 当前任务序号 从1开始
    ucLineType: int = 1                  # 1-直线 2-曲线
    fFirstPoint: Point = Point()         # 直线时起点经纬度
    fSecondPoint: Point = Point()        # 直线时终点经纬度
    fSpeedK: float = 0                   # 单位：节
    fRadius: float = 0                   # 曲线环绕半径 单位：米 (为0表示非曲线路径)
    fAzimuth: float = 0                  # 曲线路径切入点角度，相当于曲线起点位置
    fTurns: float = 0                    # 曲线环绕圈数，可为小数
    ucSurroundDire: int = 0              # 环绕方向 1-顺时针 2-逆时针


@dataclass
class NavigationControl:
    flag: int = 0           # flag = 0 不启用N - A策略的输出 保持当前航向和速度; flag = 1 启用N - A策略的输出 改变当前的速度和航向
    fTurnAngle: float = 0   # 导航避障的输出角度，绝对角度，相对于正北方向，0到360度
    fForwardVel: float = 0  # 前进速度，单位：m/s
