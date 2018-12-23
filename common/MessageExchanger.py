import socket
from collections import deque
import select


class MessageExchanger:
    def __init__(self):
        self.connections = []
        self.send_queue = deque()
        self.recv_queue = deque()


    def recv_loop(self):
        pass

