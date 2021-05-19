import os, sys
import json
# import logger
import logging
from django.conf.urls import url
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
import json


def testline(request):  
    print('testline init...')
    if 'delete' in request.POST:
        return delete_testline(request)
    elif 'poweroff' in request.POST:
        return poweroff(request)
    elif 'poweron' in request.POST:
        return poweron(request)
    else:
        return HttpResponse(json.dumps({"status": "nok"}), content_type="application/json")

def get_testline():
    from getdata import get_data_by_sql
    field, result = get_data_by_sql('select * from testlinetopo order by testlineid;')
    testline_info_list = []
    for info in result:
        testline_info = {}
        testline_info['testlineid'] = info.testlineid if info.testlineid else ""
        testline_info['entity'] = info.entity if info.entity else ""
        testline_info['btsid'] = info.btsid if info.btsid else ""
        testline_info['flag'] = info.flag if info.flag else ""
        testline_info['btss1ip'] = info.btss1ip if info.btss1ip else ""
        testline_info['btspc'] = info.btspc if info.btspc else ""
        testline_info['pbinfo'] = info.pbinfo if info.pbinfo or info.pbinfo != 'None' else ""
        testline_info['painfo'] = info.painfo if info.painfo or info.painfo != 'None' else ""
        testline_info['papc'] = info.papc if info.papc or info.papc != 'None' else "&nbsp;"
        testline_info['uetype'] = info.uetype if info.uetype or info.uetype != 'None' else ""
        testline_info['uelist'] = info.uelist if info.uelist or info.uelist != 'None' else ""
        testline_info['uepc'] = info.uepc if info.uepc or info.uepc != 'None' else ""
        testline_info['mcsinfo'] = info.mcsinfo if info.mcsinfo or info.mcsinfo != 'None' else ""
        testline_info['mcspc'] = info.mcspc if info.mcspc or info.mcspc != 'None' else ""
        # testline_info['hwinfo'] = info.hwinfo if info.hwinfo or info.hwinfo != 'None' else ""
        testline_info['hwinfo'] = info.hw_info if info.hw_info != '' else info.hwinfo
        testline_info['owner'] = info.owner if info.owner or info.owner != 'None' else ""
        testline_info['version'] = info.version if info.version or info.version != 'None' else ""
        testline_info_list.append(testline_info)
    return testline_info_list

def search_testline(searchid):
    from getdata import get_data_by_sql
    if searchid.isdigit():
        btsid = searchid
        field, result = get_data_by_sql('select * from testlinetopo where btsid={};'.format(btsid))
        testline_info_list = []
        if result == []:
            return []
        for info in result:
            testline_info = {}
            testline_info['testlineid'] = info.testlineid
            testline_info['btsid'] = info.btsid
            testline_info['entity'] = info.entity
            testline_info['flag'] = info.flag
            testline_info['btss1ip'] = info.btss1ip
            testline_info['btspc'] = info.btspc
            testline_info['pbinfo'] = info.pbinfo
            testline_info['painfo'] = info.painfo
            testline_info['papc'] = info.papc
            testline_info['uetype'] = info.uetype
            testline_info['uelist'] = info.uelist
            testline_info['uepc'] = info.uepc
            testline_info['mcsinfo'] = info.mcsinfo
            testline_info['mcspc'] = info.mcspc
            # testline_info['hwinfo'] = info.hwinfo
            testline_info['hwinfo'] = info.hw_info if info.hw_info != '' else info.hwinfo
            testline_info['owner'] = info.owner
            testline_info['version'] = info.version
            if "other:"in info.uetype:
                testline_info['other_uetype'] = info.uetype.split(":")[1]
            else:
                testline_info['other_uetype'] = ""
            testline_info_list.append(testline_info)
    return testline_info_list

def search_testline2(searchid):
    from getdata import get_data_by_sql
    print('search testline {}'.format(searchid))
    if searchid.isdigit():
        testlineid = searchid
        field, result = get_data_by_sql('select * from testlinetopo where testlineid={};'.format(testlineid))
        testline_info_list = []
        if result == []:
            return []
        for info in result:
            testline_info = {}
            testline_info['testlineid'] = info.testlineid
            testline_info['btsid'] = info.btsid
            testline_info['entity'] = info.entity
            testline_info['flag'] = info.flag
            testline_info['btss1ip'] = info.btss1ip
            testline_info['btspc'] = info.btspc
            testline_info['pbinfo'] = info.pbinfo
            testline_info['painfo'] = info.painfo
            testline_info['papc'] = info.papc
            testline_info['uetype'] = info.uetype
            testline_info['uelist'] = info.uelist
            testline_info['uepc'] = info.uepc
            testline_info['mcsinfo'] = info.mcsinfo
            testline_info['mcspc'] = info.mcspc
            # testline_info['hwinfo'] = info.hwinfo
            testline_info['hwinfo'] = info.hw_info if info.hw_info != '' else info.hwinfo
            testline_info['owner'] = info.owner
            testline_info['version'] = info.version
            if "other:"in info.uetype:
                testline_info['other_uetype'] = info.uetype.split(":")[1]
            else:
                testline_info['other_uetype'] = ""
            testline_info_list.append(testline_info)
    return testline_info_list

def delete_testline(request):
    print('delete testline info...')
    from getdata import run_sql
    btsid = str(request.POST['btsid'])
    run_sql('delete from testlinetopo where btsid={};'.format(btsid))
    return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")

def view_testline_get(request):   
    if 'searchid' in request.GET and request.GET['searchid'] != "":
        print('search testline get...')
        searchid = request.GET['searchid']
        print(searchid)
        testline_info_list = search_testline(searchid)
    else:
        print('view testline get...')
        testline_info_list = get_testline()
    context = {}
    context['testline_info'] = testline_info_list
    context['testline_num'] = len(testline_info_list)
    # print(testline_info_list)
    return render(request, "testline.html", context)

def poweroff(request):
    btsid = str(request.POST['btsid'])
    pbinfo = str(request.POST['pbinfo'])
    print('poweroff bts id...{}'.format(btsid))
    # pbinfo = get_pbinfo(btsid)
    print('poweroff bts pb info...{}'.format(pbinfo))
    if pbinfo == '' or pbinfo == 'None':
        info = "BTS PB info is null!"
        return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")
    if ":" not in pbinfo:
        info = "BTS PB info not has port info!"
        return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")    
    from pettool import power_control_for_facom
    try:
        power_control_for_facom('OFF', pbinfo)
        info = "Poweroff BTS Success!"
    except Exception as E:
        print('Error: {}'.format(E))
        info = "Cannot Poweroff BTS!"
    return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")

def poweron(request):
    btsid = str(request.POST['btsid'])
    pbinfo = str(request.POST['pbinfo'])
    print('poweron bts id...{}'.format(btsid))
    # pbinfo = get_pbinfo(btsid)
    print('poweron bts pb info...{}'.format(pbinfo))
    if pbinfo == '':
        info = "BTS PB info is null!"
        return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")
    from pettool import power_control_for_facom
    try:
        power_control_for_facom('ON', pbinfo)
        info = "Poweron BTS Success!"
    except Exception as E:
        print('Error: {}'.format(E))
        info = "Cannot Poweron BTS!"
    return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")

