#!/usr/bin/python3
import os
import requests

def request(url):
    try:
        return requests.get('http://' + url)
    except requests.exceptions.ConnectionError:
        pass
target_url = '192.168.1.22/mutillidae/'
wordlist = 'common.txt' if os.path.exists('common.txt') else os.path.join(os.path.dirname(__file__), 'common.txt')
with open(wordlist) as file:
    for line in file:
        test_url = target_url + '/' + line.strip()
        response = request(test_url)
        if response:
            print('[+] Discovered URL PATH --> ' + test_url)
