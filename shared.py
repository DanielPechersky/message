from threading import Thread
import abc
import logging


class Connection:
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address

    @property
    def tuple(self):
        return self.socket, self.address

    def __enter__(self):
        return self.socket.__enter__()

    def __exit__(self, *args):
        self.socket.__exit(*args)


class ConnectionHandler(Thread, abc.ABC):
    def __init__(self, connection: Connection):
        super().__init__()
        self.connection = connection
        self.disconnected = False
        self.finished = False

    @property
    def active(self):
        return not self.disconnected and not self.finished

    @abc.abstractmethod
    def finish(self):
        raise NotImplementedError


def parse_command(command, commands):
    try:
        logging.info(f"Running command {command}")
        return commands[command[1:]]()
    except KeyError:
        logging.info("Not valid command")
        return False
