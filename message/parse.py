import datetime
from message.boat_struct import BoatMessage


def parse_packet(packet_str, logger):
    # 去掉首尾的 "[" 和 "]"
    packet_str = packet_str.strip('[]')
    # 将字符串按逗号分割成列表
    packet_list = packet_str.split(',')
    # 解析时间戳（最后一个字段是时间戳）
    timestamp_str = packet_list[-1]
    timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d-%H-%M-%S-%f")
    # 将时间戳替换原来的时间戳字符串
    packet_list[-1] = timestamp

    header = int(packet_list[0])
    parsed_data = []
    if header == 21:
        usv_num = int(packet_list[1])
        for i in range(usv_num):
            start_index = 2 + i * 20
            end_index = start_index + 20
            boat_message = packet_list[start_index:end_index]
            parsed_data.append(BoatMessage.from_packet(boat_message))

        # for boat_message in parsed_data:
            # logger.info(boat_message.__dict__)

    return parsed_data, timestamp

