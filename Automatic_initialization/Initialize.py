#!/usr/bin/env python
#coding=utf-8
import os,sys,re,shutil,subprocess,socket,time
from paramiko import SSHClient,AutoAddPolicy
from optparse import OptionParser


def get_cli_options():
    usage = "\n"
    usage += "python " + sys.argv[0] + " [options]\n"
    usage += "\n"
    usage += "Desc: Mysql/Codis/Codis_Proxy  Management tookit\n"
    usage += "example:\n"
    usage += "python Initialize.py -H host -P Pport:Aport -n product_name -a codis_proxy\n" 
    usage += "python Initialize.py -H host -P port -r master -m memory -a mysql_server\n"
    usage += "python Initialize.py -H host -P port -r slave -m memory -a mysql_server\n"
    usage += "python Initialize.py -H host -P port -r master -m memory -a codis_server\n"
    usage += "python Initialize.py -H host -P port -r slave -m memory -a codis_server\n"
    usage += "python Initialize.py -H host -P admin_port -s codis_proxy\n"
    usage += "python Initialize.py -H host -P admin_port -t codis_proxy\n"
    usage += "python Initialize.py -H host -P port -s codis_server|mysql_server\n"
    usage += "python Initialize.py -H host -P port -t codis_server|mysql_server\n"
    
#    parser = OptionParser(usage="python %prog [options]",
#            description="""Desc: Redis/Codis Management tookit""")
    parser = OptionParser(usage)
    parser.add_option("-H","--host",
                    dest="host",
                    metavar="Node host",
                    help="Add a Host in codis_proxy|codis_server|mysql_server")
    parser.add_option("-P","--port",
                    dest="port",
                    metavar="Node Port",
                    help="Add a server_port 7001 or proxy_port 19001:11001")
    parser.add_option('-n',"--product",
                    dest="product",
                    metavar="product_name",
                    help="Add a product_name in codis_proxy")
    parser.add_option("-a","--add",
                    dest="add_role",
                    metavar="codis_proxy|codis_server|mysql_server",
                    help="Add a role in codis_proxy|codis_server|mysql_server")
    parser.add_option("-m","--memory",
                    dest="memory",
                    metavar="server_memory",
                    help="Add a memory (defaults G) in codis_server maxmemory or mysql memory")
    parser.add_option("-r","--msroles",
                    dest="msrole",
                    metavar="master|slave",
                    help="Add a roles in codis_server|mysql_server")
    parser.add_option("-d","--dashboard",
                    dest="dashboard_switch",
                    metavar="yes|no",
                    help="Add to dashboard")
    parser.add_option("-s","--start",
                    dest="start_role",
                    metavar="codis_proxy|codis_server|mysql_server",
                    help="Start a in codis_proxy|codis_server|mysql_server")
    parser.add_option("-t","--stop",
                    dest="stop_role",
                    metavar="codis_proxy|codis_server|mysql_server",
                    help="Stop a in codis_proxy|server|mysql_server ")
    (options,args) = parser.parse_args()
    return options


minpath='/home/work/'


def ssh_command(host,command):
    sshConn = SSHClient()
    sshConn.set_missing_host_key_policy(AutoAddPolicy())
    sshConn.connect(hostname=host, port=22, username='root')
    stdin, stdout, stderr = sshConn.exec_command(command)
    return  stdout.readlines()
    sshConn.close()  

def des_dir(host,path):
    host_dir=ssh_command(host,'ls -l %s'%(path))
    if host_dir:
        return host_dir
    else:
        return 0

def des_file(host,file):
    host_file=ssh_command(host,'ls %s'%(file))
    if host_file:
        return host_file
    else:
        return 0


def isIP(str):
    p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(str):
        return True
    else:
        return False


def alter_file(file,old_str,new_str):
    try:
        with open(file, "r") as f1,open("%s.bak" % file, "w") as f2:
            for line in f1.readlines():
                if new_str.strip() in line.strip():
                    msg="The configuration file %s %s the configuration \
                            item already exists"%(file,new_str)
                    print msg
                    sys.exit(2)
                f2.write(re.sub(old_str,new_str,line))
        os.remove(file)
        os.rename("%s.bak" % file, file) 

    except Exception as err:
        print err


def flush_tmp_file(role,*config):
    main_path=os.getcwd()
    if role == 'codis_proxy':
        proxy_port=config[1].split(':')[0]
        ph='0.0.0.0:' + proxy_port
        admin_port=config[1].split(':')[1]
        ah=config[0] + ':' + admin_port
        product_name=config[2]
        tmpfile=main_path + '/codis_path/%s/etc/formwork/proxy.toml'%(role)
        pfile=main_path + '/codis_path/%s/etc/proxy_%s.toml'%(role,admin_port)
        if not os.path.exists(tmpfile):
            print "%s tmpfile path not exist"%(role)
            sys.exit(2)
        else:
            shutil.copyfile(tmpfile,pfile)
            alter_file(pfile,'product-name',product_name)
            alter_file(pfile,'admin-addr',ah)
            alter_file(pfile,'proxy-addr',ph)
            scp_file(config[0],admin_port,role,pfile)

    elif role == 'codis_server':
        tmpdir=main_path + '/codis_path/%s/etc/formwork/'%(role)
        mtmpfile=tmpdir + 'redis_master.cnf'
        stmpfile=tmpdir + 'redis_slave.cnf'
        if not os.path.isfile(mtmpfile) or not os.path.isfile(stmpfile):
            print "%s or %s \n filepath not exist"%(mtmpfile,stmpfile)
            sys.exit(2)
        server_file=main_path + '/codis_path/%s/etc/codis_%s.cnf'%(role,config[1])
        port=str(config[1])
        memory=str(config[3]) + 'gb'
        if config[2] == 'master':
            shutil.copyfile(mtmpfile,server_file)
            alter_file(server_file,'rsport',port)
            alter_file(server_file,'max-memory',memory)
            scp_file(config[0],port,role,server_file)

        elif config[2] == 'slave':
            shutil.copyfile(stmpfile,server_file)
            alter_file(server_file,'rsport',port)
            alter_file(server_file,'max-memory',memory)
            scp_file(config[0],port,role,server_file)

        else:
            print  "No role assigned"

    elif role == 'mysql_server':
        myhost=config[0]
        myport=str(config[1])
        myrole=config[2]
        mymemory=str(config[3]) + 'G'
        serverid = int(time.time())
        tmpdir=main_path + '/mysql_path/%s/etc/formwork/'%(role)
        mytfile=tmpdir + 'mysql.conf'
        mysfile=main_path + '/mysql_path/%s/etc/mysql%s.conf'%(role,myport)
        if not os.path.isfile(mytfile): 
            print "Mysql config %s \n not exist"%(mtmpfile)     
            sys.exit(2)
        if myrole == 'master':
            shutil.copyfile(mytfile,mysfile)
            alter_file(mysfile,'mysql_port',myport)
            alter_file(mysfile,'mysql_serverid',str(serverid))
            alter_file(mysfile,'mysql_buffer',mymemory)
            alter_file(mysfile,'read_only','read_only=0')
            scp_file(myhost,myport,role,mysfile)
        elif myrole == 'slave':
            shutil.copyfile(mytfile,mysfile)
            alter_file(mysfile,'mysql_port',myport)
            alter_file(mysfile,'mysql_serverid',str(serverid))
            alter_file(mysfile,'mysql_buffer',mymemory)
            alter_file(mysfile,'read_only','read_only=1')
            scp_file(myhost,myport,role,mysfile)
      

    else:
        print "Add a role not in codis_proxy|codis_server|mysql_server"
 
def binfile(role,host):
    codis_binpath='/opt/codis_bin'
    mysql_binpath='/opt/mysql5721'
    main_path=os.getcwd()
    if role == 'codis_proxy':
        if des_dir(host,codis_binpath) == 0:
            bcmd='mkdir -p ' + codis_binpath
            ssh_command(host,bcmd)
        lfile=main_path + '/codis_path/codis_bin/codis-proxy'
        if os.path.isfile(lfile):
            proxy_bin='/opt/codis_bin/codis-proxy'
            if des_file(host,proxy_bin) == 0:
                cmd="scp  %s %s:%s"%(lfile,host,codis_binpath)        
                child=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        else:
            print "%s 文件不存在" %lfile
    elif role == 'codis_server':
        if des_dir(host,codis_binpath) == 0:
            bcmd='mkdir -p ' + codis_binpath
            ssh_command(host,bcmd)
        lfile=main_path + '/codis_path/codis_bin/codis-server'
        if os.path.isfile(lfile):
            server_bin='/opt/codis_bin/codis-server'
            if des_file(host,server_bin) == 0:
                cmd="scp  %s %s:%s"%(lfile,host,codis_binpath)
                child=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        else:
            print "%s 文件不存在" %lfile 
    elif role == 'mysql_server':
        if des_dir(host,mysql_binpath) == 0:
           # print des_dir(host,mysql_binpath)
            mybin=main_path + '/mysql_path/%s/base/mysql5721'%(role)
            cmd="scp -r %s %s:%s"%(mybin,host,'/opt')
            pipe=os.popen(cmd,'r')
            #subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        else:
            print "Mysql Base path %s existing"%(mysql_binpath)




def cpfile(pathfile,host,cnfpath):
    cfile=pathfile.split('/')[-1]
    checkfile=cnfpath + '/' + cfile
    if des_file(host,checkfile) == 0:
        cmd="scp %s %s:%s"%(pathfile,host,cnfpath)
        child=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        stdstr=child.stdout.read() 
        if 'svn: E' in stdstr:
            print 'File initialization Error'
        else:
            print 'File initialization successful'
        os.remove(pathfile)
    else:
        print "%s 已经存在"%(checkfile)


def scp_file(host,port,roles,pathfile):
    if roles == 'codis_proxy':
        path=minpath + roles
        cnfpath=path + '/etc'
        if des_dir(host,path) == 0: 
            cmd="mkdir -p %s/{etc,log}"%(path)
            ssh_command(host,cmd)  
            print "The main path has been created %s"%(path)
            cpfile(pathfile,host,cnfpath)
        else:
            cpfile(pathfile,host,cnfpath)

    elif roles == 'codis_server':
        path=minpath + roles
        cnfpath=path + '/etc'
        if des_dir(host,path) == 0:
            cmd="mkdir -p %s/{etc,data,log,tmp}"%(path)
            ssh_command(host,cmd)
            print "The main path has been created %s"%(path)
            cpfile(pathfile,host,cnfpath)
        else:
            cpfile(pathfile,host,cnfpath)

    elif roles == 'mysql_server':
        data_path=os.getcwd() + '/mysql_path/mysql_server/data'
        binpath=os.getcwd() + '/mysql_path/mysql_server/bin/*'
        if os.path.exists(data_path):
            mypath=minpath + 'mysql%s'%(port)  
            cnfpath=mypath + '/etc'  
            if des_dir(host,mypath) == 0:
                cmd="mkdir -p %s/{etc,log,tmp}"%(mypath)
                ssh_command(host,cmd)
                cpfile(pathfile,host,cnfpath)
                cmd="scp -r %s %s:%s ; scp %s %s:%s"%(data_path,host,mypath,binpath,host,'/usr/bin/')
                child=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                stdstr=child.stdout.read()
                if 'svn: E' in stdstr:
                    print 'Mysql data path %s initialization Error'%(data_path)
                else:
                    print 'Mysql data path %s initialization successful'%(data_path)
                cown="touch %s/log/mysql-error.log ; chown -R work. %s"%(mypath,mypath)
                ssh_command(host,cown)
            else:
                os.remove(pathfile)
                print "Mysql main path %s already exists"%(mypath)
        else:
            print "Mysql data path %s not exists"%(data_path)

def Telport(ip,port):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        s.connect((ip,int(port)))
        s.shutdown(2)
#        print 'The port %d has been occupied' % port
        return True 
    except:
        return False

def start(role,host,port):
    if role == 'codis_proxy':
        ppath="/opt/codis_bin/codis-proxy"
        cfile=minpath + "codis_proxy/etc"
        clog=minpath + "codis_proxy/log"
        if des_dir(host,cfile) != 0 and des_dir(host,clog) != 0  and des_file(host,ppath) != 0:          
            cpfile=cfile + "/proxy_%s.toml"%(port) 
            if des_file(host,cpfile) != 0:
                cplog=clog + "/proxy_%s.log"%(port)
                cmd=ppath + " --ncpu=4 --config="
                cmd+=cpfile + " --log=" + cplog + " --log-level=WARN > /dev/null 1>&2  &"
                if not Telport(host,port):       
                    ssh_command(host,cmd)
                    time.sleep(3)
                    if Telport(host,port):
                        print "Codis Proxy %s Start-up success"%(port)
                else:
                    print "Codis Proxy %s Has enabled"%(port)
            else:
                print "%s File does not exist"%(cpfile)
        else:
            print "Codis Proxy Configure path exception,Please check" 

    elif role == 'codis_server': 
        ppath="/opt/codis_bin/codis-server " 
        cfile=minpath + "codis_server/etc" 
        if des_dir(host,cfile) != 0 and des_file(host,ppath) != 0:
            sfile=cfile + "/codis_%s.cnf"%(port)
            if des_file(host,sfile) != 0:
                cmd=ppath + ' ' + sfile
                if not Telport(host,port):
                    ssh_command(host,cmd)
                    time.sleep(1)
                    if Telport(host,port):
                        print "Codis server %s Start-up success"%(port)
                else:
                    print "Codis server %s Has enabled"%(port)
            else:
                print "%s File does not exist"%(sfile)
        else:
            print "Codis server Configure path exception,Please check"

    elif role == 'mysql_server':
        mycpath=minpath + 'mysql%s/etc/mysql%s.conf'%(port,port)
        binfile="/opt/mysql5721/bin/mysqld_safe"
        start=binfile + " --defaults-file=" + mycpath + "  > /dev/null 1>&2  &"
        if des_file(host,mycpath) != 0 and des_file(host,binfile) != 0: 
            if not Telport(host,port):
                ssh_command(host,start)
                time.sleep(8)
                if Telport(host,port):
                    print "Mysql server %s Start-up success"%(port)
                else:
                    print "Mysql server %s Start-up failure "%(port)
            else:
                print "Mysql server %s port Has enabled"%(port)
        else:
            print "Mysql server %s or %s not exist"%(mycpath,binfile)

def stop(role,host,port):
    if role == 'codis_proxy':
        pfile="proxy_%s.toml"%(port)
        if  Telport(host,port): 
            cmd="ps -ef|grep " + pfile
            cmd+="|grep -v grep |awk '{print $2}'|xargs kill -9"        
            ssh_command(host,cmd)
            time.sleep(1)
            if not Telport(host,port):
                print "Codis proxy %s Stop success"%(port)
        else:
            print "Codis proxy port %s Is not enabled"%(port)

    elif role == 'codis_server':
        if  Telport(host,port):
            cmd="ps -ef|grep " + port
            cmd+="|grep -v grep |awk '{print $2}'|xargs kill -9"
            ssh_command(host,cmd)
            time.sleep(1)
            if not Telport(host,port):
                print "Codis server %s Stop success"%(port) 
        else:
            print "Codis server port %s Is not enabled"%(port)

    elif role == 'mysql_server':
        if  Telport(host,port):
            mysocket=minpath + 'mysql%s/tmp/mysql%s.sock'%(port,port)
            myadmin="/opt/mysql5721/bin/mysqladmin"
            if des_file(host,myadmin) != 0:
                cmd=myadmin 
                cmd+=" -usuperdba -pksGQPtaBGEI0H02U0v -h127.0.0.1 " 
                cmd+=" -P%s  shutdown"%(port)
                ssh_command(host,cmd)
                time.sleep(1)
                if not Telport(host,port):
                    print "Mysql server %s Stop success"%(port)
                else:
                    print "Mysql server %s Stop failure"%(port)
            else:
                print "Mysql %s not exist"%(myadmin)
        else:
            print "Mysql server port %s Is not enabled"%(port)





if __name__ == '__main__':
    options=get_cli_options()
    if options.add_role in ('codis_proxy','codis_server','mysql_server'):
        if options.add_role == 'codis_proxy':
            if options.host and options.port and options.product:
                if not isIP(options.host):
                    print options.host + " | Codis proxy host is not IP!"
                    sys.exit(1)
                portlist=options.port
                if len(portlist.split(':')) == 2:
                    pport=portlist.split(':')[0]
                    aport=portlist.split(':')[1]
                    if pport.isdigit() and aport.isdigit():
                        if Telport(options.host,pport):
                            print "The proxy port %s has been occupied" %pport
                        elif Telport(options.host,aport):
                            print "The admin port %s has been occupied" %aport
                        else:
                            binfile(options.add_role,options.host)
                            flush_tmp_file(options.add_role,options.host,portlist,options.product)
                    else:
                        print "codis_proxy port you entered is not a number"
                else:
                    print "codis_proxy the number of ports you entered is incorrect"
            else:
                print "codis_proxy the parameter configuration is wrong"
        elif options.add_role == 'codis_server':
            if options.host and options.port and options.msrole and options.memory:
                if options.msrole == 'master' or options.msrole == 'slave':
                    serverport=options.port
                    if serverport.isdigit():
                        if Telport(options.host,serverport):
                                print "The server port %s has been occupied" %serverport
                        else:
                            if options.memory.isdigit():
                                binfile(options.add_role,options.host)
                                flush_tmp_file(options.add_role,options.host,\
                                    serverport,options.msrole,options.memory)
                            else:
                                print "The memory you entered is not a number"
                    else:
                        print "The port you entered is not a number"
            else:
                print "codis_server the parameter configuration is wrong"
        elif options.add_role == 'mysql_server':
                if options.host and options.port and options.msrole and options.memory:
                    if options.msrole == 'master' or options.msrole == 'slave':
                        serverport=options.port
                        if serverport.isdigit():
                            if Telport(options.host,serverport):
                                print "Mysql server port %s has been occupied" %serverport
                            else:
                                if options.memory.isdigit():
                                    binfile(options.add_role,options.host)
                                    flush_tmp_file(options.add_role,options.host,\
                                        serverport,options.msrole,options.memory)
                                else:
                                    print "Mysql memory you entered is not a number"
                        else:
                            print "Mysql port you entered is not a number"                    
                else:
                    print "mysql_server the parameter configuration is wrong"

    elif options.start_role in ('codis_proxy','codis_server','mysql_server'):
        if options.host and options.port:
            port=options.port
            if port.isdigit():
                start(options.start_role,options.host,port) 
            else:
                print "The port you entered is not a number or not proxy admin port"

    elif options.stop_role in ('codis_proxy','codis_server','mysql_server'):
        if options.host and options.port:        
            port=options.port
            if port.isdigit():
                stop(options.stop_role,options.host,port)
            else:
                print "The port you entered is not a number or not proxy admin port"
        else:
            print "The added role is not specified"
    
