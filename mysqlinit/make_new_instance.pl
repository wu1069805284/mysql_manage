#!/usr/bin/env python
#
# Desc:
# make new mysqld instance
# 
# Change Logs:
# 1. 2016-01-07		init
#

import argparse
import sys
import os
import time
from commands   import getstatusoutput

BASEDIRPRE     = '/home/mysql/'
BASEDATADIRPRE = '/home/mysql/ssd/'
SCRIPTDIR      = '/opt/scripts/mysqlinit/'
TEMPCOFFILE    = SCRIPTDIR+'my_template.cnf'
serverid = int(time.time())

##-----------------------------------------------
# Parse the args info
##-----------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="the port")
    parser.add_argument("--innodbbuf", help="the innodb buffer size")
    parser.add_argument("--roles",help="master|slave")
#    parser.add_argument("--serverid", help="the mysqld server id")

    args = parser.parse_args()
    if args.port is None:
        print "ERROR: --port must specified"
        sys.exit(1)

    if args.innodbbuf is None:
        print "ERROR: --innodbbuf must specified"
        sys.exit(2)

    if args.roles is None:
	print "ERROR: --roles A role must be entered"
       	sys.exit(2)

    return args


def change_prv(path):
	cmd_priv="chown mysql. -R " + path
	os.system(cmd_priv)

def init_dir(portx):

    	basedir = BASEDIRPRE + "mysql_" + portx
    	datadir = BASEDATADIRPRE + "data_" + portx
 
    	## if the basedir and datadir is or not exist
	try:
    		if os.path.exists(basedir) or os.path.exists(datadir):
        		print "Warning: The Basedir or Datadir ",basedir," or ",datadir," is allready exist, Please Check."
        		sys.exit(3)
    		else:
        		## make the basedir.
        		os.makedirs(basedir)
        		## make the basedir/{logs|tmp}
			os.makedirs(basedir+"/etc")
        		os.makedirs(basedir+"/log")
        		os.makedirs(basedir+"/tmp")
        		## modify the privilege to mysql.
        		change_prv(basedir)
        		## make the datadir
        		os.makedirs(datadir)
			cmd = "tar -xvf " + SCRIPTDIR + "mysql5.6_data_file.tar.gz -C  " + datadir 
     			os.system(cmd)
       			## modify the privilege to mysql.
       			change_prv(datadir)
        		## make the soft link to ssd datadir
        		mksoftlink = "/usr/bin/ln -s " + datadir + "  " + basedir + "/data" 
        		os.system(mksoftlink)
	except Exception as err:
			print err
		


def make_conf( portx, buff, serverid ,roles):

    ## replace the port in template my.cnf to the real port.
    if roles == "master":
    	cmd = "/usr/bin/sed s'/PORT/"+portx +"/g' "  + TEMPCOFFILE + "| /usr/bin/sed s'/BUFFER_POOL/"+buff+"/g'" + "|/usr/bin/sed s'/read_only/read_only=0/g' " + " | /usr/bin/sed s'/SERVER_ID/"+str(serverid)+"/g'" + ">" + BASEDIRPRE + "mysql_" + portx + "/etc/my.cnf" 
    elif roles == "slave":
	cmd = "/usr/bin/sed s'/PORT/"+portx +"/g' "  + TEMPCOFFILE + "| /usr/bin/sed s'/BUFFER_POOL/"+buff+"/g'" + "|/usr/bin/sed s'/read_only/read_only=1/g' " + " | /usr/bin/sed s'/SERVER_ID/"+str(serverid)+"/g'" + ">" + BASEDIRPRE + "mysql_" + portx + "/etc/my.cnf"
    else:
	print "ERROR : The input role must be master or slave"
	sys.exit(2)

    base= BASEDIRPRE + "mysql_" + portx + "/*"
    change_prv(base)
    os.system(cmd)


def make_systemd_scripts(portx):
    server_file=SCRIPTDIR + "mysqld.server"
    systemdir = "/usr/lib/systemd/system/"
    systemfile = systemdir + "mysqld_" + portx + ".service"
    change_file="/usr/bin/cp -i %s %s" %(server_file,systemfile)
    change_port="/usr/bin/sed -i s'/PORT/%s/g' %s" %(portx,systemfile)
    if os.path.isfile(systemfile):
	print systemfile + " file existing"
	sys.exit(1)
    getstatusoutput(change_file)
    getstatusoutput(change_port)


def yum_cmd():
#    cmd_yummakechache = "/usr/bin/yum makecache fast"
    if os.path.exists("/usr/lib64/mysql/plugin") and os.path.isfile("/usr/sbin/mysqld"):
	os.popen("/usr/bin/yum makecache fast")
	os.popen("/usr/bin/yum -y install pv numactl lz4")
    else:
	os.popen("/usr/bin/yum makecache fast")
	os.popen("/usr/bin/yum -y install pv numactl lz4 mysql-community-server")	
#    	cmd_yuminsmysql   = "/usr/bin/yum -y install  mysql-community-server" 
#    cmd_yuminspv      = "/usr/bin/yum -y install pv"
#    cmd_yuminsnuma    = "/usr/bin/yum -y install numactl"
#    cmd_yuminslz4     = "/usr/bin/yum -y install lz4"

#    os.popen(cmd_yummakechache)
#    os.popen(cmd_yuminsmysql)
#    os.popen(cmd_yuminspv)
#    os.popen(cmd_yuminsnuma)
#    os.popen(cmd_yuminslz4)



if __name__ == '__main__':

    args = parse_args()
    yum_cmd()
    init_dir(args.port)
    make_conf(args.port, args.innodbbuf, serverid,args.roles)
    make_systemd_scripts(args.port)
