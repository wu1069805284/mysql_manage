#!/usr/bin/env python

from prettytable import PrettyTable
from optparse import OptionParser
import MySQLdb,sys 


def get_cli_options():
    parser = OptionParser(usage="usage: python %prog [options]",
            description="""Desc: Show collections status""")

    parser.add_option("-H", "--host",
                        dest="host",
                        metavar="HOST",
                        help="MYSQL host")
    parser.add_option("-p", "--port",
                        dest="port",
                        metavar="PORT",
                        help="MYSQL port")
    parser.add_option("-i", "--item",
                        dest="item",
                        metavar="ITEM",
                        help="info|count")

    (options, args) = parser.parse_args()
    if not options.host or not options.port:
        parser.error("incorrect number of arguments")

    return options


def get_client_info(host, port ,sql):

    try:
        username=''
        password=''
        gport=int(port)
        con_db = MySQLdb.connect(host=host,port=gport,user=username,passwd=password)
        dbcur = con_db.cursor()
        dbcur.execute(sql)
        sql_data = dbcur.fetchall()
        return sql_data

    except MySQLdb.OperationalError as e:
        print e


def connected_info(options):
    global_sql="select concat(USER,':',substring_index(host,':',1)) as \
            usercount,DB,COMMAND,INFO,TIME from information_schema.PROCESSLIST \
            where INFO is not NULL and user not in ('detecting')"
    info=get_client_info(options.host,options.port,global_sql)
    x = PrettyTable(["Connected_userhost",\
            "Connected_DB", "Connected_time","Connected_status","Connected_info"])
    x.align["Connected_uh"] = "l"
    x.align["Connected_DB"] = "l"
    x.align["Connected_status"] = "l"
    x.align["Connected_info"] = "l"
    x.align["Connected_time"] = "l"
    x.padding_width = 1
    if not info:
        print "There is no running connection"
    else:
        for option in info:
                x.add_row([option[0],option[1],option[4],option[2],option[3]])
                print x

def connected_count(options):
    count_sql="select concat(USER,':',substring_index(host,':',1)) as \
            usercount ,count(*) as c from information_schema.processlist \
            where user not in ('detecting','root','system user','dbsync','dbaeye')\
            group by usercount order by c"
    info=get_client_info(options.host,options.port,count_sql)
    table = PrettyTable(["Connected_userhost","Connected_number"])
    table.align["Connected_userhost"] = "l"
    table.align["Connected_number"] = "l"
    table.padding_width = 1

    for i in info:
        table.add_row([i[0],i[1]])

    print table 


if __name__ == '__main__':
    options=get_cli_options()
    if options.item == 'info':
        connected_info(options)
    elif options.item == 'count':
        connected_count(options)
    else:
        msg="%s:%s Not specified item"%(options.host,options.port)
        print msg
        sys.exit(1)
