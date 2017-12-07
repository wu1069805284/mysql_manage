#!/usr/bin/env python
#coding=utf-8

import MySQLdb
import datetime
import time
import sys
import smtplib
from email.mime.text import MIMEText
reload(sys)
sys.setdefaultencoding('utf-8')

smtp_host = 'smtp.exmail.qq.com:465'
mail_user = 'op-robot@oneniceapp.com'
mail_pass = 'opRobot@2017'

dbuser = ""
dbpass = ""
dbencode = "UTF8"
dbport   = 3306
dbhost   = "127.0.0.1"
dbname   = "db_stats"

to_list = ['op@app.com','nice-server@oneniceapp.com']

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


def main():
	datatime = time.strftime('%Y-%m-%d')
    ## select a.groupname,a.dbname,b.dbsizes,b.status from db_groups_meta a  left join db_backup_history b  on b.dbnames=a.dbname and  b.backdate='2015-10-26' where a.dbname !='';
	sql  = "select a.groupname, a.dbname, b.dbsizes, b.status, UNIX_TIMESTAMP(b.endtime)-UNIX_TIMESTAMP(b.starttime) as usedtime from db_groups_meta a left join db_backup_history b on b.dbnames=a.dbname and  b.backdate="	
	sql += "'"
	sql += datatime + "'"
	sql += " WHERE a.dbname !=''"
	try:
		conn = MySQLdb.connect(host     = dbhost,
								port     = dbport,
                               user     = dbuser,
                               passwd   = dbpass,
                               charset  = dbencode,
							   db       = dbname,
                               connect_timeout = 3)
		curs = conn.cursor()
		curs.execute(sql)
		conn.commit()
		res = curs.fetchall()
		curs.close()
		conn.close()

		## 标题
		now = int(time.time())
		todaystr = time.strftime("%Y-%m-%d", time.localtime(now))
		subject = 'MySQL 备份日报 '+todaystr
		
		## 内容
		## header
		content='''
<html>
    <head>
        <title>MySQL 备份日报</title>
        <style type="text/css">
            table{border:1px solid #66B3FF }
        </style>
    </head>
    <body>
'''
		## body title
		content += '<h1>MySQL 备份日报-'+todaystr+'</h1>'
		content += '<hr>'
		content += '<table border="1" border="0" cellspacing="0" cellpadding="0">'
		content += '<tr>'
		content += '<th>集群名称</th>'
		content += '<th>dbnames</th>'
		content += '<th>库大小</th>'
		content += '<th>备份状态</th>'
		content += '<th>备份用时</th>'
		content += '</tr>'

		for key in res:
			#print key[0],key[1],key[2],key[3],key[4]
			content += '<tr>'
			content += '<td>'+str(key[0])+'</td>'
			content += '<td>'+str(key[1])+'</td>'
			content += '<td>'+str(key[2])+'</td>'
			if key[3] >=2:
				content += '<td>'+'OK'+'</td>'
				content += '<td>'+str(key[4])+'秒</td>'
			else:
				content += '<td>'+'Failed'+'</td>'
				content += '<td>'+'None'+'</td>'
		content += '</table>'
		content += '</br>'
		content += '</br>'
		content += '<hr>'

		## footer
		content += '''
    </body>
</html>
'''
		send_mail(content, to_list, subject)
	except MySQLdb.Error,e:
		print "MySQLdb Error",e


main()




