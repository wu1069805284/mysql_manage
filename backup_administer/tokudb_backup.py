#!/usr/bin/env python
#coding=utf-8
#create by wuweijian

import socket,re,os,sys,types,MySQLdb
import datetime,time,commands,logging


class WriteLog(object):

	def write(self,log_lev,log_msg):
		logging.basicConfig(level=logging.DEBUG,
		format='%(asctime)s [%(levelname)s] %(message)s',
		datefmt='%Y-%m-%d %X',
		filename='/opt/tokudb_backup.log',
		filemode='a')

		if log_lev == 'i':
			logging.info(log_msg)
		elif log_lev == 'e':
			logging.error(log_msg)

class MySQLbackup(object):
	def __init__(self):
		self.bakuser = 'dbaeye'
		self.bakpass = 'NicePrivate@2015'
		self.localhost = '127.0.0.1'
		self.remotehost = '10.10.10.198'
		self.remoteport = 3306
		self.log = WriteLog()
		_failed_times = 0
 		while True:
     			try:

				self.remotedb = MySQLdb.connect(host=self.remotehost,\
				port=self.remoteport,user=self.bakuser,passwd=self.bakpass)
				self.remotedb.autocommit(1)
				self.remotecursor = self.remotedb.cursor()

     			except Exception as err:
         			_failed_times += 1
         			if _failed_times >= 3:
             				self.log.write('e',err)
         			else:
             				continue
     			break

	def get_ip_address(self):
		try:
			hostname = socket.gethostname()
			return socket.gethostbyname(hostname)
		except Exception as err:
			self.log.write("e","get_ip_address:{}".format(err.message))	
	def get_hostname(self):
		try:
			return socket.gethostname()
		except Exception as err:
			self.log.write("e","get_hostname:{}".format(err.message))		

	def get_mysqld_ports(self):
		try:
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
		except Exception as err:
			self.log.write("e","get_mysqld_ports:{}".format(err.message))

	def get_datadir(self,port):
		try:
			self.localdb = MySQLdb.connect(host=self.localhost,\
                                	port=port,user=self.bakuser,passwd=self.bakpass)       
                        self.localcursor = self.localdb.cursor()
			sql  = "SELECT @@tokudb_data_dir"
			self.localcursor.execute(sql)
			res = self.localcursor.fetchall()
			datadir = res[0][0]
			self.localcursor.close()
			return datadir
		except Exception as err:
			self.log.write("e","get_datadir:{}".format(err.message))

	def currenttime(self):
			now = datetime.datetime.now()
			ymd = now.strftime("%Y-%m-%d %H:%M:%S")
			return str(ymd)

	def currentdate(self):
			now = datetime.datetime.now()
			ymd = now.strftime("%Y-%m-%d")
			return str(ymd)
		
	def get_data_size(self,dirs):
			cmd = 'du -shL ' + dirs
			size = os.popen(cmd).read().strip('\n').split('\t')
			return size[0]

	def insert_datadir_size(self):
		try:
			portlist = self.get_mysqld_ports()
			localip = self.get_ip_address()	
			hostname = socket.gethostname()			
			gmtcreate = self.currenttime()
			gmtdate   = self.currentdate()

			for portx in portlist:
				dirname = self.get_datadir(int(portx))
				dirsize = self.get_data_size(dirname)
				sql = '''INSERT INTO  db_stats.db_datadir_size (hostname,ip,port,\
				dirname,dirsize,collect_date,gmt_create) VALUES("%s","%s",\
				%d,"%s","%s","%s","%s") ON DUPLICATE KEY UPDATE gmt_create="%s"'''\
				 % (hostname,localip,int(portx),dirname,dirsize,gmtdate,gmtcreate,gmtcreate)
				self.remotecursor.execute(sql)

		except Exception as err:
			self.log.write("e","insert_datadir_size:{}".format(err))


	def backup_isornot(self,portx):
		try:
			hostname = socket.gethostname()
			sql='''SELECT backup FROM db_stats.db_meta WHERE host="%s" \
				AND port=%d ''' %(hostname,portx)
			self.remotecursor.execute(sql)
			result = self.remotecursor.fetchall()
			return int(result[0][0])				
	
		except Exception as err:
			self.log.write("e","backup_isornot:{}".format(err))

	def master_or_slave(self,portx):

		try:
			localport = int(portx)
			self.localdb = MySQLdb.connect(host=self.localhost,\
                                        port=localport,user=self.bakuser,passwd=self.bakpass)
                        self.localcursor = self.localdb.cursor()
			sql = "SELECT @@READ_ONLY"
			self.localcursor.execute(sql)
			result = self.localcursor.fetchall()
			self.localcursor.close()
			return int(result[0][0])	

		except Exception as err:
			self.log.write("e","master_or_slave:{}".format(err))

	def get_db_names(self,portx):
		try:	
			self.localdb = MySQLdb.connect(host=self.localhost,\
                                        port=portx,user=self.bakuser,passwd=self.bakpass)
                        self.localcursor = self.localdb.cursor()		
			filters = [
                  			'information_schema',
                  			'mysql',
                  			'performance_schema',
                  			'test'
              				]

    			dbnames = ''
			sql = "SHOW DATABASES"
			self.localcursor.execute(sql)
			result = self.localcursor.fetchall()
			self.localcursor.close()
			for x in result:
				if x[0] not in filters:
					dbnames += x[0]
					dbnames += '|'
			dbs = dbnames.rstrip('|')
			return dbs

		except Exception as err:
			self.log.write("e","get_db_names:{}".format(err))

	def get_master_info(self,portx):
		try:
			sql = "SHOW SLAVE STATUS"
			self.localdb = MySQLdb.connect(host=self.localhost,\
                                        port=portx,user=self.bakuser,passwd=self.bakpass)
                        self.localcursor = self.localdb.cursor()
			self.localcursor.execute(sql)
			result=self.localcursor.fetchall()			

			if (result):
        			masterinfo = str(result[0][1]) + ':' + str(result[0][3])
    			else:
        			masterinfo = ''
    			return masterinfo
		
		except Exception as err:
			self.log.write("e","get_master_info:{}".format(err))

	def get_cluster_name(self,dbname):
		try:
			sql = " select groupname from db_stats.db_groups_meta where \
					dbtype='%s' and dbname='%s' " % ('mysql',dbname)
			self.remotecursor.execute(sql)
			result = self.remotecursor.fetchall()
			return result[0][0]

		except Exception as err:
			self.log.write("e","get_cluster_name:{}".format(err))

	def tokudb_check_engine(self,portx):
		try:
			self.localdb = MySQLdb.connect(host=self.localhost,\
                                        port=portx,user=self.bakuser,passwd=self.bakpass)
			self.localcursor = self.localdb.cursor()
			default_engine="select ENGINE from information_schema.ENGINES where SUPPORT='DEFAULT' "
			self.localcursor.execute(default_engine)	
			result = self.localcursor.fetchall()
			self.localcursor.close()
			return str(result[0][0])

		except Exception as err:
			self.log.write("e","tokudb_check_engine:{}".format(err))

	def tokudb_slave_restart(self,portx,value):
		try:
			self.localdb = MySQLdb.connect(host=self.localhost,\
                                        port=portx,user=self.bakuser,passwd=self.bakpass)
                        self.localcursor = self.localdb.cursor()
			start = "start slave"
			stop = "flush tables;flush logs;stop slave;"
			if value == 'start':
				self.localcursor.execute(start)	
				self.localcursor.close()
				return 1
			elif value == 'stop':
				self.localcursor.execute(stop)
				self.localcursor.close()
				return 0
			else:
				self.log.write("e","tokudb_slave_restart: port %s Abnormal operation " %(portx))
				sys.exit(1)
		except Exception as err:
			self.log.write("e","tokudb_slave_restart:{}".format(err))



	def tokudb_backup(self):
		try:
			portlist = self.get_mysqld_ports()
        		hostname = self.get_hostname()
        		localip = self.get_ip_address()
        		gmtdate   = self.currentdate()
        		for portx in portlist:
                		masterORslave = self.master_or_slave(int(portx))
                		backupisORnot = self.backup_isornot(int(portx))
                		dbnames = self.get_db_names(int(portx))
                		dirname = self.get_datadir(int(portx))
                		dirsize = self.get_data_size(dirname)
                		clustername = self.get_cluster_name(str(dbnames))
                		masterinfo = self.get_master_info(int(portx))
				engine = self.tokudb_check_engine(int(portx))
                		remotedir = '/home/data/mysql/'
                		remotedir += gmtdate
                		remotedir += '/'
                		remotedir += clustername
                		remotedir += '/'

                		backupdir = 'blog05:'+remotedir
				if ( masterORslave==1 and backupisORnot==1 and engine == 'TokuDB' ):

					msg="Start Backup Instance: %s:%s at %s" \
							 % (hostname, portx,self.currenttime())
					self.log.write("i",msg)

					sql1 = '''INSERT INTO db_stats.db_backup_history (backdate,dbtype,dbnames,hostname,ip,port,masterinfo,dbsizes,backtype,status,starttime,endtime,backupdir) \
                   VALUES("%s", "%s", "%s", "%s", "%s", %d, "%s", "%s", "%s", %d, now(), "%s", "%s") ON DUPLICATE KEY UPDATE status=%d, starttime=now() ''' % \
                   (gmtdate, 'MySQL', dbnames, hostname, localip, int(portx), masterinfo, dirsize, 'TokuDB_backup', 1, '0000-00-00 00:00:00','', 1)

					sql2 = ''' UPDATE db_stats.db_backup_history SET status=%d , endtime=now(), backupdir="%s" WHERE backdate="%s" AND dbtype="%s" AND dbnames="%s" ''' % \
                       (2,backupdir, gmtdate, 'MySQL', dbnames)

					self.tokudb_slave_restart(int(portx),'stop')

					cmd0  = '''/home/hdclient/hadoop/bin/hdfs dfs -mkdir -p /opbak/mysql/'''
            				cmd0 += gmtdate
            				cmd0 += "/"
            				cmd0 += clustername
					os.popen(cmd0)

					bakcmd = "cd /home/mysql/ssd/ ;"
					bakcmd += "tar cv tokudb_"
					bakcmd += portx
					bakcmd += "|pigz -6 -p 10 -k | /home/hdclient/hadoop/bin/hdfs dfs \
						-put -  /opbak/mysql/"
					bakcmd += gmtdate
					bakcmd += '/'
					bakcmd += clustername
					bakcmd += '/'
					bakcmd += clustername
					bakcmd += '_tokudb.tar.gz.pz'
					self.remotecursor.execute(sql1)
					(status, output) = commands.getstatusoutput(bakcmd)
					if status != 0 :
						msg="Backup Instance:%s:%s Failed %s" % (hostname,portx,output)
						self.log.write("e",msg)	
						self.tokudb_slave_restart(int(portx),'start')
						sys.exit(1)
					else:
						self.remotecursor.execute(sql2)
						msg="Complete Backup Instance: %s:%s at %s"\
							% (hostname, portx, self.currenttime())
						self.log.write("i",msg)
						self.tokudb_slave_restart(int(portx),'start')
				else:
					msg="Not backup on this instance or engine not tokudb:  %s:%s" \
					% (hostname,portx)
					self.log.write("e",msg)

		except Exception as err:
			self.log.write("e","tokudb_backup:{}".format(err))


	def close_connection(self):
		self.remotecursor.close()	



if __name__ == '__main__':

	backup_class=MySQLbackup()
	backup_class.tokudb_backup()	
	backup_class.insert_datadir_size()
	backup_class.close_connection()
