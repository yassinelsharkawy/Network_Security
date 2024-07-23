#!/usr/bin/python3
import scapy.all as scapy
import argparse

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--target', dest='Target', help='Target IP/IP range.')
    options = parser.parse_args()
    if not options.Target:
        parser.error('[-] Please specify an Target, use --help for more info')
    return options

def scan(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]
    upClients_list = []
    for element in answered_list:
        clients_dict = {'ip': element[1].psrc, 'mac': element[1].hwsrc}
        upClients_list.append(clients_dict)
    return upClients_list

def printing_result(results_list):
    print('IP\t\tMAC Address')
    print('------------------------------------------')
    for client in results_list:
        print(client['ip'] + '\t' + client['mac'])
Value = get_arguments()
scan_result = scan(Value.Target)
printing_result(scan_result)
