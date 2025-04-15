import matplotlib.pyplot as plt


def record_positions(actions, pos_list):
    recorded_positions = []
    if actions:
        # 记录第 0 个元素的位置并乘以 100
        new_pos = [i * 20 for i in pos_list[0]]
        recorded_positions.append(new_pos)

        for i in range(1, len(actions)):
            if actions[i] != actions[i - 1]:
                # 若当前动作与上一帧不同，记录上一帧的位置并乘以 100
                new_pos = [i * 20 for i in pos_list[i - 1]]
                recorded_positions.append(new_pos)
    return recorded_positions


def visualize_positions(recorded_positions):
    if not recorded_positions:
        print("没有可可视化的位置数据。")
        return
    x_coords = [pos[0] for pos in recorded_positions]
    y_coords = [pos[1] for pos in recorded_positions]

    plt.figure(figsize=(8, 6))
    # 绘制带连线的散点图
    plt.plot(x_coords, y_coords, marker='o', color='blue', label='Recorded Positions')
    plt.title('Recorded Positions Based on Action Changes')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.legend()
    plt.grid(True)
    plt.show()

