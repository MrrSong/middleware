from dataclasses import dataclass, field
from typing import List
import threading


@dataclass
class Task:
    TASK_STOP: int = 0     # 任务结束
    TASK_START: int = 1    # 任务开始

    def task_start_str(self) -> str:
        params = [
            26,  # 固定值
            self.TASK_START
        ]
        return f"[{', '.join(map(str, params))}]"  # 转换为字符串并返回

    def task_end_str(self) -> str:
        params = [
            26,  # 固定值
            self.TASK_STOP
        ]
        return f"[{', '.join(map(str, params))}]"  # 转换为字符串并返回


@dataclass
class GPSPoint:
    longitude: float      # 经度
    latitude: float       # 纬度
    speed: float          # 到该航点的速度


@dataclass
class RectangularTaskArea:
    bottom_longitude: float = 122.745196
    bottom_latitude: float = 30.796787
    top_longitude: float = 122.766097
    top_latitude: float = 30.814828


@dataclass
class Visualization:
    VISUAL_FLAG: int = 0       # 可视化标志

    def visual_flag_str(self) -> str:
        params = [
            10,  # 固定值
            self.VISUAL_FLAG
        ]
        return f"[{', '.join(map(str, params))}]"  # 转换为字符串并返回


@dataclass
class UsvPosture:
    x_m: float = 0.0             # x m/s
    y_m: float = 0.0             # y m/s
    heading_degree: float = 0.0  # 艏向角 °

    def to_string(self) -> str:
        params = [
            11,  # 固定值
            self.x_m,
            self.y_m,
            self.heading_degree
        ]
        return f"[{', '.join(map(str, params))}]"  # 转换为字符串并返回


@dataclass
class MotionControl:
    usv_id: int = 0                                          # 艇全局编号
    task_type: int = 0                                       # 艇执行任务类型
    target_id: int = 0                                       # 执行任务类型相关的目标全局编号
    route_task_id: int = 0                                   # 航路 或者 任务编号
    reserved: int = 0                                        # 预留，置 0
    motion_control_mode: int = 0                             # 运动控制模式
    throttle_or_speed: float = 0.0                           # 油门 或 速度
    rudder_angle_or_heading: float = 0.0                     # 舵角 或 航向
    change_in_previous_frame: int = 0                        # 与上一帧 航点/速度 是否改变
    waypoints_count: int = 0                                 # 航点个数
    waypoints: List[GPSPoint] = field(default_factory=list)  # 使用 field 和 default_factory 初始化列表

    def __post_init__(self):
        # 初始化后可以进行额外检查或处理
        if self.motion_control_mode in [1, 4, 5]:
            # 航点模式下需要有航点信息
            assert self.waypoints_count == len(self.waypoints), "航点数量与提供的航点信息不匹配"

    def to_string(self) -> str:
        # 先把 MotionControl 实例的属性提取出来
        params = [
            22,  # 固定值
            self.usv_id,  # para1: 艇全局编号
            self.task_type,  # para2: 艇执行任务类型
            self.target_id,  # para3: 执行任务类型相关的目标全局编号
            self.route_task_id,  # para4: 航路任务编号
            self.reserved,  # para5: 预留 2，置 0
            self.motion_control_mode,  # para6: 运动控制模式
            self.throttle_or_speed,  # para7: 油门或速度值
            self.rudder_angle_or_heading,  # para8: 舵角值或航向值
            self.change_in_previous_frame,  # para9: 与上一帧下发航点/速度是否有改变
            self.waypoints_count  # para10: 航点个数
        ]

        # 对于航点信息，假设每个航点包含经纬度、速度或时间
        for i, waypoint in enumerate(self.waypoints, start=1):
            params.extend([
                waypoint.longitude, # para(n*3+8): 航点n 经度
                waypoint.latitude,  # para(n*3+9): 航点n 纬度
                waypoint.speed      # para(n*3+10): 航点n 到该航点的速度或时间
            ])

        # 拼接成字符串
        return f"[{', '.join(map(str, params))}]"


@dataclass
# 定义 BoatMessage 类
class BoatMessage:
    usv_id: int = 0                   # 艇全局编号
    longitude: float = 0.0               # 经度，单位: °, 保留小数点后8位
    latitude: float = 0.0                # 纬度，单位: °, 保留小数点后8位
    yaw_angle: float = 0.0               # 偏航角，单位: °, 范围: [-180, 180)
    yaw_velocity: float = 0.0            # 偏航角速度，单位: rad/s
    yaw_acceleration: float = 0.0        # 偏航角加速度，单位: rad/s^2
    pitch_angle: float = 0.0             # 俯仰角，单位: °
    roll_angle: float = 0.0              # 横滚角，单位: °
    forward_speed: float = 0.0           # 前向速度，单位: m/s
    forward_acceleration: float = 0.0    # 前向加速度，单位: m/s^2
    lateral_speed: float = 0.0           # 横向速度，单位: m/s
    lateral_acceleration: float = 0.0    # 横向加速度，单位: m/s^2
    heading_angle: float = 0.0           # 航向角，单位: °, 范围: [-180, 180)
    current_state: int = 0               # 当前状态，1: 正常, 0: 故障
    task_type: int = 0                   # 当前执行任务类型
    target_id: int = 0                   # 目标编号
    control_mode: int = 0                # 当前执行的运动控制模式 0: 无; 2: 舵角/油门控制; 3: 航向/速度控制;
    current_control_value: float = 0.0   # control_mode = 2 时为当前舵角值; control_mode = 3 时为3时为当前期望航向值;
    current_throttle: float = 0.0        # control_mode = 2 时为当前油门值; control_mode = 3 时为3时为当前期望速度值;
    health: float = 0.0                  # 生命值

    @staticmethod
    def from_packet(packet):
        return BoatMessage(
            usv_id=packet[0],
            longitude=packet[1],
            latitude=packet[2],
            yaw_angle=packet[3],
            yaw_velocity=packet[4],
            yaw_acceleration=packet[5],
            pitch_angle=packet[6],
            roll_angle=packet[7],
            forward_speed=packet[8],
            forward_acceleration=packet[9],
            lateral_speed=packet[10],
            lateral_acceleration=packet[11],
            heading_angle=packet[12],
            current_state=packet[13],
            task_type=packet[14],
            target_id=packet[15],
            control_mode=packet[16],
            current_control_value=packet[17],
            current_throttle=packet[18],
            health=packet[19]
        )

    def to_string(self) -> str:
        # 先把 BoatMessage 实例的属性提取出来
        params = [
            self.usv_id,
            self.longitude,
            self.latitude,
            self.yaw_angle,
            self.yaw_velocity,
            self.yaw_acceleration,
            self.pitch_angle,
            self.roll_angle,
            self.forward_speed,
            self.forward_acceleration,
            self.lateral_speed,
            self.lateral_acceleration,
            self.heading_angle,
            self.current_state,
            self.task_type,
            self.target_id,
            self.control_mode,
            self.current_control_value,
            self.current_throttle,
            self.health
        ]

        # 拼接成字符串
        return f"[{', '.join(map(str, params))}]"


@dataclass
# 定义 BoatMessage 类
class Mission:
    task: Task = Task()                                     # 任务启停
    task_area: RectangularTaskArea = RectangularTaskArea()  # 任务区域
    motion_control: MotionControl = MotionControl()         # 运动控制信息
    boat_message: BoatMessage = BoatMessage()               # 船只信息
    usv_posture: UsvPosture = UsvPosture()                  # 物理位置
    visual_flag: Visualization = Visualization()            # 可视化标志


class Singleton:
    _instance = None
    _lock = threading.Lock()
    _mission: Mission = None  # 单例管理的核心数据

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            raise Exception("MissionSingleton instance not created yet. Use create() method instead.")
        return cls._instance

    @classmethod
    def create(cls, motion_control: MotionControl = None, boat_message: BoatMessage = None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Singleton, cls).__new__(cls)
                # 初始化 Mission 实例
                cls._mission = Mission()
        return cls._instance

    @property
    def mission(self) -> Mission:
        """获取单例管理的 Mission 实例"""
        if self._mission is None:
            raise Exception("Mission instance not initialized yet.")
        return self._mission


# 使用示例
def main():
    # 创建单例实例并初始化 Mission
    singleton1 = Singleton.create()
    singleton2 = Singleton.create()

    # 检查单例行为
    print(singleton1 is singleton2)  # 输出: True

    # 获取单例管理的 Mission 实例
    mission = singleton1.mission
    print(mission.motion_control)  # 输出: motion_control 的信息
    print(mission.boat_message)    # 输出: boat_message 的信息


if __name__ == "__main__":
    main()
