#!/usr/bin/env python3
import os
import shutil
import sys
from .banner import info, success, warn, error, highlight, GREEN, RED, YELLOW, RESET, BRIGHT
DEPENDENCIES = {'scapy': {'pip': 'scapy', 'required_for': ['scan', 'arp-spoof', 'arp-detector', 'sniff', 'dns-spoof', 'code-injector', 'replace-downloads']}, 'requests': {'pip': 'requests', 'required_for': ['crawler', 'spider', 'extract-forms', 'vuln-scanner', 'brute-login', 'download', 'download-exec']}, 'bs4': {'pip': 'beautifulsoup4', 'required_for': ['extract-forms', 'vuln-scanner']}, 'colorama': {'pip': 'colorama', 'required_for': ['cli', 'dns-spoof']}, 'pynput': {'pip': 'pynput', 'required_for': ['keylogger']}, 'netfilterqueue': {'pip': 'netfilterqueue', 'system': 'sudo apt install libnetfilter-queue-dev', 'required_for': ['dns-spoof', 'net-cut', 'code-injector', 'replace-downloads']}}
SYSTEM_TOOLS = ['iptables', 'ifconfig', 'ip']

def check_root(exit_on_failure=False):
    is_root = os.geteuid() == 0 if hasattr(os, 'geteuid') else True
    if not is_root:
        warn('This operation typically requires administrative privileges (root/sudo).')
        if exit_on_failure:
            error('Please re-run this command with sudo.')
            sys.exit(1)
    return is_root

def verify_dependencies():
    highlight('Checking NetworkSecurity Dependencies...\n')
    print(f"{'Package / Tool':<20} {'Status':<12} {'Required By / Install Hint'}")
    print('-' * 75)
    all_satisfied = True
    for mod, data in DEPENDENCIES.items():
        try:
            __import__(mod)
            print(f"{mod:<20} {GREEN + '[OK]' + RESET:<21} Core module ready")
        except ImportError:
            all_satisfied = False
            hint = f"pip install {data['pip']}"
            if 'system' in data:
                hint += f" (Requires: {data['system']})"
            print(f"{mod:<20} {RED + '[MISSING]' + RESET:<21} {hint}")
    print('\n' + '-' * 75)
    print('System Utilities:')
    for tool in SYSTEM_TOOLS:
        path = shutil.which(tool)
        if path:
            print(f"{tool:<20} {GREEN + '[FOUND]' + RESET:<21} {path}")
        else:
            print(f"{tool:<20} {YELLOW + '[OPTIONAL]' + RESET:<21} Not found in PATH")
    print('-' * 75)
    if all_satisfied:
        success('All primary Python dependencies are installed and operational.')
    else:
        warn('Some dependencies are missing. Install them with: pip install -r requirements.txt')
    return all_satisfied
