#!/usr/bin/python
# -*- coding: utf-8

import os
import smtplib
import datetime

# Set queue name
queue = 'tech-support'
# Flag to send e-mail
send_flag = 0

# Get string - "queue tech-support has N calls"
get_calls_quant = """asterisk -x 'queue show %s' | grep %s | awk '{print $1, $2, $3, $4}'""" % (queue, queue)
#calls_quant = os.popen(get_calls_quant).read()[0:1]
calls_quant = os.popen(get_calls_quant).read()
# For testing at local machine:
#calls_quant = os.popen("cat /path_to_file/test_queue | grep queue-921 | awk '{print $1, $2, $3, $4}'").read()

# Get waiting in queue callers ChannelID
callers_list = {}
get_callers = """asterisk -x 'queue show %s' | grep wait | awk '{print $2}'""" % (queue)
SIP_list = os.popen(get_callers).read()
# For testing at local machine:
#SIP_list = os.popen("cat /path_to_file/test_queue | grep wait | awk '{print $2}'").read()
SIP_list = SIP_list.splitlines()
k = 0
for i in SIP_list:
    SIP_list[k] = i[0:-2]
    k += 1

# Get callers telephone numbers, using CallerID from "asterisk show queue queue_name":
for channel in SIP_list:
    get_callerid = """asterisk -x 'core show channels verbose' | grep %s | grep %s | awk '{print $8, $9}'""" % (queue, channel)
    # For testing at local machine:
    #get_callerid = """cat /path_to_file/test_channel | grep %s | grep %s | awk '{print $8, $9}'""" % (queue, channel)
    callers = os.popen(get_callerid).read().split('\n')
    del callers[-1]
    for i in callers:
        i = i.split()
        value = callers_list.get(i[0])
        if value:
            value.append(i[1])
            callers_list[i[0]] = value
        else:
            callers_list[i[0]] = i[1].split()


# Delete same waittime values in callers_list dictionary
# and set send_flag if waittime is more then 1 minute
def del_same(dic, send_flag):
    for i in dic:
        lst = []
        for k in dic[i]:
            if k not in lst:
                lst.append(k)
                if int(k[-5:-3]) >=1:
                    send_flag = 1
        dic[i] = lst
    return dic, send_flag


callers_list, send_flag = del_same(callers_list, send_flag)

if send_flag >= 1:
    # Set sender and receivers for e-mail:
    sender = 'info@domain.net'
    receivers = ['admin@domain.net', 'voip@domain.net']
    # Compose callers numbers and waititme for message:
    callers_message = ''
    for i in callers_list:
        a = ''
        for k in callers_list[i]:
            a = '%s \t\t %s \n' % (i, k[3:])
            callers_message = callers_message + a
    current_time = datetime.datetime.now().strftime("%Y-%m-%d (%A) %H:%M")
    # This is not an indent error, message should be written with such indents
    message = """From: info<info@domain.net>
To: admin <admin@domain.net>
Subject: calls in queue
At %s there is/are calls with more then 1 minute waiting in queue.
%s 
caller is waiting for (min:sec):
%s
""" % (current_time, calls_quant.rstrip('\n'), callers_message)
    try:
        smtpObj = smtplib.SMTP('smtp.domain.net')
        smtpObj.sendmail(sender, receivers, message)
        print("Successfully sent email")
    except smtplib.SMTPException:
        print("Error: unable to send email")