#!/usr/bin/python3
import subprocess
import optparse
import re

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option('-i', '--interface', dest='Interface', help='Interface to change its MAC Address')
    parser.add_option('-m', '--mac', dest='New_MAC', help='New MAC Address')
    options, arguments = parser.parse_args()
    if not options.Interface:
        parser.error('[-] Please specify an Interface, use --help for more info')
    elif not options.New_MAC:
        parser.error('[-] Please specify the New MAC, use --help for more info')
    return options

def change_mac(interface, new_mac):
    print('[+] Changing MAC Address for ' + interface + ' To New_MAC: ' + new_mac)
    subprocess.call(['ifconfig', interface, 'down'])
    subprocess.call(['ifconfig', interface, 'hw', 'ether', new_mac])
    subprocess.call(['ifconfig', interface, 'up'])

def current_mac(interface):
    ifconfig_result = subprocess.check_output(['ifconfig', interface]).decode('utf-8')
    Actual_MAC = re.search('\\w\\w:\\w\\w:\\w\\w:\\w\\w:\\w\\w:\\w\\w', ifconfig_result)
    if Actual_MAC:
        return Actual_MAC.group(0)
    else:
        return "[-] Couldn't read MAC Address."

def check_mac(interface, new_mac):
    ifconfig_result = subprocess.check_output(['ifconfig', interface]).decode('utf-8')
    Actual_MAC = re.search('\\w\\w:\\w\\w:\\w\\w:\\w\\w:\\w\\w:\\w\\w', ifconfig_result)
    if Actual_MAC.group(0) == new_mac:
        print('[+] MAC Address Was Successfully Changed!')
    else:
        print("[-] Failed, The MAC Address Wasn't Changed!")
Value = get_arguments()
print('Current MAC => ' + current_mac(Value.Interface))
change_mac(Value.Interface, Value.New_MAC)
check_mac(Value.Interface, Value.New_MAC)
print('Current MAC => ' + current_mac(Value.Interface))
