import json
import os
from datetime import datetime


class Reader:
    def __init__(self, file_path):
        self.file_path = file_path

    def read(self):
        try:
            if not os.path.exists(self.file_path):
                print(f"错误: 文件 {self.file_path} 不存在。")
                return None
            with open(self.file_path, 'r') as file:
                data = json.load(file)
                return data
        except json.JSONDecodeError:
            print(f"错误: 文件 {self.file_path} 不是有效的 JSON 格式。")
            return None
        except Exception as e:
            print(f"错误: 发生了一个未知错误: {e}")
            return None


if __name__ == "__main__":
    # 生成保存路径（假设和之前保存路径生成规则一致）
    json_file_path = os.path.join('..', 'experiment', 'metrics_20250403_1445', 'metrics.json')

    # 创建 JSONFileReader 类的实例
    reader = Reader(json_file_path)
    # 读取 JSON 文件内容
    content = reader.read()
    if content is not None:
        print("文件内容如下:")
        print(content)
