#!/usr/bin/python
# -*- coding: utf-8

import os
import smtplib
import datetime
import logging
from logging.handlers import WatchedFileHandler
import sys

# ----- logger settings:
logger = logging.getLogger()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# ---- syslog file settings:
fh = logging.handlers.WatchedFileHandler('/var/log/asc.log')
# For log-file output use logging.INFO to write to log
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(fh)

# queue name
queue = 'tech-support'
# from what waittime send e-mail
max_waittime = 1

# get waittime in queue
get_waittime = """ asterisk -x 'queue show %s' | grep wait | awk '{print $4}' | awk -F ':' '{print $1}'""" %(queue)
waittime = os.popen(get_waittime).read().rsplit('\n')
waittime = filter(None, waittime)
waittime = [int(i) for i in waittime]
if max(waittime or [0]) >= max_waittime:
    logging.info("waittime is more then 1 minute: {}".format(waittime) )
    # get quantity of calls in queue
    calls_num = """asterisk -x 'queue show %s' | grep %s | awk '{print $3}'""" % (queue, queue)
    calls = os.popen(calls_num).read()
    #logging.info("calls_num: {}".format(calls_num) )
    #logging.info("calls: {}".format(calls) )
    dict_chan = {} 
    #get channels list with waittime 
    channels = {}
    get_channels = """ asterisk -x 'queue show %s' | grep wait | awk '{print $2, $4}'""" %(queue)
    #logging.info("get_channels: {}".format(get_channels) )
    channels = os.popen(get_channels).read().rsplit('\n')
    channels = filter(None, channels)
    logging.info("channels: {}".format(channels) )
    #compose dict_chan[channels]=waittime
    for i in channels:
        i = i.split()
        dict_chan[''.join(i[0])]=''.join(i[1])
    logging.info("channels: {}".format(dict_chan) )
    # get number of callers, using channels:
    lst = [i for i in dict_chan]
    str_grep = ""
    try:
        for i in range(1, len(lst)-1):
            str_grep = str_grep+"%s\\|" % lst[i]
        st = "| grep \"%s\\|" % lst[0]
        str_grep = " asterisk -x 'core show channels concise'" + st + str_grep + "%s\"" % lst[len(lst)-1]
        #asterisk -x 'core show channels concise'| grep "SIP/656148136-000945aa\|SIP/921-000945a6"
        logging.info("str_grep: {}".format(str_grep) )
        # get callerid:
        chan_lst = os.popen(str_grep).read().rsplit('\n')
        chan_lst = filter(None, chan_lst)
        for i in chan_lst:
            i = i.split('!')
            tmp = dict_chan.get(i[0]).split(',')
            del tmp[1]
            tmp.append(i[7])
            dict_chan[i[0]] = tmp
        #compose text for message:
        callers_message = ''
        for i in dict_chan:
            a = ''
            a = '%-10s %15s \n' %(dict_chan.get(i)[1], dict_chan.get(i)[0])
            callers_message = callers_message + a
        current_time = datetime.datetime.now().strftime("%Y-%m-%d (%A) %H:%M")
        sender = 'fax-server@some.net.ua'
        # receivers templates:
        #receivers = ['admin@some.net','someone@some.net']
        receivers = ['admin@some.net']
        
        message = """From: fax-server<fax-server@some.net>
To: admin <admin@some.net>
Subject: %s calls in queue
At %s there is/are calls with more then 1 minute waiting in queue.
queue %s has %s calls
abonent is waiting for (min:sec):
%s
""" % (calls.rstrip('\n') , current_time, queue, calls.rstrip('\n'), callers_message)
        logging.info("message: {}".format(message) )
        try:
            smtpObj = smtplib.SMTP('smtp.some.net.ua')
            smtpObj.sendmail(sender, receivers, message)
            logging.info("Succesfully send mail")
            logging.info("END OF SCRIPT --------------------")
        except smtplib.SMTPException:
            logging.info("Error: unable to send email")
            logging.info("END OF SCRIPT --------------------")
    except IndexError:
        sys.exit()
