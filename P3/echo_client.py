#!/usr/bin/env python3

import socket

HOST = '0.0.0.0'  # The server's hostname or IP address
PORT = 18001        # The port used by the server

def dec(data: bytes):
    return data.hex()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'')
    eframes = 0
    while True:
        data = s.recv(1024)
        if data:
            decoded = dec(data)
            if decoded != "0b0000007b0000000a0000000a0001":
                print(f'[{eframes:>4}] Received: "{decoded}"')
                eframes = 0
            else:
                eframes += 1
