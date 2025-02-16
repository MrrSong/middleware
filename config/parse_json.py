import json
from log.log import logger


class ParseJSON:
    def __init__(self, file_path='SimConfig.json'):
        """
        构造函数，用于初始化文件路径。
        :param file_path: JSON 文件的路径
        """
        self.file_path = file_path
        self.data = None

    def _open_json_file(self):
        """
        尝试打开 JSON 文件，若失败则抛出 AssertionError。
        """
        try:
            # 修改为 utf-8-sig 来自动处理 BOM
            with open(self.file_path, 'r', encoding='utf-8-sig') as file:
                self.data = json.load(file)
                logger.info(f"加载配置文件 '{self.file_path}' 成功！")
        except Exception as e:
            # 如果打开失败，抛出断言错误
            raise AssertionError(f"加载配置文件 '{self.file_path}' 失败！ {e}")

    def load(self):
        """
        加载并解析 JSON 文件。
        如果文件无法打开，断言抛出错误。
        """
        assert self.file_path, "配置文件路径不能为空"
        self._open_json_file()

    def get_data(self):
        """
        获取解析后的数据。
        :return: 解析后的数据
        """
        assert self.data is not None, "配置文件数据尚未加载"
        return self.data


# 测试代码
if __name__ == "__main__":
    # 实例化 ParseJSON 类并加载文件
    json_reader = ParseJSON()
    json_reader.load()

    # 获取并打印数据
    config_data = json_reader.get_data()
    print(config_data)
