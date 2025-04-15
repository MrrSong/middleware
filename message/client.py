import socket
import asyncio
from log.log import logger


class UDPClient:
    def __init__(self, host='192.168.2.100', port=2001):
        self.server_address = (host, port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logger.info(f"UDP 客户端已启动，绑定地址 {self.server_address}")

    async def send_message(self, message):
        # 使用 async 方法发送消息
        await asyncio.to_thread(self._send_message, message)

    def _send_message(self, message):
        # 发送消息到服务端（同步方法）
        self.client_socket.sendto(message.encode(), self.server_address)
        logger.info(f"send {message}")

    async def receive_message(self):
        # 使用 async 方法接收消息
        data = await asyncio.to_thread(self._receive_message)
        return data

    def _receive_message(self):
        # 接收服务端的回复（同步方法）
        data, server = self.client_socket.recvfrom(4096)
        return data.decode()

    def close(self):
        self.client_socket.close()
        print("客户端关闭。")
