#! /bin/bash
cat /dev/null  > /home/quicklink/mysite/view_bts.log
nohup python /home/quicklink/mysite/gencase/view_bts.py > /home/quicklink/mysite/view_bts.log 2>&1 & 
