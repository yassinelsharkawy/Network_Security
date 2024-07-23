#!/usr/bin/env python3
import sys
try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
    GREEN = Fore.GREEN
    CYAN = Fore.CYAN
    BLUE = Fore.BLUE
    YELLOW = Fore.YELLOW
    RED = Fore.RED
    MAGENTA = Fore.MAGENTA
    BRIGHT = Style.BRIGHT
    RESET = Style.RESET_ALL
except ImportError:
    GREEN = '\x1b[92m'
    CYAN = '\x1b[96m'
    BLUE = '\x1b[94m'
    YELLOW = '\x1b[93m'
    RED = '\x1b[91m'
    MAGENTA = '\x1b[95m'
    BRIGHT = '\x1b[1m'
    RESET = '\x1b[0m'
BANNER = f"{CYAN}{BRIGHT}\n _   _      _                      _    ____                            _ _         \n| \\ | | ___| |___      _____  _ __| | _/ ___|  ___  ___ _   _ _ __(_) |_ _   _  \n|  \\| |/ _ \\ __\\ \\ /\\ / / _ \\| '__| |/ /\\___ \\ / _ \\/ __| | | | '__| | __| | | | \n| |\\  |  __/ |_ \\ V  V / (_) | |  |   <  ___) |  __/ (__| |_| | |  | | |_| |_| | \n|_| \\_|\\___|\\__| \\_/\\_/ \\___/|_|  |_|\\_\\|____/ \\___|\\___|\\__,_|_|  |_|\\__|\\__, | \n                                                                          |___/  \n{BLUE}           Unified Network Security & Penetration Testing CLI Suite{RESET}\n{YELLOW}           v2.0.0 | Operational Security Audit & Diagnostics{RESET}\n"

def print_banner():
    print(BANNER)

def info(msg):
    print(f'{BLUE}[*]{RESET} {msg}')

def success(msg):
    print(f'{GREEN}[+]{RESET} {msg}')

def warn(msg):
    print(f'{YELLOW}[!]{RESET} {msg}')

def error(msg):
    print(f'{RED}[-]{RESET} {msg}', file=sys.stderr)

def highlight(msg):
    print(f'{CYAN}{BRIGHT}==> {msg}{RESET}')
