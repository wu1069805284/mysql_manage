#!/bin/env python
import os,sys,commands
from LogHandler import WriteLog 
from MySQLHandler import MySQLHandler
from ConfigParser import SafeConfigParser
from hacharm import check_status

Log=WriteLog()

def getConfig(section,key):
    try:
        main_path=os.getcwd().split('/mha_management')[0]
        cf='%s/mha_management/file/config.cfg'%(main_path)
        parser = SafeConfigParser()
        parser.read(cf)
        return parser.get(section,key)
    except Exception as err:
        Log.write('e',"getConfig: {}".format(err.message))


def cluster_info(ci):

    try:
        user=getConfig('user_con','mysql_user')
        host=getConfig('user_con','mysql_host')
        port=getConfig('user_con','mysql_port')
        pwd=getConfig('user_con','mysql_password')
        if ci == 'all':
            sql="select * from mha_list.mysql_cluster_info"
            conn=MySQLHandler(user,host,int(port),pwd)
            findinfo=conn.get_mysql_data(sql)
            return findinfo
        elif ci != 'all':
            sql="select * from mha_list.mysql_cluster_info where cluster_name='%s'"%(ci)
            conn=MySQLHandler(user,host,int(port),pwd)
            findinfo=conn.get_mysql_data(sql)
            return findinfo

    except Exception as err:
        Log.write('e',"cluster_info: {}".format(err.message))

def tb_info(ci):

    try:
        sql="select * from mha_list.mysql_table_list where cluster_name='%s'"%(ci)
        user=getConfig('user_con','mysql_user')
        host=getConfig('user_con','mysql_host')
        port=getConfig('user_con','mysql_port')
        pwd=getConfig('user_con','mysql_password')
        conn=MySQLHandler(user,host,int(port),pwd)
        findinfo=conn.get_mysql_data(sql)
        return findinfo


    except Exception as err:
        Log.write('e',"tb_info: {}".format(err.message))


def Account_connectivity(host,port):
    sql="select 1"

    ha_user=getConfig('user_cnf','ha_user')
    ha_pwd=getConfig('user_cnf','ha_password')
    ha_conn=MySQLHandler(ha_user,host,port,ha_pwd)
    ha_info=ha_conn.get_mysql_data(sql)
    if ha_info[0][0] == 1:
        hinfo="Mysql %s:%s node ha user connection is normal" %(host,port)
        Log.write('i',"Account_connectivity:{}".format(hinfo))

    repl_user=getConfig('user_cnf','repl_user')
    repl_pwd=getConfig('user_cnf','repl_password')
    repl_conn=MySQLHandler(repl_user,host,port,repl_pwd)
    repl_info=repl_conn.get_mysql_data(sql)
    if repl_info[0][0] == 1:
        rinfo="Mysql %s:%s node repl user connection is normal" %(host,port)
        Log.write('i',"Account_connectivity:{}".format(rinfo))

def master_dif(cname):
    sql="select @@read_only;"
    li=tb_info(cname)
    ml=[]
    for i in li:
        if i[5] == 'master': 
            ml.append(i[5])
            host=i[2]
            port=i[4]
    if len(ml) == 1:
        repl_user=getConfig('user_cnf','repl_user')
        repl_pwd=getConfig('user_cnf','repl_password')
        conn=MySQLHandler(repl_user,host,port,repl_pwd)
        info=conn.get_mysql_data(sql)
        if info[0][0] != 0:
            msg="%s The master instance read only exception"%(cname)
            Log.write('e',"master_dif:{}".format(msg))
            sys.exit(1)
    else:
        msg="%s cluster more than one master"%(cname)
        Log.write('e',"master_dif:{}".format(msg))
        sys.exit(1)


def check_masterbinlog(cname):
    sql="show global variables like 'log_bin_basename'"
    ha_user=getConfig('user_cnf','ha_user')
    ha_pwd=getConfig('user_cnf','ha_password')
    tab_info=tb_info(cname) 
    for item in tab_info:
        if item[5] == 'master': 
            host=item[2]
            port=int(item[4])
            p_conn=MySQLHandler(ha_user,host,port,ha_pwd)
            variable_path=p_conn.get_mysql_data(sql)
            return variable_path


def find_vip(cname):
    vip_info=cluster_info(cname)
    return  vip_info[0][2]


def status_list(item):
    cn=cluster_info(item)
    for v in cn:
        cname=v[1]
        status_list=check_status(cname)
        print status_list    






