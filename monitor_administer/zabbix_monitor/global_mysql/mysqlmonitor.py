#!/usr/bin/env python
#coding=utf8

import MySQLdb
from optparse import OptionParser



def get_cli_options():
	parser = OptionParser(usage="usage: python %prog [options]",
                              description="""Desc: Show mysql status""")

	parser.add_option("-H", "--host",
                         dest="host",
                         default="127.0.0.1",
                         metavar="HOST",
                         help="Mysql host")
        parser.add_option("-p", "--port",
                         dest="port",
                         default=3306,
                         metavar="PORT",
                         help="Mysql port")
	parser.add_option("-t", "--item",
			 dest="item",
			 metavar="ITEM",
			 help="Mysql item")


	(options, args) = parser.parse_args()
	return options


def check_slave():
	options=get_cli_options()
	sql_slave_status = "SHOW SLAVE STATUS"
	sql_slave_readonly = "SELECT @@READ_ONLY"
	try:
		conn = MySQLdb.connect(host = options.host,
                         port = int(options.port),
                         user = 'zabbix_moniter',
                         passwd = '123456',
                         charset = 'UTF8',
                         connect_timeout = 4)
		curs = conn.cursor()
		curs.execute(sql_slave_status)
		ls=curs.fetchall()
		curs.execute(sql_slave_readonly)
		rs=curs.fetchall()
		rr=int(rs[0][0])
 
		if not ls and rr == 1:
			return 2
		elif ls and rr != 1:
			return 1
		elif ls and rr == 1 or not ls and rr != 1:	
			return 0

	except MySQLdb.Error,e:
		print "MySQLdb Error",e

if __name__ == '__main__':
	option = get_cli_options() 
	openfile="/tmp/" + option.host + "-mysql_2.0_stats.txt_" + option.port
	value=check_slave()
	kv = str(' zz:' + '%s') %(value)
	a=open(openfile, 'a')
	a.write(kv)
	a.close




