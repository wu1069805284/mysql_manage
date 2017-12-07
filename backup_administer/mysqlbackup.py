#!/usr/bin/env python

import socket
import fcntl
import struct
import re
import os
import types
#import pymysql
import MySQLdb
import datetime
import time
import commands


## 1. Get the all mysql instance information;
## 2. Get the all instance datadir size and store
##    on db_stats.mysql_datasize table;
## 3.



## Get the ip addr.
def get_ip_address():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)


## Get the backport used for nc copy files to remote host.
def get_backport_by_ip(portx):
    localip=get_ip_address()
    ## use the last two ip sections as port
    ## etc: 10.10.10.23 to port is 1023
    p = re.compile(r'\.')
    result = p.split(localip)
    backport = str(result[2])+str(result[3])
    return int(backport)+int(portx)

## Get all mysql instance port on this host.
def get_mysqld_ports():
   cmd = "/usr/sbin/ss -ntl|awk '{print $4}' |grep ':3[0-9][0-9][0-9]$'"
   result = os.popen(cmd).read().strip('\n')
   tmplist = result.split('\n')   
   p = re.compile(r'\d+')
   portlist = []
   for x in tmplist:
       match = p.search(x)
       if match:
           port = match.group()
           portlist.append(port)
   
   return portlist
 
## Get the data dir addr.
def get_datadir(portx):
    dbaddr = '127.0.0.1'
    dbuser = ''
    dbpass = ''

    #conn = pymysql.connect(host=dbaddr, port=int(portx), user=dbuser, passwd=dbpass)
    conn = MySQLdb.connect(host=dbaddr, port=int(portx), user=dbuser, passwd=dbpass)
    curs = conn.cursor()
    sql  = "SELECT @@DATADIR"
    curs.execute(sql)
    res = curs.fetchall()
    datadir = res[0][0]
    curs.close()
    conn.close()
     
    return datadir

def currenttime():
    now = datetime.datetime.now()
    ymd = now.strftime("%Y-%m-%d %H:%M:%S")
    return str(ymd)


def currentdate():
    now = datetime.datetime.now()
    ymd = now.strftime("%Y-%m-%d")
    return str(ymd)

## Get the data dir size and insert into mysql tables.
def get_data_size(dirs):
    cmd = 'du -shL ' + dirs
    size = os.popen(cmd).read().strip('\n').split('\t')

    return size[0]
        

def insert_datadir_size():
    portlist = get_mysqld_ports()
    remotehost = ''
    remoteuser = ''
    remotepass = ''
    remoteport = 3306

    localip=get_ip_address()
    hostname = socket.gethostname()
    gmtcreate = currenttime()
    gmtdate   = currentdate()

    for portx in portlist:
        dirname = get_datadir(portx)     
        dirsize = get_data_size(dirname)
        conn = MySQLdb.connect(host=remotehost, port=int(remoteport), user=remoteuser, passwd=remotepass, db="db_stats", charset="utf8")
        curs = conn.cursor()
        sql = '''INSERT INTO  db_datadir_size (hostname,ip,port,dirname,dirsize,collect_date,gmt_create) \
               VALUES("%s","%s",%d,"%s","%s","%s","%s") ON DUPLICATE KEY UPDATE gmt_create="%s"''' % (hostname, localip, int(portx), dirname, dirsize, gmtdate, gmtcreate, gmtcreate)

        curs.execute(sql) 
        conn.commit()
        curs.close()
        conn.close()

## collect the mysql datadir and size info.
insert_datadir_size()


def backup_isornot(portx):
    remotehost = ''
    remoteuser = ''
    remotepass = ''
    remoteport = 3306

    portlist = get_mysqld_ports()
    hostname = socket.gethostname()
    conn = MySQLdb.connect(host=remotehost, port=int(remoteport), user=remoteuser, passwd=remotepass, db="db_stats", charset="utf8")
    curs = conn.cursor()

    sql = '''SELECT backup FROM db_meta WHERE host="%s" AND port=%d ''' % (hostname, portx )
    curs.execute(sql)
    result = curs.fetchall()

    curs.close()
    conn.close()

    return int(result[0][0])

def get_conf_file(portx):
    localhost = '127.0.0.1'
    localuser = ''
    localpass = ''
    localport = int(portx) 

    conn = MySQLdb.connect(host=localhost, port=localport, user=localuser, passwd=localpass, charset='utf8')
    curs = conn.cursor()

    sql = "SELECT @@DATADIR"
    curs.execute(sql)
    result = curs.fetchall()
    
    curs.close()
    conn.close()
    
    confile = result[0][0].replace('/data/','')
    return confile

def master_or_slave(portx):
    localhost = '127.0.0.1'
    localuser = ''
    localpass = ''
    localport = int(portx) 

    conn = MySQLdb.connect(host=localhost, port=localport, user=localuser, passwd=localpass, charset='utf8')
    curs = conn.cursor()

    sql = "SELECT @@READ_ONLY"
    curs.execute(sql) 
    result = curs.fetchall()

    curs.close()
    conn.close()

    return int(result[0][0])

def get_slave_parallel_workers(portx):
    localhost = ''
    localuser = ''
    localpass = ''
    localport = int(portx)

    conn = MySQLdb.connect(host=localhost, port=localport, user=localuser, passwd=localpass, charset='utf8')
    curs = conn.cursor()

    sql = "SELECT @@slave_parallel_workers"
    curs.execute(sql)
    result = curs.fetchall()
   
    curs.close()
    conn.close() 

    return int(result[0][0]) 

def set_slave_parallel_workers(portx, num):
    localhost = '127.0.0.1'
    localuser = ''
    localpass = ''
    localport = int(portx)
    nums      = int(num)

    conn = MySQLdb.connect(host=localhost, port=localport, user=localuser, passwd=localpass, charset='utf8')
    curs = conn.cursor()

    sql = "SET GLOBAL slave_parallel_workers=%d" % (nums)
    curs.execute(sql)
    conn.commit()
    curs.close()
    conn.close()


def get_db_names(portx):
    localhost = '127.0.0.1'
    localuser = ''
    localpass = ''
    localport = int(portx)
    
    filters = [
                  'information_schema',
                  'mysql',
                  'performance_schema',
                  'test'
              ]

    dbnames = ''
     
    conn = MySQLdb.connect(host=localhost, port=localport, user=localuser, passwd=localpass, charset='utf8')
    curs = conn.cursor()
 
    sql = "SHOW DATABASES"
    curs.execute(sql) 
    result = curs.fetchall()
    for x in result:
        if x[0] not in filters:
            dbnames += x[0]
            dbnames += '|'
    dbs = dbnames.rstrip('|')
    return dbs

def get_master_info(portx):
    localhost = '127.0.0.1'
    localuser = ''
    localpass = ''
    localport = int(portx)

    conn = MySQLdb.connect(host=localhost, port=localport, user=localuser, passwd=localpass, charset='utf8')
    curs = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    sql = "SHOW SLAVE STATUS"
    curs.execute(sql)
    result = curs.fetchall()

    if (result):
        masterinfo = str(result[0]['Master_Host']) + ':' + str(result[0]['Master_Port'])
    else:
        masterinfo = ''
    return masterinfo


def get_cluster_name(dbnames):
    remotehost = ''
    remoteuser = ''
    remotepass = ''
    remoteport = 3306 

    conn = MySQLdb.connect(host=remotehost, port=int(remoteport), user=remoteuser, passwd=remotepass, db="db_stats", charset="utf8")
    curs = conn.cursor()
    sql = ''' select groupname from db_groups_meta where dbtype="%s" and dbname="%s" ''' % ('mysql', dbnames)
    curs.execute(sql)
    result = curs.fetchall()
    curs.close()
    conn.close()
    
    return result[0][0]


def backup_main():
    portlist = get_mysqld_ports()
    hostname = socket.gethostname()
    localip=get_ip_address()
   
    gmtcreate = currenttime()
    gmtdate   = currentdate()

    remotehost = ''
    remoteuser = ''
    remotepass = ''
    remoteport = 3306
    
    for portx in portlist:
        masterORslave = master_or_slave(int(portx))
        backupisORnot = backup_isornot(int(portx))
        confile = get_conf_file(int(portx))
        dbnames = get_db_names(int(portx))
        dirname = get_datadir(portx)
        dirsize = get_data_size(dirname)
        clustername = get_cluster_name(dbnames)
        masterinfo = get_master_info(int(portx))
       
        remotedir  = '/home/data/mysql/'
        remotedir += gmtdate
        remotedir += '/'
        remotedir += clustername
        remotedir += '/'

        backupdir = 'blog05:'+remotedir

        if ( masterORslave==1 and backupisORnot==1 ):
            print "### Start Backup Instance: %s:%s at %s"  % (hostname, portx, gmtcreate)
            conn = MySQLdb.connect(host=remotehost, port=int(remoteport), user=remoteuser, passwd=remotepass, db="db_stats", charset="utf8")
            curs = conn.cursor()
            nows = currenttime()
            sql1 = '''INSERT INTO db_backup_history (backdate,dbtype,dbnames,hostname,ip,port,masterinfo,dbsizes,backtype,status,starttime,endtime,backupdir) \
                   VALUES("%s", "%s", "%s", "%s", "%s", %d, "%s", "%s", "%s", %d, "%s", "%s", "%s") ON DUPLICATE KEY UPDATE status=%d, starttime="%s" ''' % \
                   (gmtdate, 'MySQL', dbnames, hostname, localip, int(portx), masterinfo, dirsize, 'Xtrabackup', 1, nows, '0000-00-00 00:00:00','', 1, nows)       
            curs.execute(sql1)
            conn.commit()
            curs.close()
            conn.close()            

            slave_parallel_workers_old = get_slave_parallel_workers(portx)
            if (slave_parallel_workers_old > 0): 
                set_slave_parallel_workers(portx,0) 

	    
            cmd0  = '''/home/hdclient/hadoop/bin/hdfs dfs -mkdir -p /opbak/mysql/'''
            cmd0 += gmtdate
            cmd0 += "/"
            cmd0 += clustername
            
           
    
            os.popen(cmd0)
            
            #cmd  = "''"
            cmd = '/usr/bin/innobackupex --defaults-file='
            cmd += confile+'/my.cnf '
            #cmd += ' --slave-info  --tmpdir=/tmp --stream=tar --user=nicebackup  --password=Nice2015Backup --host=127.0.0.1 /tmp/ | lz4 -B4 |pv -q -L40m | ssh root@blog05 "cat - > /home/data/mysql/'
            cmd += ' --slave-info --parallel=24  --tmpdir=/tmp --stream=tar --user=nicebackup  --password=Nice2015Backup --host=127.0.0.1 /tmp/ | /usr/bin/lz4 -B4 |/usr/bin/pv -q -L40m | /home/hdclient/hadoop/bin/hdfs dfs -put - /opbak/mysql/'
            cmd += gmtdate
            cmd += '/'
            cmd += clustername
            cmd += '/'
            cmd += clustername
            cmd += '.tar.gz.lz4'
            #cmd += "''"
           
            (status, output) = commands.getstatusoutput(cmd)

            if (slave_parallel_workers_old > 0):
                set_slave_parallel_workers(portx,slave_parallel_workers_old)

            ## record the output into logfile
            os.popen('mkdir -p /tmp/xtrabackuplogs/')
            logfilename  = '/tmp/xtrabackuplogs/xtrabackup_'
            logfilename += portx
            logfilename += '_'
            logfilename +=gmtdate
            
            
            FH = open( logfilename, 'w')
            FH.write(output)
            FH.close()
            
            cmdx  = 'tail -20 ' 
            cmdx += logfilename
            cmdx += '| grep -c "innobackupex: completed OK!"'
            isok = os.popen(cmdx).read()         
       
            if (int(isok) == 1):
            
                ## Complete the backup and store to blog05
                conn = MySQLdb.connect(host=remotehost, port=int(remoteport), user=remoteuser, passwd=remotepass, db="db_stats", charset="utf8")
                curs = conn.cursor()
                sql2 = ''' UPDATE db_backup_history SET status=%d , endtime="%s", backupdir="%s" WHERE backdate="%s" AND dbtype="%s" AND dbnames="%s" ''' % \
                       (2, currenttime(), backupdir, gmtdate, 'MySQL', dbnames)
                curs.execute(sql2)
                conn.commit()
                curs.close()
                conn.close()
            
                print "### Complete Backup Instance: %s:%s at %s" % (hostname, portx, gmtcreate)
            else:
                print "### Error: Backup Instance:%s:%s Failed." % (hostname, portx)

        else:
            print "### Not backup on this instance:  %s:%s" % (hostname,portx)

backup_main()
