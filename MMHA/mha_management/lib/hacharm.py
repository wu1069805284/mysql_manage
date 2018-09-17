#!/bin/env python
import shutil,os,sys,commands
import time,datetime
from LogHandler import WriteLog

Log=WriteLog()

def check_ssh(ssh_command):
    try:
        (status, output) = commands.getstatusoutput(ssh_command)
        if status == 0:
            Log.write('i',"check_ssh: {}".format(output))
        else:
            msg='%s commands abnormality'%(ssh_command)
            Log.write('e',"check_ssh: {}".format(msg))
            sys.exit(1)

    except Exception as err:
        Log.write('e',"check_ssh: {}".format(err.message))

def check_repl(repl_command):
    try:
        (status, output) = commands.getstatusoutput(repl_command)
        if status == 0:
            Log.write('i',"check_repl: {}".format(output))
        else:
            msg='%s commands abnormality'%(repl_command)
            Log.write('e',"check_repl: {}".format(msg))
            sys.exit(1)

    except Exception as err:
        Log.write('e',"check_repl: {}".format(err.message))

def sr_status(cname):
        main_path=os.getcwd().split('/mha_management')[0]
        ssh_command="%s/bin/masterha_check_ssh"%(main_path)
        ssh_command += " --conf=%s/conf/%s/%s.cnf" %(main_path,cname,cname)
        repl_command="%s/bin/masterha_check_repl"%(main_path)
        repl_command += " --conf=%s/conf/%s/%s.cnf" %(main_path,cname,cname)
        check_ssh(ssh_command)
        check_repl(repl_command)


def check_status(cname):
    try:
        main_path=os.getcwd().split('/mha_management')[0]
        status_command="%s/bin/masterha_check_status"%(main_path)
        status_command += " --conf=%s/conf/%s/%s.cnf"%(main_path,cname,cname)
        cf_file="%s/conf/%s/%s.cnf"%(main_path,cname,cname)
        if not os.path.isfile(cf_file):
            msg="%s cluster uninitialized"%(cname)
            return msg
    #        sys.exit(1)
        (status, output) = commands.getstatusoutput(status_command)
        return output
        if status != 0:
            msg='%s commands abnormality'%(status_command)
            Log.write('e',"check_status: {}".format(msg))
    #        sys.exit(1)

    except Exception as err:
        Log.write('e',"check_status: {}".format(err.message))


def work_clean(cname):
    main_path=os.getcwd().split('/mha_management')[0]
    work_path="%s/work/%s"%(main_path,cname)
    shutil.rmtree(work_path)
    os.mkdir(work_path)

def pro_status(cname):
    main_path=os.getcwd().split('/mha_management')[0]
    lockfile=main_path + "/mha_management/file/process.lock"
    os.system("ps -ef | grep -i " + cname + ".cnf |grep -v grep > %s"\
            %(lockfile))
    if (os.path.getsize(lockfile)):
        return 1
    else:
        return 0

def app_start(cname):
    try:
        main_path=os.getcwd().split('/mha_management')[0]
        start_command="nohup %s/bin/masterha_manager"%(main_path)
        start_command += " --conf=%s/conf/%s/%s.cnf  &"%(main_path,cname,cname)
        status01=check_status(cname)
        if "PING_OK" in status01:
            msg="%s cluster has started"%(cname)
            Log.write('e',"app_start: {}".format(msg))
            sys.exit(1)
        if "NOT_RUNNING" in status01:
            work_clean(cname)
            os.system("%s"%(start_command))
            if pro_status(cname) == 1:
                msg="%s monitoring process has started normally"%(cname)
                Log.write('i',"app_start: {}".format(msg))
            elif pro_status(cname) == 0:
                msg='%s commands abnormality'%(start_command)
                Log.write('e',"app_start: {}".format(msg))
                sys.exit(1)
    except Exception as err:
        Log.write('e',"app_start: {}".format(err.message))


def app_stop(cname):
    try:
        main_path=os.getcwd().split('/mha_management')[0]
        stop_command="%s/bin/masterha_stop"%(main_path)
        stop_command += " --conf=%s/conf/%s/%s.cnf"%(main_path,cname,cname)
        status=check_status(cname)
        if "PING_OK" in status:
            (status, output) = commands.getstatusoutput(stop_command)
            if status == 0:
                Log.write('i',"app_stop: {}".format(output))
            else:
                msg='%s commands abnormality'%(stop_command)
                Log.write('e',"app_stop: {}".format(msg))
                sys.exit(1)
        else:
            msg="%s Process state exception"%(cname)
            Log.write('e',"app_stop: {}".format(msg))
            sys.exit(1)

    except Exception as err:
        Log.write('e',"app_stop: {}".format(err.message))

