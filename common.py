import matplotlib.pyplot as plt
from typing import List, Tuple


def pixel_to_meter(position_p: Tuple[float, float], pixels_per_meter: float) -> Tuple[float, float]:
    """
    将像素位置转换为物理位置（米）。

    :param position_p: 像素位置 (x_p, y_p)，一个包含两个元素的元组
    :param pixels_per_meter: 比例尺
    :return: 转换后的物理位置 (x_m, y_m)，元组形式
    """
    try:
        return position_p[0] * pixels_per_meter, position_p[1] * pixels_per_meter
    except IndexError:
        print("错误：输入的像素位置格式不正确，应为包含两个元素的元组。")
        return 0, 0


def batch_pixel_to_meter(positions_p: List[Tuple[float, float]], pixels_per_meter: float) -> List[Tuple[float, float]]:
    """
    批量将像素位置转换为物理位置（米）。

    :param positions_p: 像素位置列表，每个元素是一个包含两个元素的元组 (x_p, y_p)
    :param pixels_per_meter: 比例尺
    :return: 转换后的物理位置列表，每个元素是一个包含两个元素的元组 (x_m, y_m)
    """
    return [pixel_to_meter(position_p, pixels_per_meter) for position_p in positions_p]


def record_positions(actions: List[int], pos_list: List[Tuple[float, float]]) -> list[tuple[float, ...]]:
    """
    根据动作变化记录位置。

    :param actions: 动作列表
    :param pos_list: 位置列表，每个元素是一个包含两个元素的元组 (x, y)
    :return: 记录的位置列表，每个元素是一个包含两个元素的元组 (x, y)
    """
    recorded_positions = []
    if actions:
        # 记录第 0 个元素的位置
        new_pos = tuple(pos_list[0])
        recorded_positions.append(new_pos)

        pre_action = actions[0]

        for i in range(1, len(actions)):
            action = actions[i - 1]
            if action != pre_action:
                # 若当前动作与上一帧不同，记录上一帧的位置
                new_pos = tuple(pos_list[i - 1])
                recorded_positions.append(new_pos)

            # 更新 pre_action
            pre_action = action
    return recorded_positions


def _plot_positions(recorded_positions: List[Tuple[float, float]], title: str, invert_y: bool = False):
    """
    绘制位置散点图。

    :param recorded_positions: 记录的位置列表，每个元素是一个包含两个元素的元组 (x, y)
    :param title: 图表标题
    :param invert_y: 是否反转 y 轴
    """
    if not recorded_positions:
        print("没有可可视化的位置数据。")
        return
    x_coords = [pos[0] for pos in recorded_positions]
    y_coords = [pos[1] for pos in recorded_positions]

    plt.figure(figsize=(8, 6))
    # 绘制带连线的散点图
    plt.plot(x_coords, y_coords, marker='o', color='blue', label='Recorded Positions')
    plt.title(title)
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.legend()
    plt.grid(True)

    if invert_y:
        # 获取当前坐标轴对象并将 y 轴上下颠倒
        ax = plt.gca()
        ax.invert_yaxis()

    plt.show()


def visualize_positions_scatter(recorded_positions: List[Tuple[float, float]]):
    """
    可视化记录的位置，y 轴上下颠倒。

    :param recorded_positions: 记录的位置列表，每个元素是一个包含两个元素的元组 (x, y)
    """
    _plot_positions(recorded_positions, 'Recorded Positions Based on Action Changes', invert_y=True)


def visualize_positions(recorded_positions: List[Tuple[float, float]]):
    """
    可视化记录的位置。

    :param recorded_positions: 记录的位置列表，每个元素是一个包含两个元素的元组 (x, y)
    """
    _plot_positions(recorded_positions, 'Recorded Positions Based on Action Changes')