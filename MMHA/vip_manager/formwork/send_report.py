#!/usr/bin/env python
#-*- encoding:utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        send_report.py
#----------------------------------------------
import os
import sys
import time
import datetime
import smtplib
import subprocess
import fileinput
import getopt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.Utils import COMMASPACE, formatdate

reload(sys)
sys.setdefaultencoding('utf8')

def send_mail(to, subject, text, from_mail, server="localhost"):
    message = MIMEMultipart()
    message['From'] = from_mail
    message['To'] = COMMASPACE.join(to)
    message['Date'] = formatdate(localtime=True)
    message['Subject'] = subject
    message.attach(MIMEText(text,_charset='utf-8'))
    smtp = smtplib.SMTP(server)
    smtp.sendmail(from_mail, to, message.as_string())
    smtp.close()

if __name__ == "__main__":
    opts,args = getopt.getopt(sys.argv[1:],"h",["orig_master_host=","new_master_host=","new_slave_hosts=","conf=","subject=","body=","app_vip=","new_master_ssh_port=","ssh_user="])
#    print opts,args
    for lines in opts:
        key,values = lines
        if key == '--orig_master_host':
            orig_master_host = values
        if key == '--new_master_host':
            new_master_host = values
        if key == '--new_slave_hosts':
            new_slave_hosts = values
        if key == '--subject':
            subject = values
        if key == '--body':
            body = values
#    text = sys.stdin.read()
    mail_list = ['zjy@xxx.com']
    send_mail(mail_list, subject.encode("utf8"), body, "MHA_Monitor@smtp.dxy.cn", server="192.168.220.251")
