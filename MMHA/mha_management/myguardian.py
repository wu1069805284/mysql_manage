#!/usr/bin/env python
#coding=utf-8
#create by wuweijian

from lib.detection import *
from lib.LogHandler import WriteLog 
from lib.operation import ssh_key
from lib.MySQLHandler import MySQLHandler
from lib.wechat import minwechat
from ConfigParser import ConfigParser
import logging,os,sys,time,json,multiprocessing

Log=WriteLog()

class Producer(multiprocessing.Process):
    def __init__(self, queue):
        multiprocessing.Process.__init__(self)
        self.queue = queue
        self.cmysql_info=cluster_info('all')     


    def get_mysql(self):
        cl_list=[]
        for i in  self.cmysql_info:
            cl_list.append((i))
        return cl_list


    def run(self):
        while True:
            uid=self.get_mysql()
            if uid == []:
                uid='NULL'
            self.queue.put(uid)
            time.sleep(10)      



class Consumer(multiprocessing.Process):
    def __init__(self, queue):
        multiprocessing.Process.__init__(self)
        self.queue = queue
        self.main_path=os.getcwd().split('/mha_management')[0]

    def mydes(self,cname):
        try:
            msql="select * from db_cmdb.ha_mysql_table_list \
                where role='master' and cluster_name='%s' " %(cname)
            readsql="select @@read_only"
            csql="select 1"
            mlist=get_mdb(msql)
            for minfo in mlist: 
                host=minfo[2]
                port=minfo[4]
                cinfo=des_cdb(host,port,csql)                
                if cinfo:
                    rvalue=get_client(host,port,readsql)
                    if rvalue[0][0] == 0:
                        pass
                    else:
                        log_msg='Master node %s:%s is read only'%(host,port)
                        Log.write('e',"get mydes {}".format(log_msg))
                    return 'Yes',host,port
                else:
                    self.get_status(cname)
                    return 'No',host,port
        except Exception as e:
                Log.write('e',"get mydes {}".format(e))
        
    def myhades(self,cname):
        try:
            cf='%s/mha_management/file/config.cfg'%(self.main_path)
            vip_swich=find_vip(cname)
            result=check_status(cname)
            if 'PING_OK' not in result:
                if 'uninitialized' not in result:
                    if vip_swich[1] == 0:
                        cfile="%s/conf/%s/%s.cnf"%(self.main_path,cname,cname)
                        instance=ConfigParser()
                        instance.read(cfile)
                        host=instance.get('server2','hostname')
                        port=instance.get('server2','port')
                        ince=host + ':' + port
                        clog='%s/log/%s_manager.log'%(self.main_path,cname)
                        parser=ConfigParser()
                        parser.read(cf)
                        with open(clog, 'r') as f:
                            lines = f.readlines()
                            last_line = lines[-1]
                        if 'Master' in last_line and \
                                'successfully' in last_line:
                            if ince in last_line:
                                return 0
                            else:
                                log='New Master not %s'%(ince)
                                Log.write('e',"myhades {}".format(log))
                        else:
                            log="%s switch log failed to detect success"%(cname)
                            Log.write('w',"myhades {}".format(log))
                    else:
                        log_msg='%s business opening VIP'%(cname)
                        Log.write('w',"myhades {}".format(log_msg))
                        sys.exit(2)
                else:
                    log_msg='%s business not initialized'%(cname)
                    Log.write('w'," myhades {}".format(log_msg))
                    return 1
            else:
                log_msg="%s HA Normal state detection"%(cname)
                Log.write('i'," myhades {}".format(log_msg))
                return 2
            
        except Exception as e:
                Log.write('e'," myhades {}".format(e))

    def get_status(self,cname):
        try:
            cfile="%s/conf/%s/%s.cnf"%(main_path,cname,cname)
            instance=ConfigParser()
            instance.read(cfile)
            host=instance.get('server2','hostname')
            port=instance.get('server2','port')
            sql="show slave status"
            info=get_client(host,port,sql)
            slaveinfo={}
            slaveinfo['Master_Host']=info[0][1]
            slaveinfo['Master_Port']=info[0][3]
            slaveinfo['Master_Log_File']=info[0][5]
            slaveinfo['Read_Master_Log_Pos']=info[0][6]
            slaveinfo['Exec_Master_Log_Pos']=info[0][21]
            jsons=json.dumps(slaveinfo,indent=6,sort_keys=True)
            msginfo="BMaster %s:%s slave status %s"%(host,port,jsons)    
            Log.write('i',msginfo)


        except Exception as e:
                Log.write('e'," get_status {}".format(e))



    def sget_db(self,cname,oldhost,oldport):    
            cfile="%s/conf/%s/%s.cnf"%(self.main_path,cname,cname)
            cdfile='%s/mha_management/file/config.cfg'%(self.main_path)
            paser=ConfigParser()
            paser.read(cdfile)
            proxy_list=paser.get('dbproxy','host')
            proxy_path=paser.get('dbproxy','path')
            instance=ConfigParser()
            instance.read(cfile)
            host=instance.get('server2','hostname')
            port=instance.get('server2','port')
            domain="select domain from db_cmdb.ha_mysql_table_list\
                         where ip='%s' and port =%s limit 1"%(host,port)
            for dbproxy_host in proxy_list.split(','):
                cmd="python /opt/flush_dbproxy.py %s %s %s \
                        %s %s"%(oldhost,oldport,host,port,proxy_path)
                ssh_key(dbproxy_host,cmd)
            newdomain=get_mdb(domain)
            upsql="update db_cmdb.ha_mysql_table_list set \
                    ip='%s',domain='%s',port=%s where ip='%s'and\
                    port=%s ; delete from db_cmdb.ha_mysql_table_list\
                     where ip='%s'and port=%s and role='slave'"\
                    %(host,newdomain[0][0],port,oldhost,oldport,host,port)
            execute_mdb(upsql) 
            self.send_wechat(cname,oldhost,oldport,host,port)
            log_msg='%s 业务触发切换，原主节点 %s:%s 已经成功切换到 %s:%s ,并同步dbproxy,更新完 CMDB , 请核实' %(cname,oldhost,oldport,host,port)
            Log.write('i'," Mysql failover : {}".format(log_msg))
        #    sys.exit(1)



    def send_wechat(self,cname,oldhost,oldport,newhost,newport):
        msg="AllFootball Mysql 故障切换\n%s 集群触发 Failover\n主库 %s:%s 已切换到备主库 %s:%s 成功,并同步到dbproxy,请核实\n当前时间为 %s" \
            %(cname,oldhost,oldport,newhost,newport,\
                    time.strftime("%Y-%m-%d %H:%M:%S"))
        chat=minwechat(msg)
        if chat == 1:
            Log.write('i',"切换状态微信已经发送")
    


    def run(self):
        while True:
            csr = self.queue.get(1)
            if csr != None:
                if csr != 'NULL':
                    for clist in csr:
                        connect_keys=self.mydes(clist[2])
                        oldhost=connect_keys[1]
                        oldport=connect_keys[2]
                        hades=self.myhades(clist[2])
                        instance="%s:%s"%(oldhost,oldport)
                        if connect_keys[0] == 'Yes' and hades == 2:
                            log_msg=' %s Master node connect normal'%(instance)
                            Log.write('i'," Master node {}".format(log_msg))
                        elif connect_keys[0] == 'Yes' and hades == 1:
                            log_msg=' %s Before joining the HA'%(instance)
                            Log.write('w'," Master node {}".format(log_msg))
                        elif connect_keys[0] == 'No' and hades == 0:
                            self.sget_db(clist[2],oldhost,oldport)
                            log_msg=' %s Unable to connect and HA has \
                                        switched'%(instance)
                            Log.write('e'," Master node {}".format(log_msg))
                        else:
                            log_msg='%s State not acquired'%(instance)
                            Log.write('e'," Master node {}".format(log_msg))
                else:
                    log_msg='There is no task into the queue'
                    Log.write('w'," run get {}".format(log_msg))



class ceshi():
    def __init__(self):
        self.cmysql_info=cluster_info('all')
    
    def get(self):
        aa=[]
        for i in self.cmysql_info:
            log_msg="Id for %s task is performed"%(i[0])
            Log.write('i','run get {}'.format(log_msg))
            print i[0]



queue = multiprocessing.Queue(40)

if __name__ == "__main__":
    processed = []
    for i in range(1):
        processed.append(Producer(queue))
        processed.append(Consumer(queue))
       
    for i in range(len(processed)):
        processed[i].start()
   
    for i in range(len(processed)):
        processed[i].join()  




