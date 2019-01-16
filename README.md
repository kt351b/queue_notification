# queue_notification
queue e-mail notification

If there are callers in queue with waittime more then 1 minute, script will send an e-mail notification.
Tested on Asterisk 14.7.7 version, but it must be compatible with another Asterisk versions also. 
Tested with python 2.7

How to use:
- by crontab
- or call it from Asterisk dialplan with System() application:
exten => 222,n,System(python /path/queue_notificator.py)

How it works:
1) Get waittime from queue (" asterisk -x 'queue show queue-name' | grep wait | awk '{print $4}' | awk -F ':' '{print $1}' ") and put it to waittime list
2) Chech is there a value with waittime more then 1 minute (by defult, you can set required waittime by min_waittime variable) 
3) Get caller's ChannelID and waititme by " asterisk -x 'queue show queue-name' | grep wait | awk '{print $2, $4}' "
2) Get CallerId (actually - phone number), using ChannelID from previous command by " asterisk -x 'core show channels concise'| grep "ChannelID1\|ChannelID2" "
3) Compose and send a e-mail.

Working principle diagram
![e-mail_pub](https://user-images.githubusercontent.com/37866374/51247963-577bd480-1997-11e9-8a16-bf05d799bd18.png)
