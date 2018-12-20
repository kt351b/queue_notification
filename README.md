# queue_notification
queue e-mail notification
If there are callers in queue with waittime more then 1 minute, the script will send an e-mail notification.
Tested on Asterisk 14.7.7 version, but it must be compatible with another Asterisk versions also. Tested with puthon 2.7 and 3.5
How to use:
- by crontab
- or call it from Asterisk dialplan with System():
exten => 222,n,System(python /opt/astsc.py)
