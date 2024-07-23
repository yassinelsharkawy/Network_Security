#!/usr/bin/env python3
import urllib.parse
import requests
from bs4 import BeautifulSoup
from core.banner import info, success, warn, error, highlight, CYAN, YELLOW, RESET, BRIGHT

def extract_forms(url, session=None):
    requester = session if session else requests
    response = requester.get(url, timeout=5)
    soup = BeautifulSoup(response.content, features='html.parser')
    return soup.find_all('form')

def run(args):
    url = args.url
    if not url:
        error('Target URL (-u / --url) is required.')
        return 1
    if not url.startswith('http://') and (not url.startswith('https://')):
        url = 'http://' + url
    info(f'Extracting HTML forms from: {url}\n')
    try:
        forms = extract_forms(url)
        if not forms:
            warn('No HTML forms found on the target page.')
            return 0
        success(f'Discovered {len(forms)} form(s) on target page:')
        for idx, form in enumerate(forms, 1):
            action = form.get('action') or ''
            method = (form.get('method') or 'get').upper()
            post_url = urllib.parse.urljoin(url, action)
            print(f'\n{CYAN}{BRIGHT}--- Form #{idx} ---{RESET}')
            print(f'Action URL: {post_url}')
            print(f'Method:     {method}')
            print('Inputs:')
            inputs = form.find_all(['input', 'textarea', 'select'])
            test_data = {}
            for inp in inputs:
                name = inp.get('name')
                input_type = inp.get('type', 'text')
                value = inp.get('value', '')
                if name:
                    print(f'  - Name: {name:<20} Type: {input_type:<10} Default: {value}')
                    if input_type in ['text', 'search']:
                        test_data[name] = 'TestInput'
                    else:
                        test_data[name] = value
            if args.submit and inputs:
                info(f'Submitting test payload to Form #{idx}...')
                if method == 'POST':
                    resp = requests.post(post_url, data=test_data, timeout=5)
                else:
                    resp = requests.get(post_url, params=test_data, timeout=5)
                print(f'Response Status: {resp.status_code} (Length: {len(resp.content)} bytes)')
        return 0
    except Exception as e:
        error(f'Error during form extraction: {e}')
        return 1
