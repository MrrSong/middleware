import os
import json
import time
import socket
import threading
from geopy import Point
from log.log import logger
from message.server import UDPServer
from message.client import UDPClient
from message.parse import parse_packet
from message.boat_struct import RectangularTaskArea, MotionControl, Mission, Singleton
from config.parse_json import ParseJSON
from convert.coordinate_conversion import GeoConverter
from log.reader import Reader
from los.los_controller import LOSController
from common import (
    record_positions,
    visualize_positions
)
from threading import Lock

# 创建一个锁
lock = Lock()

# 在全局作用域创建单例
# 在全局作用域创建单例
singleton_instance: Mission = Mission()
task_area = RectangularTaskArea()
converter = GeoConverter(task_area)


# 创建转发用的 UDP 套接字
forward_client = UDPClient(host='192.168.2.100', port=4001)


def update_singleton_instance(boat_message):
    global singleton_instance
    with lock:
        if hasattr(singleton_instance, 'mission'):
            singleton_instance.mission.boat_message = boat_message
            # 转发更新后的数据
            x_m, y_m = converter.latlon_to_meters_continuous(Point(latitude=boat_message.latitude,
                                                                   longitude=boat_message.longitude))
            heading_degree = boat_message.heading_angle
            singleton_instance.mission.usv_posture.x_m = x_m
            singleton_instance.mission.usv_posture.y_m = y_m
            singleton_instance.mission.usv_posture.heading_degree = heading_degree
            send_message = singleton_instance.mission.usv_posture.to_string()
            forward_client.send_message(send_message)
        else:
            raise AttributeError("singleton_instance is not initialized")


def receive_data(server):
    while True:
        # 使用阻塞方式接收数据
        data, client_address = server.receive_message()
        if data:
            # logger.info(f"接收到来自 {client_address} 的消息: {data.decode()}")  # log 输出到控制台
            parsed_data, timestamp = parse_packet(data.decode(), logger)  # 解析报文
            for boat_message in parsed_data:
                update_singleton_instance(boat_message)
                # logger.debug(f"singleton_instance {singleton_instance.mission.boat_message.latitude}")


def process_data(client):
    # 读取配置文件
    json_reader = ParseJSON('config/SimConfig.json')
    json_reader.load()
    config_data = json_reader.get_data()

    # 将配置文件转化为字符串
    config_data_str = json.dumps(config_data, indent=4, ensure_ascii=False)

    client.send_message(config_data_str)

    control_str = 'continuous'  # scatter continuous

    if hasattr(singleton_instance, 'mission'):
        mission: Mission = singleton_instance.mission

        client.send_message(mission.task.task_start_str())  # 发送 任务开始 指令
        time.sleep(5)

        # 发送可视化标志
        singleton_instance.mission.visual_flag.VISUAL_FLAG = 1
        forward_client.send_message(singleton_instance.mission.visual_flag.visual_flag_str())

        if control_str == 'scatter':
            json_file_path = os.path.join('.', 'log', 'metrics_20250409_1634', 'metrics.json')  # 读取指标的路径
            reader = Reader(json_file_path)  # 创建 JSONFileReader 类的实例
            content = reader.read()  # 读取 JSON 文件内容

            actions = content['actions']  # 提取 actions 列
            pos_list = content['pos_list']  # 提取 pos_list 列
            recorded_positions = record_positions(actions, pos_list)
            positions = converter.meters_to_latlon_scatter_list(recorded_positions)
            los_controller = LOSController()
            usv_ins = singleton_instance.mission.boat_message
            los_controller.get_path_info(positions, usv_ins)

            while True:
                mission: Mission = singleton_instance.mission
                usv_ins = mission.boat_message
                los_controller.get_usv_info(usv_ins)
                los_controller.tick()
                navigation_control = los_controller.navigation_control

                motion_control: MotionControl = mission.motion_control
                motion_control.usv_id = 1
                motion_control.motion_control_mode = 3
                motion_control.throttle_or_speed = navigation_control.fForwardVel
                motion_control.rudder_angle_or_heading = navigation_control.fTurnAngle
                motion_control_str = motion_control.to_string()  # 类型转换
                client.send_message(motion_control_str)  # 发送 usv 控制 指令
                time.sleep(0.1)  # sleep 0.1s
        elif control_str == 'continuous':
            while True:
                mission: Mission = singleton_instance.mission

                motion_control: MotionControl = mission.motion_control
                motion_control.usv_id = 1
                motion_control.motion_control_mode = 3
                motion_control.throttle_or_speed = 20.0
                motion_control.rudder_angle_or_heading = 180
                motion_control_str = motion_control.to_string()  # 类型转换
                client.send_message(motion_control_str)  # 发送 usv 控制 指令
                time.sleep(0.1)  # sleep 0.1s

    else:
        raise AttributeError("singleton_instance is not initialized")


def main():
    # 在全局作用域创建单例
    global singleton_instance
    singleton_instance = Singleton.create()

    # 创建服务端和客户端对象
    server = UDPServer(host='192.168.2.100', port=3001)
    client = UDPClient(host='192.168.2.100', port=2001)

    # 启动两个线程，一个进行数据接收，一个进行任务处理
    receive_thread = threading.Thread(target=receive_data, args=(server,))  # 数据接收
    process_thread = threading.Thread(target=process_data, args=(client,))  # 任务处理

    # 启动线程
    receive_thread.start()
    process_thread.start()

    # 等待线程结束
    receive_thread.join()
    process_thread.join()


if __name__ == "__main__":
    main()