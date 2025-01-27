import json
import time
import asyncio
from log.log import logger
from message.server import UDPServer
from message.client import UDPClient
from message.parse import parse_packet
from message.boat_struct import MotionControl, BoatMessage, Mission, Singleton
from config.parse_json import ParseJSON

# 在全局作用域创建单例
singleton_instance: Mission = Mission()


async def receive_data(server):
    loop = asyncio.get_event_loop()
    while True:
        # 使用非阻塞方式接收数据
        data, client_address = await loop.run_in_executor(None, server.receive_message)
        if data:
            # logger.info(f"接收到来自 {client_address} 的消息: {data.decode()}")  # log 输出到控制台
            parsed_data, timestamp = parse_packet(data.decode(), logger)  # 解析报文
            for boat_message in parsed_data:
                if hasattr(singleton_instance, 'mission'):
                    singleton_instance.mission.boat_message = boat_message
                    logger.debug(singleton_instance.mission.boat_message)
                else:
                    raise AttributeError("singleton_instance is not initialized")

        await asyncio.sleep(0.1)  # sleep 0.1s


async def process_data(client):
    # 读取配置文件
    json_reader = ParseJSON('config/SimConfig.json')
    json_reader.load()
    config_data = json_reader.get_data()

    # 将配置文件转化为字符串
    config_data_str = json.dumps(config_data, indent=4, ensure_ascii=False)

    await client.send_message(config_data_str)
    await client.send_message("[26, 1]")

    if hasattr(singleton_instance, 'mission'):
        motion_control: MotionControl = singleton_instance.mission.boat_message
        motion_control.usv_id = 1
        motion_control.motion_control_mode = 3
        motion_control.throttle_or_speed = 10.0
        motion_control.rudder_angle_or_heading = 0
        motion_control_str = motion_control.to_string()  # 类型转换
        await client.send_message(motion_control_str)  # 发送

    else:
        raise AttributeError("singleton_instance is not initialized")

    await asyncio.sleep(0.1)  # sleep 0.1s


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
