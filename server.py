import socket
import config
import logging

logging = logging.getLogger()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(config.server_address)
    s.listen()
    with s.accept() as c:
        c.send(c.recv(1024))
