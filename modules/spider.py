#!/usr/bin/env python3
import re
import urllib.parse
import requests
from core.banner import info, success, warn, error, CYAN, RESET

def extract_links_from(url, session=None):
    try:
        requester = session if session else requests
        response = requester.get(url, timeout=5)
        return re.findall('href=[\\\'"](.*?)[\\\'"]', response.text)
    except Exception:
        return []

def crawl(base_url, current_url, visited, max_depth=5, current_depth=0):
    if current_depth > max_depth:
        return
    href_links = extract_links_from(current_url)
    for link in href_links:
        full_url = urllib.parse.urljoin(current_url, link)
        if '#' in full_url:
            full_url = full_url.split('#')[0]
        if base_url in full_url and full_url not in visited:
            visited.add(full_url)
            print(f'{CYAN}[Spider]{RESET} {full_url}')
            crawl(base_url, full_url, visited, max_depth, current_depth + 1)

def run(args):
    url = args.url
    if not url:
        error('Target URL (-u / --url) is required.')
        return 1
    if not url.startswith('http://') and (not url.startswith('https://')):
        url = 'http://' + url
    info(f'Target site to spider: {url}')
    info('Extracting internal hyperlinks recursively...\n')
    visited = set([url])
    print(f'{CYAN}[Root]{RESET}   {url}')
    try:
        crawl(url, url, visited, max_depth=args.max_depth or 10)
        print('\n' + '-' * 50)
        success(f'Spidering completed. Identified {len(visited)} unique endpoint(s).')
        return 0
    except KeyboardInterrupt:
        warn('\nSpidering interrupted by user.')
        return 130
