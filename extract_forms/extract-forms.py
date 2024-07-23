#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup
import urllib.parse

def request(url):
    try:
        return requests.get(url)
    except requests.exceptions.ConnectionError:
        pass
target_url = 'http://192.168.1.22/mutillidae/index.php?page=dns-lookup.php'
response = request(target_url)
parsed_html = BeautifulSoup(response.content, features='lxml')
forms_lists = parsed_html.findAll('form')
for form in forms_lists:
    action = form.get('action')
    post_url = urllib.parse.urljoin(target_url, action)
    method = form.get('method')
    inputs_list = form.findAll('input')
    post_data = {}
    for input in inputs_list:
        input_name = input.get('name')
        input_type = input.get('type')
        input_value = input.get('value')
        if input_type == 'text':
            input_value = 'YousseffMohamed'
        post_data[input_name] = input_value
    result = requests.post(post_url, data=post_data)
    print(result.content.decode('utf-8'))
