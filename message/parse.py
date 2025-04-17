import datetime
from message.boat_struct import (
    Path,
    LocalPoint,
    UsvPosture,
    BoatMessage,
    Visualization
)


def parse_packet(packet_str, logger):
    # 去掉首尾的 "[" 和 "]"
    packet_str = packet_str.strip('[]')
    # 将字符串按逗号分割成列表
    packet_list = packet_str.split(',')
    header = int(packet_list[0])
    parsed_data = []
    if header == 10:
        visual_flag = Visualization(visual_flag=packet_list[1], feedback_flag=packet_list[2])
        parsed_data.append(visual_flag)
    elif header == 11:
        x_m = float(packet_list[1])
        y_m = float(packet_list[2])
        heading_degree = float(packet_list[3])
        usv_posture = UsvPosture(x_m=x_m, y_m=y_m, heading_degree=heading_degree)
        parsed_data.append(usv_posture)
    elif header == 12:
        point_num = int(packet_list[1])
        path_points = []
        for i in range(point_num):
            start_index = 2 + i * 3
            x_m = float(packet_list[start_index])
            y_m = float(packet_list[start_index + 1])
            speed = float(packet_list[start_index + 2])
            path_points.append(LocalPoint(x_m=x_m, y_m=y_m, speed=speed))
        feedback_flag = int(packet_list[-1])
        path = Path(point_num=point_num, path_points=path_points, feedback_flag=feedback_flag)
        parsed_data.append(path)
    elif header == 21:    # 解析时间戳（最后一个字段是时间戳）
        timestamp_str = packet_list[-1]
        timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d-%H-%M-%S-%f")
        # 将时间戳替换原来的时间戳字符串
        packet_list[-1] = timestamp
        usv_num = int(packet_list[1])
        for i in range(usv_num):
            start_index = 2 + i * 20
            end_index = start_index + 20
            boat_message = packet_list[start_index:end_index]
            parsed_data.append(BoatMessage.from_packet(boat_message))

    # for message in parsed_data:
    #     logger.info(message.__dict__)

    return parsed_data, header

