import math
from geopy import Point
from geopy.distance import distance
from los.link_list import ListNode
from pyproj import Geod
from los.tool import (
    NavigationData,
    BoatData,
    TaskPath,
    InsData,
    NavigationInfo,
    SinglePathInfo,
    NavigationControl,
    to_kn,
    to_mps,
    calculate_angle_error_180
)
from log.log import logger
from message.boat_struct import BoatMessage


class LOSController:
    def __init__(self):
        self.ge_od = Geod(ellps='WGS84')               # 创建一个 WGS84 地理坐标系的对象
        self.head = ListNode()                         # 链表指针位置
        self.ins_data = InsData()                      # USV 惯导信息
        self.navigation_info = NavigationInfo()        # USV 导航信息
        self.navigation_control = NavigationControl()  # 导航控制信息
        self.single_path_info = SinglePathInfo()       # 当前单条路径信息
        self.path_info = TaskPath()                    # 维护一个link_list用来存储 航线信息

        self.navigation_data = NavigationData()        # los 导航信息
        self.boat_data = BoatData                      # boat 信息

        self.lat_dist_pi = 0.0
        self.timeDelay = 5.0
        self.disToAngle = 3
        self.rateDelay = 5.0
        self.ModeControl = 132010
        self.fMinAheadDist = 100
        self.factor_k = -0.001
        self.fMaxAheadDist = 200
        self.time_factor = 5.0
        self.fAngularSpeed = 0.0
        self.fFormalAngRate = 0.0

        self.iCntPi = 0
        self.kind_of_switch = 1
        self.kind_of_predict = 3
        self.kind_of_los_pre = 2
        self.kind_of_delta = 0
        self.kind_of_approach = 1
        self.advance_control = 0

        self.iUseAccLatMethod = 1
        self.iLength = 10
        self.fLengthOfLatDist = [0] * 10
        self.fSumOfLatDist = 0
        self.fPreLatDist = 0

    def get_path_info(self, path_pts: list, usv_ins: BoatMessage):
        # 清空 航线信息
        self.path_info.path.clear()

        # 航线赋值
        self.path_info.state = 1
        self.path_info.end_flag = 0
        self.path_info.PathPointNum = len(path_pts)

        for pts in path_pts:
            self.path_info.path.append(pts)

        # 头结点 赋值
        usv_point = Point(latitude=usv_ins.latitude, longitude=usv_ins.longitude)
        self.path_info.path.prepend(usv_point)

        # head -> 头结点
        self.head = self.path_info.path.head

        # 创建当前航段
        self._update_single_path_info()

    def get_usv_info(self, usv_ins: BoatMessage):
        self.navigation_info.tid = usv_ins.usv_id
        usv_point = Point(latitude=usv_ins.latitude, longitude=usv_ins.longitude)
        self.ins_data.fPoint = usv_point
        self.ins_data.fHeading = usv_ins.heading_angle

        self.ins_data.fSpeedK = to_kn(usv_ins.forward_speed)
        self.ins_data.fSpeedM = usv_ins.forward_speed

    def tick(self):
        if self.path_info.path.is_empty():
            logger.error(f"path is null")
            return

        self._get_line_tracking_info()  # 计算路径跟踪相关导航状态信息
        i_switch = self.if_switch_line(self.single_path_info, self.navigation_info, self.ins_data, self.path_info)

        if i_switch == 1:
            if self.head.next is None:
                return
            else:
                self._update_single_path_info()
        else:

            self.navigation_control = self._get_line_tracking_control()

    def get_route_angle(self):
        angle = self.calculate_bearing(self.single_path_info.fFirstPoint, self.single_path_info.fSecondPoint)
        return angle

    def get_route_speed(self):
        return to_mps(self.single_path_info.fSpeedK)

    def _get_line_tracking_info(self):
        start_point = self.single_path_info.fFirstPoint
        end_point = self.single_path_info.fSecondPoint
        self._get_info_straight(start_point, end_point, self.ins_data, self.navigation_info)

    def _get_line_tracking_control(self):
        f_full_speed = to_mps(SinglePathInfo.fSpeedK)
        control = self._straight_line_tracking( f_full_speed)  # f_full_speed 单位:m/s
        return control

    def _straight_line_tracking(self, f_tracking_velocity: float):
        self._calculate_yaw_error()

        if self.advance_control == 1:
            if abs(self.boat_data.fYawErr) >= 30.0:
                self.boat_data.fYawErr -= self.boat_data.fYawRate * 5.0
            elif 15.0 <= abs(self.boat_data.fYawErr) < 30.0:
                self.boat_data.fYawErr -= self.boat_data.fYawRate * 3.0
            elif abs(self.boat_data.fYawErr) < 15.0:
                self.boat_data.fYawErr -= self.boat_data.fYawRate * 2.0

        self.boat_data.fYawErr = calculate_angle_error_180(self.boat_data.fYawErr, 0.0)

        if self.boat_data.fYawErr > 150.0:
            self.boat_data.fYawErr = 150.0
        elif self.boat_data.fYawErr < -150.0:
            self.boat_data.fYawErr = -150.0

        self.navigation_control.flag = 1
        self.navigation_control.fTurnAngle = self.boat_data.fCurBoatYaw + self.boat_data.fYawErr

        if self.navigation_control.fTurnAngle > 360.0:
            self.navigation_control.fTurnAngle -= 360.0
        elif self.navigation_control.fTurnAngle < 0.0:
            self.navigation_control.fTurnAngle += 360.0

        self.navigation_control.fForwardVel = to_kn(f_tracking_velocity)

        return self.navigation_control

    def _calculate_yaw_error(self):
        # 得到当前时刻的偏航角（ 航迹线角 - 艏向角 ）
        f_yaw_angle = calculate_angle_error_180(self.navigation_data.fTrackLineAngle, self.boat_data.fCurBoatYaw)
        # 计算预测侧偏距值
        f_predict_distance = self._calculate_predict_distance(f_yaw_angle)
        # 计算侧偏距的距离转换系数
        f_num_of_distance = self._calculate_num_of_lat_dist(f_predict_distance)
        # 计算侧偏距积分
        self._calculate_lat_dist_i()

        if abs(self.boat_data.fAngErr) > 60 or abs(f_yaw_angle) > 90:
            self.boat_data.fYawErr = calculate_angle_error_180(self.boat_data.fToDestAngle,
                                                               self.boat_data.fCurBoatYaw)
        else:
            if f_predict_distance > 20.0:
                self.boat_data.fYawErr = calculate_angle_error_180(self.boat_data.fToDestAngle + 60,
                                                                   self.boat_data.fCurBoatYaw)
            else:
                if f_predict_distance < -20.0:
                    self.boat_data.fYawErr = calculate_angle_error_180(self.boat_data.fToDestAngle - 60,
                                                                       self.boat_data.fCurBoatYaw)
                else:
                    self.boat_data.fYawErr = self._calculate_optimal_yaw_error(f_yaw_angle,
                                                                               f_predict_distance,
                                                                               f_num_of_distance)

        if self.kind_of_approach == 1:
            self._calculate_optimal_yaw_error_by_los()

    def _calculate_predict_distance(self, f_yaw_angle: float) -> float:
        f_predict_distance = 0.0
        f_yaw_rate = self.boat_data.fYawRate
        if self.kind_of_predict == 1:
            f_predict_distance = self.boat_data.fLatDist  # 不预测
        elif self.kind_of_predict == 2:
            f_predict_distance = (self.boat_data.fLatDist +
                                  self.boat_data.fCurBoatSpeed * self.timeDelay * math.sin(math.radians(f_yaw_angle)))
        elif self.kind_of_predict == 3:
            f_predict_distance = (self.boat_data.fLatDist + self.boat_data.fCurBoatSpeed *
                                  self.timeDelay * math.sin(math.radians(f_yaw_angle - f_yaw_rate * self.rateDelay)))
        self.fPreLatDist = f_predict_distance
        return f_predict_distance

    def _calculate_num_of_lat_dist(self, f_predict_distance):
        factor = 0.0
        if self.kind_of_switch == 1:
            factor = self.disToAngle
        elif self.kind_of_switch == 2:
            if (10.0 <= f_predict_distance < 20) or (-20.0 < f_predict_distance <= -10.0):
                factor = 0.5 * self.disToAngle
            elif (5.0 <= f_predict_distance < 10.0) or (-10.0 < f_predict_distance <= -5.0):
                factor = 0.3 * self.disToAngle
            elif (0.0 <= f_predict_distance < 5.0) or (-5.0 < f_predict_distance <= -0.0):
                factor = 0.1 * self.disToAngle
        elif self.kind_of_switch == 3:
            factor = (20.0 * self.disToAngle /
                      (abs(f_predict_distance) * (1 + math.exp(-0.5 * (abs(f_predict_distance) - 10.0)))))
        return factor

    def _calculate_lat_dist_i(self):
        self.boat_data.fLatDist_I += self.boat_data.fLatDist / 10.0

        self.iCntPi += 1

        if self.iCntPi >= 50:
            self.boat_data.fLatDist_I = 0.0
            self.iCntPi = 0

    def _calculate_optimal_yaw_error(self, f_yaw_angle, f_predict_distance, f_num_of_distance):
        f_optimal_yaw_error = (f_yaw_angle + f_num_of_distance * f_predict_distance +
                               self.lat_dist_pi * self.boat_data.fLatDist_I)

        return f_optimal_yaw_error

    def _calculate_optimal_yaw_error_by_los(self):
        f_look_ahead_distance = 50.0
        f_los_line_angle = 0.0
        f_track_line_los_line_angle = 0.0
        f_threshold_to_dest = 30.0

        if self.kind_of_delta == 0:
            if self.boat_data.fCurBoatSpeed > 9:
                self.fMinAheadDist = 100
                self.fMaxAheadDist = 200
            else:
                self.fMinAheadDist = 30
                self.fMaxAheadDist = 60

            f_look_ahead_distance = (self.fMinAheadDist + (self.fMaxAheadDist - self.fMinAheadDist) *
                                     math.exp(self.factor_k * abs(self.boat_data.fLatDist) ** 3))

            self.boat_data.fAngErr = calculate_angle_error_180(self.boat_data.fAngErr, 0)

            if -90.0 <= self.boat_data.fAngErr <= 90.0:
                f_track_line_los_line_angle = calculate_angle_error_180(self.boat_data.fToDestAngle,
                                                                        self.navigation_data.fTrackLineAngle)
            elif self.boat_data.fToDestDist < f_threshold_to_dest:
                f_track_line_los_line_angle = calculate_angle_error_180(self.boat_data.fToDestAngle,
                                                                        self.navigation_data.fTrackLineAngle)
            else:
                f_tmp = self.boat_data.fLatDist
                if self.kind_of_los_pre == 1:
                    f_angle_error = calculate_angle_error_180(self.navigation_data.fTrackLineAngle,
                                                              self.boat_data.fCurBoatYaw)
                    f_predict_distance = self._calculate_predict_distance(f_angle_error)
                    f_tmp = f_predict_distance

                f_k = 3.5
                if self.iUseAccLatMethod == 1:
                    f_tmp += f_k * self.fSumOfLatDist / self.iLength

                if f_tmp > 0:
                    f_tmp += 0.0
                f_track_line_los_line_angle = math.radians(math.atanh(f_tmp / f_look_ahead_distance))

                if f_track_line_los_line_angle > 60.0:
                    f_track_line_los_line_angle = 60.0
                elif f_track_line_los_line_angle < -60.0:
                    f_track_line_los_line_angle = -60.0

        f_los_line_angle = self.navigation_data.fTrackLineAngle + f_track_line_los_line_angle  # Los线相对于正北方向夹角
        f_los_line_angle = calculate_angle_error_180(f_los_line_angle, 0)  # 将fLosLineAngle调整到 -180° - 180°
        # 计算导航角 -180° - 180°
        self.boat_data.fYawErr = calculate_angle_error_180(f_los_line_angle, self.boat_data.fCurBoatYaw)

    def _update_single_path_info(self):
        self.single_path_info.usCurTaskNum += 1
        self.single_path_info.ucLineType = 1
        self.single_path_info.fFirstPoint = self.head.val
        self.single_path_info.fSecondPoint = self.head.next.val
        self.single_path_info.fSpeedK = 20
        self.head = self.head.next

    def get_route_angle(self):
        angle = self.calculate_bearing(self.single_path_info.fFirstPoint, self.single_path_info.fSecondPoint)
        return angle

    def get_route_speed(self):
        return to_mps(self.single_path_info.fSpeedK)

    def calculate_bearing(self, point1: Point, point2: Point):
        """
        使用 pyproj 计算从 point1 到 point2 的方位角（以度为单位）
        :param point1: geopy 的 Point 对象，起点
        :param point2: geopy 的 Point 对象，终点
        :return: 方位角（以度为单位）
        """
        _, forward_azimuth, _ = self.ge_od.inv(point1.longitude, point1.latitude, point2.longitude, point2.latitude)
        if forward_azimuth < 0:
            forward_azimuth += 360
        return forward_azimuth

    def _get_info_straight(self, start_point, end_point, ins_data, navigation_info):
        self.navigation_data.fFromPoint = start_point
        self.navigation_data.fDestPoint = end_point
        # 计算航迹线的方向
        f_azimuth = self.calculate_bearing(self.navigation_data.fFromPoint, self.navigation_data.fDestPoint)
        f_distance = distance(self.navigation_data.fFromPoint, self.navigation_data.fDestPoint).miles

        f_azimuth = calculate_angle_error_180(f_azimuth, 0.0)  # 转到 -180 - 180 范围内
        self.navigation_data.fTrackLineAngle = f_azimuth
        self.navigation_data.fTrackLineDist = f_distance

        # 从惯导数据接口中取出当前 usv 位置 航速 方向 艏向角速度，存储在 BoatData 结构体中
        self.boat_data.stGpsMyBoat = ins_data.fPoint
        self.boat_data.fCurBoatSpeed = ins_data.fSpeedM
        self.boat_data.fCurBoatYaw = ins_data.fHeading
        self.boat_data.fYawRate = ins_data.fHeadingRate

        f_azimuth_1 = self.calculate_bearing(self.boat_data.stGpsMyBoat, self.navigation_data.fDestPoint)
        f_distance_1 = distance(self.boat_data.stGpsMyBoat, self.navigation_data.fDestPoint).miles

        # ang1出来之后是0~360度转到-180到180
        f_azimuth_1 = calculate_angle_error_180(f_azimuth_1, 0)

        f_azimuth_2 = self.navigation_data.fTrackLineAngle

        # ang2-ang1 调整到 -180-180，表示当前点到目标点直线与起始点到目标点直线的夹角
        f_azimuth_3 = calculate_angle_error_180(f_azimuth_2, f_azimuth_1)

        # 根据直角三角形投影计算侧偏距
        f_distance_3 = f_distance_1 * math.sin(math.radians(f_azimuth_3))

        self.boat_data.fToDestAngle = f_azimuth_1  # 到目标角度
        self.boat_data.fToDestDist = f_distance_1  # 到目标距离

        self.boat_data.fAngErr = f_azimuth_3  # 以航迹线为视角，左侧小于0右侧大于0
        self.boat_data.fLatDist = -f_distance_3  # 侧偏距，左正右负

        navigation_info.fLatDist = self.boat_data.fLatDist
        navigation_info.fLineAngle = self.navigation_data.fTrackLineAngle
        navigation_info.fToDestAngle = self.boat_data.fToDestAngle
        navigation_info.fToDestDist = self.boat_data.fToDestDist

        if self.fPreLatDist <= 0 <= navigation_info.fLatDist:
            self._clear_acc_lat_dist()
        if self.fPreLatDist >= 0 >= navigation_info.fLatDist:
            self._clear_acc_lat_dist()

        self.fPreLatDist = navigation_info.fLatDist

        self.fSumOfLatDist = 0

        for i in range(self.iLength - 1, 0, -1):
            self.fLengthOfLatDist[i] = self.fLengthOfLatDist[i - 1]
            self.fSumOfLatDist += self.fLengthOfLatDist[i]

        self.fLengthOfLatDist[0] = navigation_info.fLatDist
        self.fSumOfLatDist += self.fLengthOfLatDist[0]

    def _clear_acc_lat_dist(self):
        self.fLengthOfLatDist = [0] * 10
        self.fSumOfLatDist = 0

    def if_switch_line(self,
                       single_path_info: SinglePathInfo,
                       navigation_info: NavigationInfo,
                       ins_data: InsData,
                       task_path_info: TaskPath):
        i_switch = 0
        change_length = 4 * single_path_info.fSpeedK

        from_point = single_path_info.fFirstPoint
        dest_point = single_path_info.fSecondPoint
        i_pass = self.calculate_if_pass_dest(from_point, dest_point, ins_data)

        if single_path_info.usCurTaskNum == task_path_info.PathPointNum:
            if navigation_info.fToDestDist < 20 or i_pass == 1:
                i_switch = 1
                return i_switch
        else:
            if navigation_info.fToDestDist < change_length or i_pass == 1:
                i_switch = 1
                return i_switch

        return i_switch

    def calculate_if_pass_dest(self, from_point: Point, dest_point: Point, ins_data: InsData) -> int:
        i_pass = 0
        usv_point = ins_data.fPoint

        f_path_azimuth = self.calculate_bearing(from_point, dest_point)
        f_path_distance = distance(from_point, dest_point).miles

        f_from_to_azimuth = self.calculate_bearing(from_point, usv_point)
        f_from_to_usv_distance = distance(from_point, usv_point).miles

        f_angle_error = abs(calculate_angle_error_180(f_path_azimuth - f_from_to_azimuth, 0))

        f_project_distance = f_from_to_usv_distance * math.cos(math.radians(f_angle_error))

        if f_project_distance >= f_path_distance:
            i_pass = 1

        return i_pass
