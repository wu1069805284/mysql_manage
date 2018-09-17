#!/usr/local/bin/python
#coding=utf-8
import MySQLdb,time
from  LogHandler import WriteLog


class MySQLHandler(object):
    def __init__(self,user,host,port,password):
	    self.Log = WriteLog()
	    self.user = user
	    self.host = host        
	    self.port = port
	    self.pw = password
            try:
                self.con_db = MySQLdb.connect(host=self.host,port=self.port,user=self.user,passwd=self.pw)
                self.con_db.autocommit(1)
                self.cursor = self.con_db.cursor()
            except Exception as e:
                log_msg = " %s:%s %s" % (self.host,self.port,e)
                self.Log.write('e',log_msg)


    def reconnect(self):
        _failed_times = 0
        while True:
            try:
                itime=True
                self.con_db = MySQLdb.connect(host=self.host,port=self.port,user=self.user,passwd=self.pw)
                self.con_db.autocommit(1)
                self.cursor = self.con_db.cursor()
                return itime
            except Exception as e:
                _failed_times += 1
                time.sleep(1) 
                if _failed_times >= 3:
                    itime=False
                    return itime
                    log_msg = "reconnect %s:%s %s" % (self.host,self.port,e)
                    self.Log.write(log_msg)
                else:
                    continue
            break


    def get_mysql_data(self,sql):
        try:
            self.cursor.execute(sql)
            sql_data = self.cursor.fetchall()
            return sql_data
        except MySQLdb.OperationalError as e:
            if 2006 == e.args[0]:
                self.reconnect()
                try:
                    self.cursor.execute(sql)
                    sql_data = self.cursor.fetchall()
                    return sql_data
                except MySQLdb.Error as e1:
                    print e1.args[1]
                    log_msg = "get_mysql_data %s:%s %s" % (self.host,self.port,e1)
                    self.Log.write('e',log_msg)
                    return 0
            else:
                print e.args[1]
                log_msg = "get_mysql_data %s:%s %s" % (self.host,self.port,e)
                self.Log.write('e',log_msg)
                return 0
        except MySQLdb.Error as e2:
            print e2.args[1]
            log_msg = "get_mysql_data %s:%s %s" % (self.host,self.port,e2)
            self.Log.write('e',log_msg)
            return 0
        except Exception as e3:
            log_msg = "get_mysql_data %s:%s %s" % (self.host,self.port,e3)
            self.Log.write('e',log_msg)
            return 0
   

    def execute_sql(self,sql):
        try:
            self.cursor.execute(sql)
            self.con_db.autocommit(1)
            self.close_connection()
            status = 1
        except  MySQLdb.OperationalError as e:
            self.Log.write('e',e)
            if 2006 == e.args[0]:
                self.reconnect()
                try:
                    self.cursor.execute(sql)
                    status = 1
                except MySQLdb.Error as e1:
                    print e1.args[1]
                    log_msg = "execute_sql %s:%s %s" % (self.host,self.port,e1)
                    self.Log.write('e',log_msg)
                    status = 0
            else:
                print e.args[1]
                log_msg = "execute_sql %s:%s %s" % (self.host,self.port,e)
                self.Log.write('e',log_msg)
                status = 0
        except  MySQLdb.Error as e2:
            print e2.args[1]
            log_msg = "execute_sql %s:%s %s" % (self.host,self.port,e2)
            self.Log.write('e',log_msg)
            status = 0
        except Exception as e3:
            log_msg = "execute_sql %s:%s %s" % (self.host,self.port,e3)
            self.Log.write('e',log_msg)
            status = 0
        finally:
            return status



    def close_connection(self):
        self.con_db.close()
