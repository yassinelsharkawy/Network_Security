#!/usr/bin/python3
import scapy.all as scapy

def scan(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]
    return answered_list

def printing_result(answer):
    print('IP\t\tMAC Address')
    print('------------------------------------------')
    for element in answer:
        print(element[1].psrc + '\t' + element[1].hwsrc)
printing_result(scan('192.168.1.1/24'))
