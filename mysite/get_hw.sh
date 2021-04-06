#!/bin/bash

rm -rf /home/quicklink/mysite/get_hw.log
nohup python3 /home/quicklink/mysite/gencase/get_hw.py > /home/quicklink/mysite/get_hw.log 2>&1 & 
