#!/usr/bin/env python3
from core.banner import info, success, warn, error, highlight, CYAN, GREEN, RESET, BRIGHT
from core.checker import check_root

def scan(ip_range, interface=None, timeout=1):
    try:
        import scapy.all as scapy
    except ImportError:
        error('Scapy library is missing. Install via: pip install scapy')
        return []
    arp_request = scapy.ARP(pdst=ip_range)
    broadcast = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')
    arp_request_broadcast = broadcast / arp_request
    srp_kwargs = {'timeout': timeout, 'verbose': False}
    if interface:
        srp_kwargs['iface'] = interface
    answered_list = scapy.srp(arp_request_broadcast, **srp_kwargs)[0]
    clients = []
    for element in answered_list:
        clients.append({'ip': element[1].psrc, 'mac': element[1].hwsrc})
    return clients

def print_results(clients):
    if not clients:
        warn('No active hosts responded to ARP probe.')
        return
    print('\n' + '=' * 50)
    print(f"{CYAN}{BRIGHT}{'IP Address':<20} {'MAC Address':<20}{RESET}")
    print('-' * 50)
    for client in clients:
        print(f"{client['ip']:<20} {client['mac']:<20}")
    print('=' * 50)
    success(f'Discovered {len(clients)} active host(s) on network.')

def run(args):
    check_root(exit_on_failure=False)
    target = args.target
    if not target:
        error('Target network/IP (-t / --target) is required (e.g. 192.168.1.1/24).')
        return 1
    info(f'Scanning target network range: {target}')
    if args.interface:
        info(f'Using network interface: {args.interface}')
    try:
        clients = scan(target, interface=args.interface, timeout=args.timeout)
        print_results(clients)
        return 0
    except KeyboardInterrupt:
        warn('\nScan aborted by user.')
        return 130
    except Exception as e:
        error(f'Error during network scan: {e}')
        return 1
