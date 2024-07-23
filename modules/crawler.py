#!/usr/bin/env python3
import os
import sys
import requests
from core.banner import info, success, warn, error, CYAN, RESET, BRIGHT

def test_url(target_url, timeout=3):
    try:
        response = requests.get(target_url, timeout=timeout, allow_redirects=False)
        if response.status_code in [200, 204, 301, 302, 307, 401, 403]:
            return response.status_code
    except requests.exceptions.RequestException:
        pass
    return None

def run(args):
    url = args.url
    if not url:
        error('Target URL (-u / --url) is required.')
        return 1
    if not url.startswith('http://') and (not url.startswith('https://')):
        url = 'http://' + url
    if not url.endswith('/'):
        url += '/'
    wordlist_path = args.wordlist
    if not wordlist_path:
        default_wordlist = os.path.join(os.path.dirname(__file__), '..', 'crawler', 'common.txt')
        if os.path.exists(default_wordlist):
            wordlist_path = default_wordlist
        else:
            wordlist_path = 'common.txt'
    if not os.path.exists(wordlist_path):
        error(f'Wordlist file not found: {wordlist_path}')
        return 1
    info(f'Target Base URL: {url}')
    info(f'Using Wordlist:  {wordlist_path}')
    info('Starting directory and path enumeration...\n')
    discovered = 0
    try:
        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                word = line.strip()
                if not word or word.startswith('#'):
                    continue
                probe_url = url + word
                status = test_url(probe_url)
                if status:
                    discovered += 1
                    status_color = CYAN if status == 200 else BRIGHT
                    print(f'{status_color}[Status {status}]{RESET} Discovered: {probe_url}')
        print('\n' + '-' * 50)
        success(f'Crawl complete. Discovered {discovered} accessible endpoint(s).')
        return 0
    except KeyboardInterrupt:
        warn('\nCrawl interrupted by user.')
        return 130
