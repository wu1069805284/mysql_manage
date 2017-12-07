#!/usr/bin/env python
#coding=utf-8
#create by wuweijian

import commands,os,sys
from lib.detection import * 
from lib.operation import *
from lib.hacharm import *
from optparse import OptionParser


def c_check(cname):
        ci=cluster_info(cname)
        if not ci:
            print "ERROR : The cluster you entered is not entered"
        else:
            return 1


def t_check(cname):
    try:
        ti=tb_info(cname)
        for v in ti:
            host=v[2]
            port=int(v[4])
            Account_connectivity(host,port)
        return 1
    except Exception as err:
        print "t_check: {}".format(err.message)
        sys.exit(1)



def get_cli_options():
    parser = OptionParser(usage="usage: python %prog [options]",
            description="""Desc: MHA Management tool""")
    parser.add_option("-a","--add",
                            dest="add_cluster",
                            metavar="cluster name",
                            help="Add a mysql cluster in MHA")

    parser.add_option("-k","--keys",
                            dest="key_threshold",
                            metavar="yes|no",
                            help="Host key selection is automatically added .\
                            If yes, the same host cluster process will exit automatically, verify.\
                                If no, please confirm that the key authentication between the cluster hosts has been opened, please check.")
                    
    parser.add_option("-d","--del",
                            dest="delete_cluster",
                            metavar="cluster name",
                            help="Delete a mysql cluster in MHA,The host keys need to be manually cleaned")

    parser.add_option("-r","--start",
                            dest="start_cluster",
                            metavar="cluster name",
                            help="Start a mysql cluster in MHA")

    parser.add_option("-t","--stop",
                            dest="stop_cluster",
                            metavar="cluster name",
                            help="Stop a mysql cluster in MHA")
    
    parser.add_option("-l","--list",
                            dest="status_cluster",
                            metavar="cluster name|all",
                            help="View the state of mysql cluster in mha")

    (options,args) = parser.parse_args()
    return options


def _options_filtering(optionitem,num):
    try:
        tiem_list=[]
        kv=optionitem.__dict__
        for k in kv.itervalues():
            tiem_list.append(k)
        if tiem_list.count(None) == num:
            return 1
        else:
            if num == 3:
                nv = 2
            elif num == 4:
                nv = 1
            print "Only %s key item can be specified"%(nv)
            sys.exit(2)
    except Exception as err:
        print "options_filtering: {}".format(err.message)


if __name__ == '__main__':
    options=get_cli_options()
    if options.add_cluster or options.key_threshold:
        options_filter_v=_options_filtering(options,4)
        if options_filter_v == 1:
            if options.key_threshold == 'yes':
                if c_check(options.add_cluster) == 1 and t_check(options.add_cluster) == 1:
                    Add_sshkeys(options.add_cluster)
                    HA_init(options.add_cluster)
                    supple_file(options.add_cluster)
                    sr_status(options.add_cluster)
            elif options.key_threshold == 'no': 
                if c_check(options.add_cluster) == 1 and t_check(options.add_cluster) == 1:
                    HA_init(options.add_cluster)
                    supple_file(options.add_cluster)
                    sr_status(options.add_cluster)
            else:
                print "Key's threshold input is not correct"
    elif options.delete_cluster:
        options_filter=_options_filtering(options,5)
        if options_filter == 1:
            if pro_status(options.delete_cluster) == 0:
                ha_delete(options.delete_cluster)
            elif pro_status(options.delete_cluster) == 1:
                msg="%s monitoring process is not shutdown, please close"\
                        %(options.delete_cluster)
                print msg
                sys.exit(1)
#            Clean_sshkeys(options.delete_cluster)
    elif options.start_cluster:
        options_filter=_options_filtering(options,5)
        if options_filter == 1:
            app_start(options.start_cluster)
    elif options.stop_cluster:
        options_filter=_options_filtering(options,5)
        if options_filter == 1:
            app_stop(options.stop_cluster)
    elif options.status_cluster:
        options_filter=_options_filtering(options,5)
        if options_filter == 1:
            status_list(options.status_cluster)

