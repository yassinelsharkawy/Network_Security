#!/usr/bin/env python3
import smtplib
import subprocess
from core.banner import info, success, warn, error

def send_mail(email, password, message, server_host='smtp.gmail.com', server_port=587):
    server = smtplib.SMTP(server_host, server_port)
    server.starttls()
    server.login(email, password)
    subject = 'Subject: NetworkSecurity Command Execution Report\n\n'
    server.sendmail(email, email, subject + message)
    server.quit()

def run(args):
    command = args.command
    if not command:
        error('Command (-c / --command) to execute is required.')
        return 1
    info(f'Executing local command: {command}')
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode('utf-8', errors='ignore')
    except subprocess.CalledProcessError as e:
        output = e.output.decode('utf-8', errors='ignore') if e.output else str(e)
    except Exception as e:
        error(f'Failed to execute command: {e}')
        return 1
    info('Command execution complete.')
    if args.email and args.password:
        info(f'Dispatching execution report to {args.email}...')
        try:
            send_mail(args.email, args.password, output, args.smtp_server or 'smtp.gmail.com', args.smtp_port or 587)
            success('Email report successfully dispatched.')
            return 0
        except Exception as e:
            error(f'Failed to dispatch email: {e}')
            print('\nCommand Output:')
            print(output)
            return 1
    else:
        info('No SMTP credentials provided. Displaying command output below:\n')
        print(output)
        return 0
