#!/usr/bin/env python
#coding=utf-8
#create by wuweijian

import sys,os,time
from ConfigParser import ConfigParser

arg=sys.argv[1:]
Old_host=arg[0]
Old_port=arg[1]
New_host=arg[2]
New_port=arg[3]
proxy_path=arg[4]

def main():
    parser=ConfigParser()
    parser.read(proxy_path)
    s=parser.sections()
    for tital in  s:
        if 'host' in parser.options(tital) and \
            'cluster_name' in parser.options(tital) and\
                 Old_host == parser.get(tital,'host') and\
                    Old_port == parser.get(tital,'port'):
            parser.set(tital,'host',New_host)
            parser.set(tital,'port',New_port)
            with open(proxy_path,'wb') as config_file:
                parser.write(config_file)


main()
