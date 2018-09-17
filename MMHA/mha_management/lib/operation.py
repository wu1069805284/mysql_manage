#!/bin/env python
import sys,os,re,stat,shutil
from detection import *
from LogHandler import WriteLog
from paramiko   import SSHClient,AutoAddPolicy

Log=WriteLog()


def ssh_key(host,command):

        try:
            sshConn = SSHClient()
            sshConn.set_missing_host_key_policy(AutoAddPolicy())
            sshConn.connect(hostname=host, port=22, username='root')
            stdin, stdout, stderr = sshConn.exec_command(command)
            return(stdout.read())


        except Exception as err:
            Log.write('e',"ssh_key: {}".format(err.message))



def Clean_sshkeys(cname):
    try:
        table_list=[]
        tb=tb_info(cname)
        for tb_list in tb:
            host=tb_list[2]
            hostname=tb_list[3]
            work_dir(host)
            table_list.append(hostname)
        for tb_list in tb:
            host=tb_list[2]
            for i in table_list:
                ssh_key(host,"sed -i -e '/%s/d' /root/.ssh/authorized_keys"%(i))



    except Exception as err:
        Log.write('e',"Clean_sshkeys: {}".format(err.message))




def Add_sshkeys(cname):
    try:
        keys_list=[]
        tb=tb_info(cname)
        Clean_sshkeys(cname)
        for tb_list in tb:
            host=tb_list[2]
            hostname=tb_list[3]
            keys=ssh_key(host,"cat /root/.ssh/id_rsa.pub")
            if not keys:
                msg="The host %s public key is not generated"%(host)
                Log.write('e',"main: {}".format(msg))
                sys.exit(2)
            keys_list.append(keys)
        for key in keys_list:
            for tb_list in tb:
                host=tb_list[2]
                hostname=tb_list[3]
                if hostname not in key:
                    ssh_key(host,"echo '%s' >> /root/.ssh/authorized_keys"%(key))
        msg="%s keys authentication between the cluster hosts is completed"%(cname)
        Log.write('i',"Add_sshkeys: {}".format(msg))

    except Exception as err:
        Log.write('e',"Add_sshkeys: {}".format(err.message))



def alter_file(file,old_str,new_str):

    with open(file, "r") as f1,open("%s.bak" % file, "w") as f2:
        for line in f1.readlines():
            if new_str.strip() in line.strip():
                msg="The configuration file %s %s the configuration \
                        item already exists"%(file,new_str)
                Log.write('e',"alter_file:{}".format(msg))
                sys.exit(2)
            f2.write(re.sub(old_str,new_str,line))
    os.remove(file)
    os.rename("%s.bak" % file, file)


def User_init(cfile):
    ha_user=getConfig('user_cnf','ha_user')
    ha_pwd=getConfig('user_cnf','ha_password')
    repl_user=getConfig('user_cnf','repl_user')
    repl_pwd=getConfig('user_cnf','repl_password')
    ssh_user=getConfig('user_cnf','ssh_user')
    user_list="user=%s\npassword=%s\nrepl_user=%s\nrepl_password=%s\nssh_user=%s\n"\
                %(ha_user,ha_pwd,repl_user,repl_pwd,ssh_user)
    alter_file(cfile,'userlist',user_list)



def HA_init(cname):
    try:
        master_dif(cname)
        main_path=os.getcwd().split('mha_management')[0]
        ssh_dir="%sconf/%s" %(main_path,cname)
        ssh_file="%sconf/%s/%s.cnf"%(main_path,cname,cname)
        tmpfile=main_path + 'conf/formwork/app.formwork'
        if not os.path.exists(tmpfile):
            msg="The master configuration template file does not exist"
            Log.write('e',"confinit: {}".format(msg))
            sys.exit(2)
        if not os.path.exists(ssh_dir):
            os.mkdir(ssh_dir)
        if not os.path.exists(ssh_file): 
            shutil.copy(tmpfile,ssh_file)
        local_work_dir="%swork/%s" %(main_path,cname)
        if not os.path.exists(local_work_dir):
            os.mkdir(local_work_dir)
        alter_file(ssh_file,'manager_workdir=','manager_workdir=%s'%local_work_dir)
        log_file="%slog/%s_manager.log"%(main_path,cname)
        alter_file(ssh_file,'manager_log=','manager_log=%s'%log_file)
        User_init(ssh_file)
        binlist=['mysql-bin','log-bin']
        binfile=check_masterbinlog(cname)[0][1].split('/')[-1]
        for i in  binlist:
            if binfile == i:
                sp='/' + i
                binlog_path=check_masterbinlog(cname)[0][1].split(sp)[0]
            else:
                binlog_path=check_masterbinlog(cname)[0][1]
        alter_file(ssh_file,'master_binlog_dir=','master_binlog_dir=%s'%(binlog_path))
        alter_file(ssh_file,'remote_workdir=','remote_workdir=/tmp/mysql_ha_work')
        alter_file(ssh_file,'secondary_check_script=',\
            'secondary_check_script=%sbin/masterha_secondary_check -s %s'\
            %(main_path,secondary_check(cname)))

    except Exception as err:
        Log.write('e',"HA INIT : {}".format(err)) 
        sys.exit(1)

def HA_vip_init(cname):
    try:
        master_dif(cname)
        main_path=os.getcwd().split('mha_management')[0]
        ssh_dir="%sconf/%s" %(main_path,cname)
        ssh_file="%sconf/%s/%s.cnf"%(main_path,cname,cname)
        tmpfile=main_path + 'conf/formwork/app_vip.formwork'
        if not os.path.exists(tmpfile):
            msg="The master configuration template file does not exist"
            Log.write('e',"confinit: {}".format(msg))
            sys.exit(2)
        if not os.path.exists(ssh_dir):  
            os.mkdir(ssh_dir)
            if not os.path.exists(ssh_file):
                shutil.copy(tmpfile,ssh_file)
        local_work_dir="%swork/%s" %(main_path,cname)
        if not os.path.exists(local_work_dir):
            os.mkdir(local_work_dir)
        alter_file(ssh_file,'manager_workdir=','manager_workdir=%s'%local_work_dir)
        log_file="%slog/%s_manager.log"%(main_path,cname)
        alter_file(ssh_file,'manager_log=','manager_log=%s'%log_file)
        User_init(ssh_file)
        binlist=['mysql-bin','log-bin']
        binfile=check_masterbinlog(cname)[0][1].split('/')[-1]
        for i in  binlist:
            if binfile == i:
                sp='/' + i
                binlog_path=check_masterbinlog(cname)[0][1].split(sp)[0]
            else:
                binlog_path=check_masterbinlog(cname)[0][1]

        alter_file(ssh_file,'master_binlog_dir=','master_binlog_dir=%s'%(binlog_path))
        alter_file(ssh_file,'remote_workdir=','remote_workdir=/tmp/mysql_ha_work')
        vip_dir="%svip_manager"%(main_path)
        line_dir="%s/%s"%(vip_dir,cname)
        if not os.path.exists(vip_dir):
            os.mkdir(vip_dir)
        if not os.path.exists(line_dir):
            swich_vip=find_vip(cname) 
            vip=swich_vip[0] + '/32'
            shutil.copytree('%s/formwork'%(vip_dir),line_dir)
            alter_file('%s/master_ip_failover'%(line_dir),'tmpvip',vip)    
            alter_file('%s/master_ip_online_change'%(line_dir),'tmpvip',vip)
            alter_file('%s/send_report.sh'%(line_dir),'tmp_manager.log',\
                    '%s/log/%s_manager.log'%(main_path,cname))
             
        alter_file(ssh_file,'master_ip_failover_script=',\
                'master_ip_failover_script=%s/master_ip_failover'%(line_dir))
        alter_file(ssh_file,'report_script=','report_script=%s/send_report.sh'%(line_dir))
        alter_file(ssh_file,'master_ip_online_change_script=',\
                'master_ip_online_change_script=%s/master_ip_online_change'%(line_dir))
        alter_file(ssh_file,'secondary_check_script=',\
                'secondary_check_script=%sbin/masterha_secondary_check -s %s'\
                %(main_path,secondary_check(cname)))

    except Exception as err:
        Log.write('e',"HA VIP INIT : {}".format(err))
        sys.exit(1)
    

def ha_delete(cname):
        main_path=os.getcwd().split('/mha_management')[0]
        cnf_path="%s/conf/%s"%(main_path,cname)
        vip_path="%s/vip_manager/%s"%(main_path,cname)
        work_path="%s/work/%s"%(main_path,cname)
        vip_swich=find_vip(cname)
        if os.path.exists(cnf_path):
            shutil.rmtree(cnf_path)
        else:
            msg="%s path may not exist, please check !"%(cnf_path)
            Log.write('e',"ha_delete:{}".format(msg))
        if vip_swich[1] == 1:
            if os.path.exists(vip_path):
                shutil.rmtree(vip_path)
        else:  
            msg="%s path may not exist, please check !"%(vip_path)
            Log.write('e',"ha_delete:{}".format(msg))
        if os.path.exists(work_path):
            shutil.rmtree(work_path)
        else:
            msg="%s path may not exist, please check !"%(work_path)
            Log.write('e',"ha_delete:{}".format(msg))



def secondary_check(cname):
    slave_list=[]
    for v in tb_info(cname):
        if v[5] == 'slave':
            slave_list.append(v[2])
    secondary=" -s ".join(slave_list)
    return secondary


def supple_file(cname):
    main_path=os.getcwd().split('mha_management')[0]
    cnf_file="%sconf/%s/%s.cnf"%(main_path,cname,cname)
    tb=tb_info(cname)
    if cnf_file:
        with open(cnf_file, "a") as f1:
            for num,value in enumerate(tb,1):
                    if value[5] == 'master':
                        num=1
                        serverinfo="[server%s]\nhostname=%s\nport=%s\ncandidate_master=1\n\n"\
                             %(num,value[2],value[4])
                        f1.write(serverinfo)
                    if value[5] == 'slave' and value[6] == 0:
                        serverinfo="[server%s]\nhostname=%s\nport=%s\ncandidate_master=1\n\n"\
                            %(num,value[2],value[4])
                        f1.write(serverinfo)
                    if value[5] == 'slave' and value[6] == 1:
                        serverinfo="[server%s]\nhostname=%s\nport=%s\nno_master=1\n\n"\
                            %(num,value[2],value[4])
                        f1.write(serverinfo)



def work_dir(host):
    comm01="ll /tmp/mysql_ha_work/"
    comm02="mkdir /tmp/mysql_ha_work"
    ofile=ssh_key(host,comm01)
    if not ofile:
        ssh_key(host,comm02)


def authorise(cname):
    main_path=os.getcwd().split('/mha_management')[0]
    vip_path='%s/vip_manager/%s'%(main_path,cname)
    for f in os.listdir(vip_path):
        vip_file='%s/%s'%(vip_path,f)
        os.chmod('%s'%(vip_file),stat.S_IRWXU)

