import socket
import config
import logging
from shared import Connection, ConnectionHandler, parse_command


class Receiver(ConnectionHandler):
    def __init__(self, connection, owner):
        super().__init__(connection)
        self.owner = owner

    def run(self):
        logging.debug(f"Ready to receive from {self.connection.address}")
        while self.active:
            encoded_message = self.connection.socket.recv(1024)
            if encoded_message:
                self.owner.process_message(encoded_message)
            else:
                self.disconnected = True

    def finish(self):
        self.finished = True


class Client:

    def stop_command(self):
        self.finish()
        return False

    def process_message(self, encoded_message):
        decoded_message = encoded_message.decode()
        should_display = True
        if decoded_message.startswith('/'):
            should_display = parse_command(decoded_message, self.commands)
        if should_display:
            print(decoded_message)

    def __init__(self, address):
        self.connection = Connection(socket.socket(socket.AF_INET, socket.SOCK_STREAM), address)
        logging.info(f"Attempting to connect to {self.connection.address}")
        self.connection.socket.connect(self.connection.address)
        logging.info("Connected successfully")

        self.commands = {'dc': self.stop_command}

        self.receiver = Receiver(self.connection, self)
        self.receiver.start()

        self.finished = False

        self.main_loop()

    def main_loop(self):
        while not self.finished:
            logging.debug("Loop")
            if self.receiver.disconnected:
                logging.info("Disconnected")
                self.finish()
            else:
                try:
                    self.connection.socket.send(input().encode())
                except KeyboardInterrupt:
                    logging.debug("KeyboardInterrupt")
                    self.connection.socket.send(b"Disconnecting")
                    self.finish()

    def finish(self):
        logging.debug("Finishing")
        self.receiver.finish()
        self.finished = True
        self.connection.socket.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            logging.error((exc_type, exc_value, traceback))

        if not self.finished:
            self.finish()


if __name__ == '__main__':
    with Client(config.server_address) as c:
        pass
    logging.debug("Finished")
