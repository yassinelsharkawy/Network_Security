#!/usr/bin/env python3
from core.banner import info, success, warn, error, RED, RESET, BRIGHT
from core.checker import check_root

def get_mac(ip, interface=None):
    import scapy.all as scapy
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')
    packet = broadcast / arp_request
    kwargs = {'timeout': 1, 'verbose': False}
    if interface:
        kwargs['iface'] = interface
    answered = scapy.srp(packet, **kwargs)[0]
    if answered:
        return answered[0][1].hwsrc
    return None

def run(args):
    check_root(exit_on_failure=True)
    interface = args.interface or 'eth0'
    try:
        import scapy.all as scapy
    except ImportError:
        error('Scapy library is missing. Install via: pip install scapy')
        return 1
    info(f"Monitoring network interface '{interface}' for ARP poisoning activity...")
    info('Press Ctrl+C to halt detection monitor.')
    known_macs = {}

    def process_packet(packet):
        if packet.haslayer(scapy.ARP) and packet[scapy.ARP].op == 2:
            sender_ip = packet[scapy.ARP].psrc
            response_mac = packet[scapy.ARP].hwsrc.lower()
            if sender_ip not in known_macs:
                real_mac = get_mac(sender_ip, interface)
                if real_mac:
                    known_macs[sender_ip] = real_mac.lower()
            real_mac = known_macs.get(sender_ip)
            if real_mac and real_mac != response_mac:
                print(f'\n{RED}{BRIGHT}[!] SECURITY ALERT: ARP Spoofing Detected!{RESET}')
                print(f'    Target IP:     {sender_ip}')
                print(f'    Claimed MAC:   {response_mac}')
                print(f'    Legitimate MAC:{real_mac}')
    try:
        scapy.sniff(iface=interface, store=False, prn=process_packet)
    except KeyboardInterrupt:
        info('\nARP detector terminated.')
        return 0
    except Exception as e:
        error(f'Sniffing error: {e}')
        return 1
