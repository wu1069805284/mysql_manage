#!/usr/bin/env python
#coding=utf-8

import MySQLdb
import sys
import smtplib  
import time
from email.mime.text import MIMEText  

reload(sys)
sys.setdefaultencoding('utf-8')

smtp_host = 'smtp.exmail.qq.com:465'
mail_user = 'op@app.com'
mail_pass = ''

db_host   = ''
db_port   = 
db_user   = ''
db_pass   = ''
db_db     = ''


def dbhelp(hostname, dport, duser, pwd, ddb, sql):
    conn = MySQLdb.connect(host=hostname,port=dport,user=duser,passwd=pwd,db=ddb) 
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()

    return result


def send_mail(content, mailto, get_sub):

    ##Setting MIMEText
    msg = MIMEText( content.encode('utf8'), _subtype = 'html', _charset = 'utf8')
    msg['From']    = mail_user
    msg['Subject'] = u'%s' % get_sub
    msg['to']      = ",".join(mailto)

    try:
        ## connect smtp_host
        s = smtplib.SMTP_SSL(smtp_host)
        s.set_debuglevel(0)
       
        ## login to smtp_host
        s.login(mail_user, mail_pass)

        ## send mail
        s.sendmail(msg['From'], mailto, msg.as_string())

        ## close the connection between the mail server
        s.close()

    except Exception as e: 
        print 'Exception: ', e
   
## 标题
now = int(time.time())
todaystr = time.strftime("%Y-%m-%d", time.localtime(now-24*60*60))
subject = 'MySQL 慢查询日报 '+todaystr

## 发送列表
to_list = ['op@oneniceapp.com','nice-backrd@oneniceapp.com'] 

## 内容
## header
content='''
<html>
    <head>
        <title>MySQL 慢查询日报</title>
        <style type="text/css"> 
            table{border:1px solid #66B3FF } 
        </style>
    </head>
    <body>
'''
## body title
content += '<h1>MySQL 慢查询日报-'+todaystr+'</h1>'
content += '<hr>'

## total slowlog for all mysql instances
fromtimestr = time.strftime("%Y-%m-%d 00:00:00", time.localtime(now-24*60*60))
endtimestr  = time.strftime("%Y-%m-%d 23:59:59", time.localtime(now-24*60*60))

sql = "select sum(cnt) as cnts,round(sum(query_time_sum),2) as query_time_sum,round(sum(lock_time_sum),2) as lock_time_sum,sum(rows_sent_sum) as rows_sent_sum, sum(rows_examined_sum) as rows_examined_sum, round(max(max_query_time),2) as max_query_time, round(min(min_query_time),2) as min_query_time from nice_slow_log_parse where q_exec_time>="
sql += "'"+fromtimestr+"' and q_exec_time<="
sql += "'"+endtimestr+"'"
result = dbhelp(db_host, db_port, db_user, db_pass, db_db, sql)

content += '<h3>所有实例的慢查询统计</h3>'
#content += '<hr style="height:3px;border:none;border-top:3px blue;" />'

## table list
content += '<table border="1" border="0" cellspacing="0" cellpadding="0">'
content += '<tr>'
content += '<th>总次数</th>'
content += '<th>总时间</th>'
content += '<th>总Lock时间</th>'
content += '<th>总发送行数</th>'
content += '<th>总检测行数</th>'
content += '<th>最慢执行时间</th>'
content += '<th>最小执行时间</th>'
content += '</tr>'

for x in result:
    content += '<tr>'
    content += '<td>'+str(x[0])+'</td>'
    content += '<td>'+str(x[1])+'</td>'
    content += '<td>'+str(x[2])+'</td>'
    content += '<td>'+str(x[3])+'</td>'
    content += '<td>'+str(x[4])+'</td>'
    content += '<td>'+str(x[5])+'</td>'
    content += '<td>'+str(x[6])+'</td>'
    content += '</tr>'

content += '</table>'
content += '</br>'
content += '</br>'
content += '<hr>'


##  过滤拉数据的所有实例慢查询统计
sql111 = "select sum(cnt) as cnts,round(sum(query_time_sum),2) as query_time_sum,round(sum(lock_time_sum),2) as lock_time_sum,sum(rows_sent_sum) as rows_sent_sum, sum(rows_examined_sum) as rows_examined_sum, round(max(max_query_time),2) as max_query_time, round(min(min_query_time),2) as min_query_time from nice_slow_log_parse where q_exec_time>="
sql111 += "'"+fromtimestr+"' and q_exec_time<="
sql111 += "'"+endtimestr+"' and check_sum not in (select filter_key from nice_slow_log_filter)"
result111 = dbhelp(db_host, db_port, db_user, db_pass, db_db, sql111)
content += '<h3>所有实例的慢查询统计(过滤掉拉数据SQL)</h3>'

## table list
content += '<table border="1" border="0" cellspacing="0" cellpadding="0">'
content += '<tr>'
content += '<th>总次数</th>'
content += '<th>总时间</th>'
content += '<th>总Lock时间</th>'
content += '<th>总发送行数</th>'
content += '<th>总检测行数</th>'
content += '<th>最慢执行时间</th>'
content += '<th>最小执行时间</th>'
content += '</tr>'

for x in result111:
    content += '<tr>'
    content += '<td>'+str(x[0])+'</td>'
    content += '<td>'+str(x[1])+'</td>'
    content += '<td>'+str(x[2])+'</td>'
    content += '<td>'+str(x[3])+'</td>'
    content += '<td>'+str(x[4])+'</td>'
    content += '<td>'+str(x[5])+'</td>'
    content += '<td>'+str(x[6])+'</td>'
    content += '</tr>'

content += '</table>'
content += '</br>'
content += '</br>'
content += '<hr>'


sql1 = "select instancename, sum(cnt) as cnts,round(sum(query_time_sum),2) as query_time_sum,round(sum(lock_time_sum),2) as lock_time_sum,sum(rows_sent_sum) as rows_sent_sum, sum(rows_examined_sum) as rows_examined_sum,round(max(max_query_time),2) as max_query_time, round(min(min_query_time),2) as min_query_time from nice_slow_log_parse where q_exec_time>="
sql1 += "'"+fromtimestr+"' and q_exec_time<="
sql1 += "'"+endtimestr+"' and check_sum not in (select filter_key from nice_slow_log_filter) group by instancename order by cnts desc"

result1 = dbhelp(db_host, db_port, db_user, db_pass, db_db, sql1)

content += '<h3>实例维度的慢查询分布统计</h3>'
content += '<table border="1" border="0" cellspacing="0" cellpadding="0">'

content += '<tr>'
content += '<th>实例名</th>'
content += '<th>总次数</th>'
content += '<th>总时间</th>'
content += '<th>总Lock时间</th>'
content += '<th>总发送行数</th>'
content += '<th>总检测行数</th>'
content += '<th>最慢执行时间</th>'
content += '<th>最小执行时间</th>'
content += '</tr>'

for m in result1:
    content += '<tr>'
    content += '<td>'+str(m[0])+'</td>'
    content += '<td>'+str(m[1])+'</td>'
    content += '<td>'+str(m[2])+'</td>'
    content += '<td>'+str(m[3])+'</td>'
    content += '<td>'+str(m[4])+'</td>'
    content += '<td>'+str(m[5])+'</td>'
    content += '<td>'+str(m[6])+'</td>'
    content += '<td>'+str(m[7])+'</td>'
    content += '</tr>'

content += '</table>'

content += '</br>'
content += '</br>'
content += '<hr>'
content += '<h3>Top 20 慢sql(过滤掉拉数据SQL)</h3>'
content += '<br>'

sql3 = "select  sum(cnt) as cnts, round(sum(query_time_sum),2) as query_time_sum,round(max(max_query_time),2) as max_query_time, round(min(min_query_time),2) as min_query_time, fingerprint, query_string_orig,check_sum from nice_slow_log_parse where q_exec_time>="
sql3 += "'" + fromtimestr + "' and q_exec_time<="
sql3 += "'" + endtimestr  + "'and check_sum not in (select filter_key from nice_slow_log_filter) group by check_sum order by cnts desc limit 20"

result3 = dbhelp(db_host, db_port, db_user, db_pass, db_db, sql3)
for n in result3:
   content += '<p>   checksum: '+str(n[6])+'</p>'
   content += '<p>     总次数: '+str(n[0])+'</p>'
   content += '<p>     总时间: '+str(n[1])+'</p>'
   content += '<p>   最慢时间: '+str(n[2])+'</p>'
   content += '<p>   最快时间: '+str(n[3])+'</p>'
   content += '<p>Fingerprint: '+str(n[4])+'</p>'
   content += '<p>最慢原始SQL: '+str(n[5])+'</p>'
   content += '<hr>'

## footer 
content += ''' 
    </body>
</html>
'''



send_mail(content, to_list, subject)
