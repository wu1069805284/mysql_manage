思路：为了实现mysql的高可用的集中化管理，自动初始集群到MHA的管理中来，以mysql集群的唯一性进行统一识别与管理。
功能：
一、初始化mysql集群到mha。
二、自动初始化集群主机之间的公钥认证（可选）。
三、以守护进程启动集群到mha管理中，并自动添加vip。
四、停止指定集群的监控。
五、从mha管理中删除指定集群。
六、查看指定集群或所有集群监控的运行状态。

Usage: python HA_management.py [options]
 Desc: MHA Management tool
 Options:
  -h, --help            show this help message and exit
  -a cluster name, --add=cluster name
                        Add a mysql cluster in MHA
  -k yes|no, --keys=yes|no
                        Host key selection is automatically added .
                        If yes, the same host cluster process will exit
                        automatically, verify.
                        If no, please confirm that the key authentication
                        between the cluster hosts has been opened, please
                        check.
  -d cluster name, --del=cluster name
                        Delete a mysql cluster in MHA,The host keys need to be
                        manually cleaned
  -r cluster name, --start=cluster name
                        Start a mysql cluster in MHA
  -t cluster name, --stop=cluster name
                        Stop a mysql cluster in MHA
  -l cluster name|all, --list=cluster name|all
                        View the state of mysql cluster in mha

使用方法：
yum install perl-DBD-MySQL perl-Config-Tiny perl-Log-Dispatch perl-Parallel-ForkManager perl-Time-HiRes -y

一、把Mha_Management_program管理程序放在的机器保证该主机对所有mysql主机能自动登录，例如bmon。
二、配置文件说明：
配置文件：Mha_Management_program/mha_management/file/config.cfg
vip添加卸载、通知脚本：Mha_Management_program/vip_manager/formwork/*,目前默认采用的ifconfig
ha_user:ha切换探测使用的用户名，需要保证指定集群已经初始化完成。
ha_password：ha用户的密码。
repl_user：主从复制账号。
repl_password：主从复制密码。
ssh_user：ssh登录用户，默认root
 
mysql_user：管理节点用户
mysql_password：管理节点密码
mysql_host：管理节点主机
mysql_port：管理节点端口

三、管理节点需要添加的库和表。
表结构文件：Mha_Management_program/mha_management/module/ha_administer.sql
注意：集群名和vip一定要保证唯一性，发生过failover一定要调整集群表的信息。
 
四、执行文件路径
Mha_Management_program/mha_management/HA_management.py  --help

需要改进的功能需求：
1、vip切换通知功能。
2、集群管理表failover自动同步。
3、ha进程管理监控。
4、ssh互信功能安全性。
5、集群从节点延时功能，目前工具集不考虑集群节点延时。
