import socket
from threading import Thread
import json
import time

class Client:

    def write(self):
        while True:
            x = input("x: ").strip()
            y = input('y: ').strip()
            data = {
                'target': 0,
                "x": x,
                "y": y
            }
            print(self.client.send(json.dumps(data).encode("utf-8")))

    def recv(self):
        self.client = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        host = socket.gethostname()
        self.client.connect((host, 5321))
        # 开启一个读线程
        t = Thread(target=self.write)
        t.setDaemon(True)
        t.start()
        while True:
            data = self.client.recv(1024).decode('utf-8')  # 阻塞
            print(data)


if __name__ == '__main__':
    client = Client()
    client.recv()