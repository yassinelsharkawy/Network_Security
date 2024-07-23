#!/usr/bin/env python3
import subprocess
from core.banner import info, success, warn, error
from core.checker import check_root

def setup_iptables(queue_num):
    subprocess.call(['iptables', '-I', 'FORWARD', '-j', 'NFQUEUE', '--queue-num', str(queue_num)])
    success(f'Configured iptables FORWARD rule for queue {queue_num}.')

def flush_iptables():
    warn('Flushing iptables filter rules...')
    subprocess.call(['iptables', '--flush'])
    success('iptables reset.')

def run(args):
    check_root(exit_on_failure=True)
    queue_num = args.queue_num if args.queue_num is not None else 0
    drop_mode = args.drop
    try:
        import netfilterqueue
    except ImportError as e:
        error(f'netfilterqueue missing: {e}')
        error('Install via: sudo apt install libnetfilter-queue-dev && pip install netfilterqueue')
        return 1
    action_label = 'DROPPING (blocking traffic)' if drop_mode else 'ACCEPTING (forwarding traffic)'
    info(f'Net Cut active on queue {queue_num}. Action: {action_label}')
    info('Press Ctrl+C to terminate and restore normal network flow.')

    def process_packet(packet):
        if drop_mode:
            packet.drop()
        else:
            packet.accept()
    setup_iptables(queue_num)
    queue = netfilterqueue.NetfilterQueue()
    try:
        queue.bind(queue_num, process_packet)
        queue.run()
    except KeyboardInterrupt:
        info('\nStopping Net Cut...')
    finally:
        flush_iptables()
    return 0
