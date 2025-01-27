import logging
import colorlog
from datetime import datetime


class Logger:
    def __init__(self, name="Logger", log_file=None, save_to_file=False):
        # 如果没有传入 log_file，默认使用当前日期和时间（精确到分钟）作为日志文件名
        if log_file is None:
            log_file = datetime.now().strftime("%Y-%m-%d_%H-%M.log")

        # 创建日志器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # 创建控制台输出格式
        log_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s%(reset)s',
            datefmt='%Y-%m-%d %H:%M:%S',  # 设置时间格式
            log_colors={
                'DEBUG': 'blue',       # 蓝色
                'INFO': 'green',       # 绿色
                'WARNING': 'yellow',   # 黄色
                'ERROR': 'red',        # 红色
                'CRITICAL': 'purple',  # 紫色
            }
        )

        # 创建控制台处理器并设置格式
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)

        # 如果 save_to_file 为 True，则创建文件处理器
        if save_to_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S'))
            self.logger.addHandler(file_handler)

        # 添加控制台处理器
        self.logger.addHandler(console_handler)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)


# 创建日志
logger = Logger(save_to_file=False)

# 测试 Logger
if __name__ == "__main__":
    # 设置 save_to_file 为 True 时，控制台和文件都会输出；否则，只输出到控制台
    logger.debug("debug_msg")
    logger.info("info_msg")
    logger.warning("warning_msg")
    logger.error("error_msg")
    logger.critical("critical_msg")
