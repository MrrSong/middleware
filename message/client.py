import socket
from log.log import logger


class UDPClient:
    def __init__(self, host='192.168.2.100', port=2001):
        self.server_address = (host, port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logger.info(f"UDP 客户端已启动，绑定地址 {self.server_address}")

    def send_message(self, message, printf=False):
        # 发送消息到服务端
        self.client_socket.sendto(message.encode(), self.server_address)
        if printf:
            logger.info(f"send {message}")

    def receive_message(self):
        # 接收服务端的回复
        data, server = self.client_socket.recvfrom(4096)
        return data.decode()

    def close(self):
        self.client_socket.close()
        print("客户端关闭。")