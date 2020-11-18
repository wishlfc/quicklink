import os, sys
import json
# import logger
import logging
from django.conf.urls import url
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
import json


def testlinechange(request):  
    print('testline change init...')
    if 'update' in request.POST:
        return update_testline(request)
    else:
        return HttpResponse(json.dumps({"status": "nok"}), content_type="application/json")

def view_testlinechange_get(request):  
    print('view testline info...')
    from view_testline import search_testline
    url = request.build_absolute_uri()
    print(url)
    if 'btsid' in url:
        btsid = url.split('btsid=')[1].split('&')[0]
        if btsid == '':
            testline_info = {}
            newtestlineid = str(int(count_testline()) + 1)
            testline_info['testlineid'] = newtestlineid
        else:
            testline_info = search_testline(btsid)[0]
        context = {}
        context['info'] = testline_info
        print(testline_info)
        return render(request, "testlinechange.html", context)


def insert_testline(request):
    print('insert testline info...')
    from getdata import run_sql
    testlineid = str(request.POST['testlineid'])
    btsid = str(request.POST['btsid'])
    flag = str(request.POST['flag'])
    entity = str(request.POST['entity'])
    btss1ip = str(request.POST['btss1ip'])
    btspc = str(request.POST['btspc'])
    pbinfo = str(request.POST['pbinfo'])
    painfo = str(request.POST['painfo'])
    papc = str(request.POST['papc'])
    uetype = str(request.POST['uetype'])
    uelist = str(request.POST['uelist'])
    uepc = str(request.POST['uepc'])
    mcspc = str(request.POST['mcspc'])
    mcsinfo = str(request.POST['mcsinfo'])
    hwinfo = str(request.POST['hwinfo'])
    owner = str(request.POST['owner'])
    key = "testlineid, btsid, flag, entity, btss1ip, btspc, pbinfo, painfo, papc, uetype, uelist, uepc, mcsinfo, mcspc, hwinfo, owner"
    cmd = 'insert into testlinetopo({}) values("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}");'.format(
        key, testlineid, btsid, flag, entity, btss1ip, btspc, pbinfo, painfo, papc, uetype, uelist, uepc, mcsinfo, mcspc, hwinfo, owner)
    print(cmd)
    run_sql(cmd)
    return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")

def count_testline():
    from getdata import get_data_from_sql
    # result = get_data_from_sql('select count(*) from testlinetopo;')
    result = get_data_from_sql('select testlineid from testlinetopo order by testlineid desc limit 1;')
    return result[0]


def update_testline(request):
    print('update testline info...')
    from getdata import get_data_by_sql
    # btsid = str(request.POST['btsid'])
    # field, result = get_data_by_sql('select * from testlinetopo where btsid="{}";'.format(btsid))
    testlineid = str(request.POST['testlineid'])
    field, result = get_data_by_sql('select * from testlinetopo where testlineid="{}";'.format(testlineid))
    if result == []:
        return insert_testline(request)
    else:
        return edit_testline(request)

def edit_testline(request):
    print('edit testline info...')
    btsid = str(request.POST['btsid'])
    testlineid = str(request.POST['testlineid'])
    entity = str(request.POST['entity'])
    flag = str(request.POST['flag'])
    btss1ip = str(request.POST['btss1ip'])
    btspc = str(request.POST['btspc'])
    pbinfo = str(request.POST['pbinfo'])
    painfo = str(request.POST['painfo'])
    papc = str(request.POST['papc'])
    uetype = str(request.POST['uetype'])
    uelist = str(request.POST['uelist'])
    uepc = str(request.POST['uepc'])
    mcspc = str(request.POST['mcspc'])
    mcsinfo = str(request.POST['mcsinfo'])
    hwinfo = str(request.POST['hwinfo'])
    owner = str(request.POST['owner'])
    cmd = 'update testlinetopo set '
    # keylist = ['testlineid', 'flag', 'entity', 'btss1ip', 'btspc', 'pbinfo', 'painfo', 'papc', 'uetype', 'uelist', 'uepc', 'mcsinfo', 'mcspc', 'hwinfo', 'owner']
    # valuelist = [testlineid, flag, entity, btss1ip, btspc, pbinfo, painfo, papc, uetype, uelist, uepc, mcsinfo, mcspc, hwinfo, owner]
    keylist = ['btsid', 'flag', 'entity', 'btss1ip', 'btspc', 'pbinfo', 'painfo', 'papc', 'uetype', 'uelist', 'uepc', 'mcsinfo', 'mcspc', 'hwinfo', 'owner']
    valuelist = [btsid, flag, entity, btss1ip, btspc, pbinfo, painfo, papc, uetype, uelist, uepc, mcsinfo, mcspc, hwinfo, owner] 
    for i in range(len(keylist)):
        if i == len(keylist) - 1:
            cmd += keylist[i] + "=" + '"' + valuelist[i] + '" '
        else:
            cmd += keylist[i] + "=" + '"' + valuelist[i] + '",'
    # cmd += 'where btsid={};'.format(btsid)
    cmd += 'where testlineid={};'.format(testlineid)
    from getdata import run_sql
    print(cmd)
    run_sql(cmd)
    return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")
