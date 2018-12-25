# queue_notification
queue e-mail notification
If there are callers in queue with waittime more then 1 minute, script will send an e-mail notification.
Tested on Asterisk 14.7.7 version, but it must be compatible with another Asterisk versions also. Tested with python 2.7 and 3.5
How to use:
- by crontab
- or call it from Asterisk dialplan with System() application:
exten => 222,n,System(python /path/astsc.py)
How it works:
1) Get caller's ChannelID and waititme by "asterisk -x 'queue show tech-support'"
2) Get CallerId (actually - phone number), using ChannelID from previous command by "asterisk -x 'core show channels verbose'"
3) Check if wait time is more then 1 minute, if at least one waittime is more then 1 minute - send a mail.
How to test:
I use bash command for getting info from Asterisk, such commands as:
- asterisk -x 'queue show tech-support' | grep tech-support | awk '{print $1, $2, $3, $4}
- asterisk -x 'queue show tech-support' | grep wait | awk '{print $2}
- asterisk -x 'core show channels verbose' | grep tech-support | grep SIP/656148136-000705 | awk '{print $8, $9}'
replased tech-support and SIP/656148136-000705 by variables in script.
The output of this two last commands put in files: test_queue and test_channel. I attached those two files to Github. Now you can test this script at your local machine without calling Asterisk from CLI.
