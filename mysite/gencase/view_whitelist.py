#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
import json
# import logger
import logging
from django.conf.urls import url
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
import json

filename_dir = './templates/txt/'

def white_list(request):  
    print('check btslog init...')
    if 'check' in request.POST:
        return check(request)
    else:
        return HttpResponse(json.dumps({"status": "nok"}), content_type="application/json")


def get_whitelist():
    import csv
    # url = 'https://nokia.sharepoint.com/sites/MN_FM_Process/ERR_WRN/SitePages/Home.aspx'
    whitelist_dict = dict()
    filename = './templates/txt/whitelist.csv'
    with open(filename) as csvfile:
        readcsv = csv.reader(csvfile)
        for row in readcsv:
            if "Regular expression" in row[0]:
                continue
            key = row[0]
            reason = row[2]
            whitelist_dict[key] = reason
    print(whitelist_dict)
    return whitelist_dict

whitelist_dict = {
    'AaSyslog buffer \d+ \(\w+\) reached LoadLevel2 , Info, Warning, Error and Vip logs will be accepted':
    'valid prints - appear due to extensive logging',

    'dhcpd:.*': 
    'Pronto agreed as CNN',

    'AaSyslog buffer \d+ \(\w+\) reached LoadLevel3 , Error and Vip logs will be accepted':
    'valid prints - appear due to extensive logging',

    'buffer LoadLevel3 : ERR and VIP logs will be accepted':
    'valid prints - appear due to extensive logging',

    'kernel: \[\s*\d+\.\d+\] EXT4-fs \(sda\d\): warning: maximal mount count reached, running e2fsck is recommended':
    'Standard linux check ',

    'extSrioPortStateControl:.*SFP absent':
    'OAM periodically tries to open connection to other SM in if no SRIO SFP present this warning occurs.',

    'rsyslogd:.*try http://www.rsyslog.com/e/2027':
    'valid prints - appear due to RAM access error',

    'WRN/Ne3sAdapter/Common, Fetch MO:/PNP_CONTEXT-\d+ of fragment:INTERNAL from DB failed!':
    'Pronto agreed as CNN',

    'ERR/Common/CommonFaultEvent.cpp#\d+, LOM_FaultInd is preparing to send':
    'Configuration Error',

    'ERR/DCS/BBConf, LogicalLinks::AntennaResourcesAllocator Filtered out all devices':
    'Pronto agreed as CNN',

    'ERR/macps.ul.pre.msr|enb:* cell:*|setRachParams() config error, PRACH overlapping with PUCCH':
    'Configuration Error',

    'CC-TupSocketThread WRN/TUPC/TupcSctpCantStrAssocHandler.cpp':
    'Configuration Error'


}
def check(request):
    import re
    print('check init...')
    # reload(sys)
    # sys.setdefaultencoding("utf8")
    btslog = request.POST['input']
    # whitelist_dict = get_whitelist()
    # print(btslog)
    output = ''
    line_list = []
    white_print = []
    for line in btslog.split('\n'):
        for key in whitelist_dict:
            if re.search(key, str(line)):
                output += line + '-----' + whitelist_dict[key] + '\n'
                line_list.append(line)
                white_print.append(whitelist_dict[key])
    print(output)
    return HttpResponse(json.dumps({"status": "ok", "output": output, "linelist": line_list, "whiteprint": white_print}), content_type="application/json")
