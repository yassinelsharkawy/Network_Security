#!/usr/bin/python3
import subprocess
import netfilterqueue

def process_packet(packet):
    print(packet)
    packet.accept()
subprocess.call(['sudo', 'iptables', '-I', 'FORWARD', '-j', 'NFQUEUE', '--queue-num', '0'])
queue = netfilterqueue.NetfilterQueue()
queue.bind(0, process_packet)
queue.run()
