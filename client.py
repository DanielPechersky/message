import socket
import config
import logging

logger = logging.getLogger()


async def recieve(socket):
    while True:
        print(s.recv(1024))


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    host, port = config.client_address
    logger.info(f"Attempting to connect to {host}:{port}")
    s.settimeout(10)
    s.connect(config.server_address)
    reciever = recieve(s)
    try:
        while True:
            s.send(input())

    except KeyboardInterrupt:
        s.send("Disconnected")
