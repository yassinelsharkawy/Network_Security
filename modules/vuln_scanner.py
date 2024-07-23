#!/usr/bin/env python3
import re
import urllib.parse
import requests
from bs4 import BeautifulSoup
from core.banner import info, success, warn, error, highlight, RED, GREEN, CYAN, RESET, BRIGHT

class WebScanner:

    def __init__(self, target_url, links_to_ignore=None):
        self.session = requests.Session()
        self.target_url = target_url
        self.target_links = []
        self.links_to_ignore = links_to_ignore or []
        self.vulnerabilities_found = 0

    def extract_links_from(self, url):
        try:
            response = self.session.get(url, timeout=5)
            return re.findall('href=[\\\'"](.*?)[\\\'"]', response.text)
        except Exception:
            return []

    def crawl(self, url=None, max_depth=5, current_depth=0):
        if url is None:
            url = self.target_url
        if current_depth > max_depth:
            return
        for link in self.extract_links_from(url):
            full_link = urllib.parse.urljoin(url, link)
            if '#' in full_link:
                full_link = full_link.split('#')[0]
            if self.target_url in full_link and full_link not in self.target_links and (full_link not in self.links_to_ignore):
                self.target_links.append(full_link)
                print(f'{CYAN}[Endpoint]{RESET} {full_link}')
                self.crawl(full_link, max_depth, current_depth + 1)

    def extract_forms(self, url):
        try:
            response = self.session.get(url, timeout=5)
            soup = BeautifulSoup(response.content, features='html.parser')
            return soup.find_all('form')
        except Exception:
            return []

    def submit_form(self, form, value, url):
        action = form.get('action')
        post_url = urllib.parse.urljoin(url, action)
        method = (form.get('method') or 'get').lower()
        inputs_list = form.find_all(['input', 'textarea'])
        post_data = {}
        for inp in inputs_list:
            input_name = inp.get('name')
            input_type = inp.get('type', 'text')
            input_value = inp.get('value', '')
            if input_type in ['text', 'search']:
                input_value = value
            if input_name:
                post_data[input_name] = input_value
        if method == 'post':
            return self.session.post(post_url, data=post_data, timeout=5)
        return self.session.get(post_url, params=post_data, timeout=5)

    def test_xss_in_form(self, form, url):
        xss_payload = "<sCript>alert('SecAuditXSS')</scriPt>"
        try:
            response = self.submit_form(form, xss_payload, url)
            return xss_payload in response.text
        except Exception:
            return False

    def test_xss_in_link(self, url):
        xss_payload = "<sCript>alert('SecAuditXSS')</scriPt>"
        test_url = url.replace('=', '=' + urllib.parse.quote(xss_payload))
        try:
            response = self.session.get(test_url, timeout=5)
            return xss_payload in response.text
        except Exception:
            return False

    def run_scanner(self):
        info(f'Auditing {len(self.target_links)} discovered endpoint(s) for XSS...')
        for link in self.target_links:
            forms = self.extract_forms(link)
            for form in forms:
                is_vuln = self.test_xss_in_form(form, link)
                if is_vuln:
                    self.vulnerabilities_found += 1
                    print(f'\n{RED}{BRIGHT}[!] Confirmed Reflected XSS in form at:{RESET} {link}')
                    action = form.get('action') or ''
                    print(f'    Form Action: {urllib.parse.urljoin(link, action)}')
            if '=' in link:
                is_vuln = self.test_xss_in_link(link)
                if is_vuln:
                    self.vulnerabilities_found += 1
                    print(f'\n{RED}{BRIGHT}[!] Confirmed Reflected XSS in parameter at:{RESET} {link}')

def run(args):
    target_url = args.url
    if not target_url:
        error('Target URL (-u / --url) is required.')
        return 1
    if not target_url.startswith('http://') and (not target_url.startswith('https://')):
        target_url = 'http://' + target_url
    ignore_list = args.ignore if args.ignore else []
    scanner = WebScanner(target_url, links_to_ignore=ignore_list)
    if args.login_url and args.username and args.password:
        info(f'Authenticating against {args.login_url}...')
        login_data = {'username': args.username, 'password': args.password, 'Login': 'submit'}
        try:
            scanner.session.post(args.login_url, data=login_data, timeout=5)
            success('Authentication request submitted.')
        except Exception as e:
            warn(f'Authentication request failed: {e}')
    info(f'Crawling target application: {target_url}')
    scanner.target_links.append(target_url)
    try:
        scanner.crawl()
        print('\n' + '-' * 50)
        scanner.run_scanner()
        print('\n' + '=' * 50)
        if scanner.vulnerabilities_found > 0:
            warn(f'Assessment finished. Found {scanner.vulnerabilities_found} vulnerability instance(s).')
        else:
            success('Assessment finished. No reflected XSS vulnerabilities identified.')
        return 0
    except KeyboardInterrupt:
        warn('\nScan terminated by user.')
        return 130
