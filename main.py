import os
import json
import socket
import asyncio
from log.log import logger
from message.server import UDPServer
from message.client import UDPClient
from message.parse import parse_packet
from message.boat_struct import MotionControl, Mission, Singleton
from config.parse_json import ParseJSON
from convert.coordinate_conversion import GeoConverter
from log.reader import Reader
from common import (
    record_positions,
    visualize_positions
)

# 创建一个异步锁
lock = asyncio.Lock()

# 在全局作用域创建单例
singleton_instance: Mission = Mission()

# 转发地址
forward_address = ('192.168.2.100', 4001)

# 创建转发用的 UDP 套接字
forward_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# async def update_singleton_instance(boat_message):
#     global singleton_instance
#     async with lock:
#         if hasattr(singleton_instance, 'mission'):
#             singleton_instance.mission.boat_message = boat_message
#         else:
#             raise AttributeError("singleton_instance is not initialized")
#
#
# async def receive_data(server):
#     loop = asyncio.get_event_loop()
#     while True:
#         # 使用非阻塞方式接收数据
#         data, client_address = await loop.run_in_executor(None, server.receive_message)
#         if data:
#             # logger.info(f"接收到来自 {client_address} 的消息: {data.decode()}")  # log 输出到控制台
#             parsed_data, timestamp = parse_packet(data.decode(), logger)  # 解析报文
#             for boat_message in parsed_data:
#                 await update_singleton_instance(boat_message)
#                 # logger.debug(f"singleton_instance {singleton_instance.mission.boat_message.latitude}")
#         await asyncio.sleep(0.1)  # sleep 0.1s

async def update_singleton_instance(boat_message):
    global singleton_instance
    async with lock:
        if hasattr(singleton_instance, 'mission'):
            singleton_instance.mission.boat_message = boat_message
            # 转发更新后的数据
            boat_message_str = boat_message.to_string()
            encoded_message = boat_message_str.encode()
            forward_socket.sendto(encoded_message, forward_address)
        else:
            raise AttributeError("singleton_instance is not initialized")


async def receive_data(server):
    loop = asyncio.get_event_loop()
    while True:
        # 使用非阻塞方式接收数据
        data, client_address = await loop.run_in_executor(None, server.receive_message)
        if data:
            # logger.info(f"接收到来自 {client_address} 的消息: {data.decode()}")  # log 输出到控制台
            parsed_data, timestamp = parse_packet(data.decode(), logger)  # 解析报文
            for boat_message in parsed_data:
                await update_singleton_instance(boat_message)
                # logger.debug(f"singleton_instance {singleton_instance.mission.boat_message.latitude}")
        await asyncio.sleep(0.1)  # sleep 0.1s


async def process_data(client):
    # 读取配置文件
    json_reader = ParseJSON('config/SimConfig.json')
    json_reader.load()
    config_data = json_reader.get_data()

    # 将配置文件转化为字符串
    config_data_str = json.dumps(config_data, indent=4, ensure_ascii=False)

    await client.send_message(config_data_str)

    control_str = 'scatter'  # scatter continuous

    if hasattr(singleton_instance, 'mission'):
        mission: Mission = singleton_instance.mission
        converter = GeoConverter(mission.task_area)

        await client.send_message(mission.task.task_start_str())  # 发送 任务开始 指令
        await asyncio.sleep(5)

        if control_str == 'scatter':
            json_file_path = os.path.join('.', 'log', 'metrics_20250409_1634', 'metrics.json')  # 读取指标的路径
            reader = Reader(json_file_path)  # 创建 JSONFileReader 类的实例
            content = reader.read()  # 读取 JSON 文件内容

            actions = content['actions']  # 提取 actions 列
            pos_list = content['pos_list']  # 提取 pos_list 列
            recorded_positions = record_positions(actions, pos_list)
            positions = converter.meters_to_latlon_scatter_list(recorded_positions)

            while True:
                mission: Mission = singleton_instance.mission

                motion_control: MotionControl = mission.motion_control
                motion_control.usv_id = 1
                motion_control.motion_control_mode = 3
                motion_control.throttle_or_speed = 20.0
                motion_control.rudder_angle_or_heading = 180
                motion_control_str = motion_control.to_string()  # 类型转换
                await client.send_message(motion_control_str)  # 发送 usv 控制 指令
                await asyncio.sleep(0.1)  # sleep 0.1s
        elif control_str == 'continuous':
            while True:
                mission: Mission = singleton_instance.mission

                motion_control: MotionControl = mission.motion_control
                motion_control.usv_id = 1
                motion_control.motion_control_mode = 3
                motion_control.throttle_or_speed = 20.0
                motion_control.rudder_angle_or_heading = 0
                motion_control_str = motion_control.to_string()  # 类型转换
                await client.send_message(motion_control_str)  # 发送 usv 控制 指令
                await asyncio.sleep(0.1)  # sleep 0.1s

    else:
        raise AttributeError("singleton_instance is not initialized")


async def main():
    # 在全局作用域创建单例
    global singleton_instance
    singleton_instance = await Singleton.create()

    # 创建服务端和客户端对象
    server = UDPServer(host='192.168.2.100', port=3001)
    client = UDPClient(host='192.168.2.100', port=2001)

    # 启动两个协程，一个进行数据接收，一个进行任务处理
    receive_task = asyncio.create_task(receive_data(server))  # 数据接收
    process_task = asyncio.create_task(process_data(client))  # 任务处理

    # 协程挂起
    await receive_task
    await process_task

if __name__ == "__main__":
    asyncio.run(main())
