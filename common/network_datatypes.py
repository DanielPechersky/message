from hashlib import sha256
import netstruct


class Credentials:
    _struct = netstruct.NetStruct(b'H$32s')

    def __init__(self, username: str, password_hash: bytes):
        self.username = username.encode()
        self.password_hash = password_hash

    @classmethod
    def from_password(cls, username: str, password: str):
        return cls(username, sha256(password.encode()).digest())

    def build(self):
        return self._struct.pack(self.username, self.password_hash)

    @classmethod
    def parse(cls, bytes_):
        return cls(*cls._struct.unpack(bytes_))


class Message:
    max_length = 200
    _struct = netstruct.NetStruct(b'H$')

    class MessageTooLong(Exception):
        def __init__(self, message_length):
            self.message_length = message_length

    def __init__(self, contents: bytes):
        self.contents = contents
        if len(self.contents) > self.max_length:
            raise self.MessageTooLong(len(self.contents))

    @classmethod
    def from_str(cls, string):
        return cls(string.encode())

    def __str__(self):
        return self.contents.decode()

    def is_command(self):
        return self.contents.startswith(b'/')

    def build(self):
        return self._struct.pack(self.contents)

    @classmethod
    def parse(cls, bytes_):
        return cls(*cls._struct.unpack(bytes_))


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
