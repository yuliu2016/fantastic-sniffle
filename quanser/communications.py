from .common import GenericError
import socket
from urllib.parse import urlsplit
import threading


class StreamError(GenericError): pass


class PollFlag: ACCEPT = 0x04


class Timeout:
    def __init__(self, seconds=0, nanoseconds=0, is_absolute=False): pass


# noinspection PyUnusedLocal
class Stream:
    def __init__(self):
        self.sock: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = None
        self.bound = False

    def listen(self, uri, non_blocking):
        if self.bound: raise RuntimeError
        url_s = urlsplit(uri)
        if url_s.scheme != "tcpip": raise ValueError("Pi simulator: only TCP connection is allowed")
        if not non_blocking: raise ValueError("Pi simulator: non_blocking has to be true")
        self.sock.bind((url_s.hostname, url_s.port))
        self.sock.setblocking(False)
        self.sock.listen()
        self.bound = True

    def accept(self, send_buffer_size, receive_buffer_size):
        return self

    def poll(self, timeout, flags):
        if flags != PollFlag.ACCEPT:
            raise ValueError("Pi simulator: Only accepting a comm is allowed")
        try:
            self.conn, addr = self.sock.accept()
            return PollFlag.ACCEPT
        except BlockingIOError:
            return 0

    def shutdown(self):
        self.sock.close()
        self.sock.shutdown(socket.SHUT_RDWR)

    def close(self):
        self.conn.close()

    def send(self, buffer, buffer_size):
        if len(buffer) > buffer_size:
            raise ValueError("Pi simulator: Buffer size inappropriate")
        if threading.current_thread() is not threading.main_thread():
            # noinspection PyBroadException
            try:
                self.conn.sendall(buffer)
            except Exception as e:
                print(e)
        else:
            self.conn.sendall(buffer)  # don't catch exception

    def receive(self, buffer, buffer_size):
        try:
            return self.conn.recv_into(buffer, nbytes=buffer_size)
        except BlockingIOError:
            return 0

    def flush(self): pass
