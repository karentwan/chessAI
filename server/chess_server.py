import socket
import select
from collections import deque
from threading import Thread
import json


class ChessServer:

    def __init__(self) -> None:
        pass

    def start(self):
        server = socket.socket()
        server.setblocking(False)
        host = socket.gethostname()
        server.bind((host, 5321))
        server.listen(5)
        rlist = deque([server])  # 读事件队列
        wlist = deque()   # 写事件队列
        xlist = deque()
        # 构造 id 与 socket的映射
        id_map = {}
        socket_map = {}
        cnt = 0
        print('server start....')
        while True:
            try:
                read_list, write_list, error_list = select.select(rlist, wlist, xlist)
                for socket_item in read_list:  # accept也属于读事件
                    if socket_item == server:  # 收到请求
                        conn, addr = socket_item.accept()
                        conn.setblocking(False)
                        rlist.append(conn)
                        id_map[cnt] = conn
                        socket_map[conn] = cnt
                        print('client [{}] connected'.format(cnt))
                        cnt += 1
                    else:
                        data = socket_item.recv(1024).decode('utf-8')
                        if data != '':  # 关闭事件
                            obj = json.loads(data)
                            print(obj)
                            # print(type(obj))
                            target_id = obj['target']
                            from_id = socket_map[socket_item]
                            obj['id'] = from_id
                            target = id_map[target_id]
                            # 转发数据
                            target.sendall(json.dumps(data).encode("utf-8"))
                        else:  # 客户端断开连接
                            if socket_item in wlist:
                                wlist.remove(socket_item)
                            rlist.remove(socket_item)
                            socket_item.close()
            except Exception as e:
                print(' error => {}'.format(str(e)))
                # 服务端关闭连接, 并且删除存有的套接字资源
                socket_item.close()
                # 服务端剔除客户端信息
                rlist.remove(socket_item)
                idx = socket_map[socket_item]
                del socket_map[socket_item]
                del id_map[idx]
            # 可写事件
            for write_item in write_list:
                pass
            # 错误项
            for error_item in error_list:
                error_item.close()
                rlist.remove(error_item)


if __name__ == '__main__':
    server = ChessServer()
    server.start()
