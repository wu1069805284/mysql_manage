#/bin/bash  
source /root/.bash_profile  
  
orig_master_host=`echo "$1" | awk -F = '{print $2}'`  
new_master_host=`echo "$2" | awk -F = '{print $2}'`  
new_slave_hosts=`echo "$3" | awk -F = '{print $2}'`  
subject=`echo "$4" | awk -F = '{print $2}'`  
body=`echo "$5" | awk -F = '{print $2}'`  
  
#判断日志结尾是否有successfully，有则表示切换成功，成功与否都发邮件。  

tac tmp_manager.log | sed -n 2p | grep 'successfully' > /dev/null  

if [ $? -eq 0 ]  
then  
    echo -e "MHA $subject 主从切换成功\n master:$orig_master_host --> $new_master_host \n $body \n 当前从库:$new_slave_hosts" >> tmp_manager.log 

#| mutt  -s "MySQL实例宕掉,MHA $subject 切换成功"  

else  
    echo -e "MHA $subject 主从切换失败\n master:$orig_master_host --> $new_master_host \n $body" >> tmp_manager.log 

#| mutt -s "MySQL实例宕掉,MHA $subje  ct 切换失败" -- 94097532@qq.com  

fi  
