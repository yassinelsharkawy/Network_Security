#!/usr/bin/env python3
import random
import re
import subprocess
import shutil
from core.banner import info, success, warn, error
from core.checker import check_root

def get_current_mac(interface):
    try:
        if shutil.which('ip'):
            output = subprocess.check_output(['ip', 'link', 'show', interface], stderr=subprocess.DEVNULL).decode('utf-8')
            match = re.search('link/ether\\s+([0-9a-fA-F:]{17})', output)
            if match:
                return match.group(1).lower()
        if shutil.which('ifconfig'):
            output = subprocess.check_output(['ifconfig', interface], stderr=subprocess.DEVNULL).decode('utf-8')
            match = re.search('([0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5})', output)
            if match:
                return match.group(0).lower()
        sysfs_path = f'/sys/class/net/{interface}/address'
        with open(sysfs_path, 'r') as f:
            return f.read().strip().lower()
    except Exception:
        return None

def generate_random_mac():
    byte_0 = random.choice([2, 6, 10, 14])
    remaining = [random.randint(0, 255) for _ in range(5)]
    mac_bytes = [byte_0] + remaining
    return ':'.join((f'{b:02x}' for b in mac_bytes))

def change_mac(interface, new_mac):
    check_root(exit_on_failure=True)
    info(f'Target Interface: {interface}')
    info(f'Requested MAC:    {new_mac}')
    if shutil.which('ip'):
        try:
            subprocess.check_call(['ip', 'link', 'set', 'dev', interface, 'down'])
            subprocess.check_call(['ip', 'link', 'set', 'dev', interface, 'address', new_mac])
            subprocess.check_call(['ip', 'link', 'set', 'dev', interface, 'up'])
            return True
        except subprocess.CalledProcessError:
            pass
    if shutil.which('ifconfig'):
        try:
            subprocess.check_call(['ifconfig', interface, 'down'])
            subprocess.check_call(['ifconfig', interface, 'hw', 'ether', new_mac])
            subprocess.check_call(['ifconfig', interface, 'up'])
            return True
        except subprocess.CalledProcessError as e:
            error(f'Failed to change MAC address: {e}')
            return False
    error("Neither 'ip' nor 'ifconfig' command found on the system.")
    return False

def run(args):
    interface = args.interface
    if not interface:
        error('Network interface (-i / --interface) is required.')
        return 1
    current = get_current_mac(interface)
    if current:
        info(f'Current MAC address: {current}')
    else:
        error(f"Could not read MAC address for interface '{interface}'. Ensure it exists.")
        return 1
    if args.show:
        return 0
    if args.random:
        new_mac = generate_random_mac()
        info(f'Generated random MAC address: {new_mac}')
    elif args.mac:
        new_mac = args.mac.lower()
        if not re.match('^([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})$', new_mac):
            error(f'Invalid MAC address format: {new_mac}')
            return 1
    else:
        error('Please specify a new MAC address (-m) or use --random.')
        return 1
    if change_mac(interface, new_mac):
        updated = get_current_mac(interface)
        if updated and updated.lower() == new_mac.lower():
            success(f'MAC address for {interface} successfully changed to {updated}!')
            return 0
        else:
            warn(f"Interface MAC is currently '{updated}'. Verification check failed.")
            return 1
    return 1
