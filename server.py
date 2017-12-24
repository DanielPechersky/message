import socket
import config
import logging
from shared import Connection, ConnectionHandler, parse_command
from queue import Queue


class ClientHandler(ConnectionHandler):
    def __init__(self, connection, new_messages: Queue):
        super().__init__(connection)
        self.new_messages = new_messages

    def run(self):
        logging.info(f"Receiving from {self.connection.address}")
        while self.active:
            self.receive()

    def receive(self):
        try:
            message = self.connection.socket.recv(1024)
            if message:
                logging.info(f"Received message {message} from {self.connection.address}")
                self.new_messages.put(message)
            else:
                self.disconnected = True
        except ConnectionError:
            self.disconnected = True

    def send(self, message):
        self.connection.socket.send(message)

    def finish(self):
        self.finished = True
        self.connection.socket.close()
        self.join()


class Listener(ConnectionHandler):
    def __init__(self, address, new_connections: Queue):
        super().__init__(Connection(socket.socket(socket.AF_INET, socket.SOCK_STREAM), address))
        self.connection.socket.bind(address)
        self.connection.socket.listen()

        self.new_connections = new_connections

        self.finished = False

    def run(self):
        logging.debug("Listening")
        try:
            while self.active:
                connection = Connection(*self.connection.socket.accept())
                self.new_connections.put(connection)
                logging.info(f"Accepted new connection from {connection.address}")
        except ConnectionError:
            self.disconnected = True

    def finish(self):
        self.finished = True
        self.connection.socket.close()
        self.join()


class Server:

    def stop_command(self):
        self.finish()
        return False

    def broadcast(self, encoded_message):
        logging.info(f"Broadcasting {encoded_message}")
        for client_handler in self.client_handlers:
            client_handler.send(encoded_message)
        self.old_messages.append(encoded_message)

    def process_message(self, encoded_message):
        logging.debug(f"Processing message {encoded_message}")
        decoded_message = encoded_message.decode()

        should_display = True
        if decoded_message.startswith('/'):
            should_display = parse_command(decoded_message, self.commands)
        if should_display:
            self.broadcast(encoded_message)

    def process_connection(self, connection):
        receiver = ClientHandler(connection, self.new_messages)
        receiver.start()
        self.client_handlers.append(receiver)

    def __init__(self, port):
        self.finishing = False

        self.commands = {'stop': self.stop_command}

        self.new_connections = Queue()
        self.listener = Listener(('', port), self.new_connections)
        self.listener.start()

        self.client_handlers = []
        self.old_messages = []
        self.new_messages = Queue()

        self.main_loop()

    def update_client_handlers(self):
        for client_handler in self.client_handlers:
            if client_handler.disconnected:
                logging.info(f"{client_handler.connection.address} disconnected")
                client_handler.finish()
                self.client_handlers.remove(client_handler)

    def main_loop(self):
        try:
            while not self.finishing:
                self.update_client_handlers()

                while not self.new_connections.empty():
                    self.process_connection(self.new_connections.get())

                while not self.new_messages.empty():
                    self.process_message(self.new_messages.get())
        except KeyboardInterrupt:
            self.finish()

    def finish(self):
        logging.debug("Finishing")
        self.update_client_handlers()
        self.broadcast(b"/dc")
        self.finishing = True
        for client_handler in self.client_handlers:
            client_handler.finish()
        self.listener.finish()
        self.update_client_handlers()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            logging.error((exc_type, exc_value, traceback))

        if not self.finishing:
            self.finish()


if __name__ == '__main__':
    with Server(config.server_address[1]) as s:
        pass
    logging.debug("Finished")
