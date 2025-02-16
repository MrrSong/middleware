import socket
from log.log import logger


class UDPServer:
    def __init__(self, host='127.0.0.1', port=3001):
        self.server_address = (host, port)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(self.server_address)
        logger.info(f"UDP 服务端已启动，绑定地址 {self.server_address}")

    def receive_message(self):
        # 使用阻塞方式接收数据
        return self.server_socket.recvfrom(4096)

    def send_message(self, message, client_address):
        # 使用阻塞方式发送数据
        self.server_socket.sendto(message, client_address)

    @staticmethod
    def handle_message(self, message):
        # 处理消息的逻辑，可以根据实际需求进行修改
        return f"服务端收到：{message}"

    def close(self):
        self.server_socket.close()
        print("服务端关闭。")
