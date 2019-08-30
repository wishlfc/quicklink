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
import time

sys.path.append('/home/work/tacase_dev/Resource')
filename_dir = './templates/txt/'
remote_ip = '10.106.214.206'
remote_folder = '/home/amy/temp/'

def view_bts(request):
    print('view bts init...')
    if 'add' in request.POST:
        return add(request)
    if 'addrru' in request.POST:
        return addrru(request)
    elif 'query' in request.POST:
        return query(request)
    elif 'modify' in request.POST:
        return modify(request)
    elif 'delete' in request.POST:
        return delete(request)
    elif 'search' in request.POST:
        return search(request)
    elif 'getstatus' in request.POST:
        return getstatus(request)
    elif 'savescf' in request.POST:
        return save_scf(request)
    elif 'savesnapshot' in request.POST:
        return save_snapshot(request)
    elif 'saveswconfig' in request.POST:
        return save_swconfig(request)
    elif 'block' in request.POST:
        return block(request)
    elif 'unblock' in request.POST:
        return unblock(request)
    elif 'reboot' in request.POST:
        return reboot(request)
    elif 'block_all_rru' in request.POST:
        return block_all_rru(request)
    elif 'unblock_all_rru' in request.POST:
        return unblock_all_rru(request)
    elif 'block_all_cell' in request.POST:
        return block_all_cell(request)
    elif 'unblock_all_cell' in request.POST:
        return unblock_all_cell(request)
    elif 'poweroff' in request.POST:
        return poweroff(request)
    elif 'poweron' in request.POST:
        return poweron(request)
    elif 'good_night' in request.POST:
        return good_night(request)
    elif 'lock' in request.POST:
        return lock(request)
    elif 'unlock' in request.POST:
        return unlock(request)
    elif 'get_project' in request.POST:
        return get_project(request)
    elif 'run_project' in request.POST:
        return run_project(request)
    else:
        return HttpResponse(json.dumps({"status": "nok"}), content_type="application/json")

def get_job_bts():
    import requests
    cmd = "ls /home/jenkins/home/jobs/"
    remote_cmd = 'sshpass -p root ssh root@10.69.82.130 "{}"'.format(cmd)
    out = os.popen(remote_cmd).read()
    # print(out)
    jobdict = {}
    for job in out.split('\n'):
        if job == "":
            continue
        url = "http://10.69.82.129/job/{}/config.xml".format(job)
        print(url)
        headers = {'User-Agent':
                   'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
        r = requests.get(url, auth=("admin", "admin123"), verify=True,
                         headers=headers)
        if r.status_code == 200:
            lines = r.content
        else:
            continue
        # print(lines)
        lines = [x for x in lines.split('\n') if x.strip() and x[0] != '#']
        bts = [x for x in lines if 'master_bts' in x.lower()]
        bts = bts[0].split('=')[-1].replace('\n', '') if bts else ''
        if bts == '' or bts.isdigit() == False:
            continue
        if jobdict.has_key(bts):
            jobdict[bts] += ',' + job
        else:
            jobdict[bts] = job
        change_joblist(bts, jobdict[bts])
    print jobdict
    return jobdict

def insert_btsinfo(btsid, btsip, issran, pbinfo, group, lock, powerstatus):
    from getdata import run_sql
    hwtype = 'BTS'
    run_sql('insert into btstable(btsid,btsip,sran,pbinfo,`group`,`lock`,`powerstatus`,`hwtype`) values({},"{}",{},"{}","{}","{}","{}","{}");'.format(int(btsid), btsip, int(issran), pbinfo, group, lock, powerstatus,hwtype))

def insert_rruinfo(btsid, btsip, issran, pbinfo, group, lock, powerstatus):
    from getdata import run_sql
    hwtype = 'RRU'
    run_sql('insert into btstable(btsid,btsip,sran,pbinfo,`group`,`lock`,`powerstatus`,`hwtype`) values({},"{}",{},"{}","{}","{}","{}","{}");'.format(int(btsid), btsip, int(issran), pbinfo, group, lock, powerstatus,hwtype))

def delete_btsinfo(btsid):
    from getdata import run_sql
    run_sql('delete from btstable where btsid={};'.format(btsid))

def search_joblist(btsid):
    from getdata import get_data_by_sql
    field, result = get_data_by_sql('select `joblist` from btstable where btsid={};'.format(btsid))
    if result == []:
        return ""
    else:
        if result[0].joblist == 'NULL':
            return ""
        jobstr = result[0].joblist
        return jobstr

def search_btsinfo(searchid):
    from getdata import get_data_by_sql
    bts_group_list = []
    if searchid.isdigit():
        btsid = searchid
        field, result = get_data_by_sql('select * from btstable where btsid={};'.format(btsid))
        bts_info_list = []
        bts_info = {}
        if result == []:
            return [], []
        bts_info['btsid'] = result[0].btsid
        bts_info['btsip'] = result[0].btsip
        bts_info['powerstatus'] = result[0].powerstatus
        bts_info['lock'] = result[0].lock
        bts_info['group'] = result[0].group
        bts_info['version'] = result[0].version
        bts_info['powerstatus'] = result[0].powerstatus
        bts_info['status'] = result[0].status
        bts_info['hwtype'] = result[0].hwtype
        bts_info_list.append(bts_info)
        if result[0].group not in bts_group_list:
            bts_group_list.append(result[0].group)
        return bts_info_list, bts_group_list
    else:
        group = searchid.upper()
        field, result = get_data_by_sql('select * from btstable where `group`="{}";'.format(group))
        bts_info_list = []
        bts_group_list = []
        if result == []:
            return [], []
        for line in result:
            bts_info = {}
            bts_info['btsid'] = line.btsid
            bts_info['btsip'] = line.btsip
            bts_info['powerstatus'] = line.powerstatus
            bts_info['lock'] = line.lock
            bts_info['group'] = line.group
            bts_info['version'] = line.version
            bts_info['powerstatus'] = line.powerstatus
            bts_info['status'] = line.status
            bts_info['hwtype'] = line.hwtype
            bts_info_list.append(bts_info)
            if line.group not in bts_group_list:
                bts_group_list.append(line.group)
        return bts_info_list, bts_group_list


def check_btsid(btsid):
    from getdata import get_data_by_sql
    field, result = get_data_by_sql('select * from btstable where btsid={};'.format(btsid))
    bts_info_list = []
    for bts in result:
        bts_info = {}
        bts_info['btsid'] = bts.btsid
        bts_info['btsip'] = bts.btsip
        bts_info['sran'] = bts.sran
        bts_info['pbinfo'] = bts.pbinfo
        bts_info['powerstatus'] = bts.powerstatus
        bts_info['version'] = bts.version
        bts_info['status'] = bts.status
        bts_info['group'] = bts.group
        bts_info['hwtype'] = bts.hwtype
        bts_info_list.append(bts_info)
    return bts_info_list

def get_pbinfo(btsid):
    from getdata import get_data_by_sql
    field, result = get_data_by_sql('select pbinfo from btstable where btsid={};'.format(btsid))
    return result[0].pbinfo

def get_lock(btsid):
    from getdata import get_data_by_sql
    field, result = get_data_by_sql('select `lock` from btstable where btsid={};'.format(btsid))
    return result[0].lock

def get_btsinfo():
    from getdata import get_data_by_sql
    field, result = get_data_by_sql('select * from btstable;')
    bts_info_list = []
    bts_group_list = []
    for bts in result:
        bts_info = {}
        bts_info['btsid'] = bts.btsid
        bts_info['btsip'] = bts.btsip
        bts_info['lock'] = bts.lock
        bts_info['powerstatus'] = bts.powerstatus
        bts_info['group'] = bts.group
        bts_info['version'] = bts.version
        bts_info['status'] = bts.status
        bts_info['hwtype'] = bts.hwtype
        if bts.group not in bts_group_list:
            bts_group_list.append(bts.group)
        bts_info_list.append(bts_info)
    return bts_info_list, bts_group_list

def modify_btsinfo(btsid, btsip, issran, pbinfo, group):
    key1 = 'btsip'
    value1 = str(btsip)
    key2 = 'sran'
    value2 = int(issran)
    key3 = 'pbinfo'
    value3 = str(pbinfo)
    key4 = 'group'
    value4 = str(group)
    from getdata import run_sql
    cmd = 'update btstable set {}="{}" where btsid={};'.format(key1, value1, btsid)
    print(cmd)
    run_sql(cmd)
    cmd = 'update btstable set {}={} where btsid={};'.format(key2, value2, btsid)
    print(cmd)
    run_sql(cmd)
    cmd = 'update btstable set {}="{}" where btsid={};'.format(key3, value3, btsid)
    print(cmd)
    run_sql(cmd)
    cmd = 'update btstable set `{}`="{}" where btsid={};'.format(key4, value4, btsid)
    print(cmd)
    run_sql(cmd)

def change_lock(btsid, lock):
    key1 = 'lock'
    value1 = lock
    from getdata import run_sql
    cmd = 'update btstable set `{}`="{}" where btsid={};'.format(key1, value1, btsid)
    print(cmd)
    run_sql(cmd)

def change_powerstatus(btsid, status):
    key1 = 'powerstatus'
    value1 = status
    from getdata import run_sql
    cmd = 'update btstable set `{}`="{}" where btsid={};'.format(key1, value1, btsid)
    print(cmd)
    run_sql(cmd)

def change_refresh_info(btsid, powerstatus, version, status):
    key1 = 'powerstatus'
    value1 = str(powerstatus)
    key2 = 'version'
    value2 = str(version)
    key3 = 'status'
    value3 = str(status)
    from getdata import run_sql
    cmd = 'update btstable set {}="{}" where btsid={};'.format(key1, value1, btsid)
    print(cmd)
    run_sql(cmd)
    cmd = 'update btstable set {}="{}" where btsid={};'.format(key2, value2, btsid)
    print(cmd)
    run_sql(cmd)
    cmd = 'update btstable set {}="{}" where btsid={};'.format(key3, value3, btsid)
    print(cmd)
    run_sql(cmd)

def change_joblist(btsid, jobliststr):
    key1 = 'joblist'
    value1 = jobliststr
    btsid = int(btsid)
    from getdata import run_sql
    cmd = 'update btstable set `{}`="{}" where btsid={};'.format(key1, value1, btsid)
    print(cmd)
    run_sql(cmd)

def view_bts_get(request):   
    if 'searchid' in request.GET and request.GET['searchid'] != "":
        print('search bts get...')
        searchid = request.GET['searchid']
        print(searchid)
        bts_info_list, bts_group_list = search_btsinfo(searchid)
    else:
        print('view bts get...')
        bts_info_list, bts_group_list = get_btsinfo()
    context = {}
    context['bts_info'] = bts_info_list
    context['bts_group_list'] = bts_group_list
    print(bts_info_list)
    return render(request, "btsmgmt.html", context)

def get_time():
    import datetime
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return timestamp

def add(request):    
    btsid = str(request.POST['btsid'])
    btsip = str(request.POST['btsip'])
    issran = str(request.POST['issran'])
    pbinfo = str(request.POST['pbinfo'])
    group = str(request.POST['group']).upper()
    lock = 'off'
    powerstatus = 'on'
    if check_btsid(btsid) == []:
        print('add bts id...{}'.format(btsid))
    else:
        print('bts id is exist...{}'.format(btsid))
        return HttpResponse(json.dumps({"status": "exist"}), content_type="application/json")
    sran = 1 if issran == 'true' else 0
    insert_btsinfo(btsid, btsip, sran, pbinfo, group, lock, powerstatus)
    return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")

def addrru(request):    
    btsid = str(request.POST['rruid'])
    btsip = "0.0.0.0"
    issran = "0"
    pbinfo = str(request.POST['pbinfo'])
    group = str(request.POST['group']).upper()
    lock = 'off'
    powerstatus = 'on'
    if check_btsid(btsid) == []:
        print('add rru id...{}'.format(btsid))
    else:
        print('rru id is exist...{}'.format(btsid))
        return HttpResponse(json.dumps({"status": "exist"}), content_type="application/json")
    sran = 1 if issran == 'true' else 0
    insert_rruinfo(btsid, btsip, sran, pbinfo, group, lock, powerstatus)
    return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")

def query(request):
    btsid = str(request.POST['btsid'])
    print('query bts id...{}'.format(btsid))
    bts_info = check_btsid(btsid)[0]
    btsip = bts_info['btsip']
    sran = bts_info['sran']
    pbinfo = bts_info['pbinfo']
    powerstatus = bts_info['powerstatus']
    version = bts_info['version']
    status = bts_info['status']
    group = bts_info['group']
    bts_info['hwtype'] = line.hwtype
    # print('query bts ip {} sran {}'.format(btsid, sran))
    issran = True if int(sran) == 1 else False
    return HttpResponse(json.dumps({"status": "ok", 'btsip': btsip, 'issran': issran,
                        'pbinfo': pbinfo, 'powerstatus': powerstatus, 'btsstatus': status,
                        'version': version, 'group': group}), content_type="application/json")

def modify(request):
    btsid = str(request.POST['btsid'])
    btsip = str(request.POST['btsip'])
    issran = str(request.POST['issran'])
    pbinfo = str(request.POST['pbinfo'])
    group = str(request.POST['group']).upper()
    sran = 1 if issran == 'true' else 0
    print('modify bts info...{}'.format(btsid))
    modify_btsinfo(btsid, btsip, sran, pbinfo, group)
    return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")

def lock(request):
    btsid = int(request.POST['btsid'])
    lock = "on"
    print('lock bts id...{}'.format(btsid))
    change_lock(btsid, lock)
    return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")

def unlock(request):
    btsid = int(request.POST['btsid'])
    lock = "off"
    print('unlock bts id...{}'.format(btsid))
    change_lock(btsid, lock)
    return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")

def delete(request):
    btsid = str(request.POST['btsid'])
    print('delete bts...{}'.format(btsid)) 
    delete_btsinfo(btsid)
    return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")

def status(api):
    api.connect()
    state = api.ute_admin.get_mrbts_state(alias=api.ute_admin_alias)
    return state

def ping_s1(btsip):
    if btsip == 'NULL' or btsip == '' or  btsip == '0.0.0.0':
        return False
    result = os.popen('ping -c 3 {}'.format(btsip)).read()
    print(result)
    if "100% packet loss" in result or "Invalid argument" in result :
        return False
    return True

def getstatus(request):    
    btsid = str(request.POST['btsid'])
    btsip = str(request.POST['btsip'])
    powerstatus = "on"
    if not ping_s1(btsip):
        btsstatus = "S1 is not Reachable!"
        # change_powerstatus(btsid, "off")
        powerstatus = "off"
        version = "S1 is not Reachable!"
        change_refresh_info(btsid, powerstatus, version, btsstatus)
        return HttpResponse(json.dumps({"status": "ok", "btsstatus": btsstatus,"version":version,"powerstatus":powerstatus}), content_type="application/json")    
    print('get bts status...{}'.format(btsid))
    bts = None
    try:
        bts = admin_api_setup(btsid)
        btsstatus = status(bts.admin_api)
        version = bts.admin_api.get_bts_version()
        print('get bts status {} version {}'.format(btsstatus, version))
        import time
        time.sleep(3)
        # bts.admin_api.teardown()
    except Exception as E:
        print('Error: {}'.format(E))
        btsstatus = "Cannot get info!"
        version = "Cannot get info!"
    finally:
        if bts and bts.admin_api != None:
            bts.admin_api.teardown()
        change_refresh_info(btsid, powerstatus, version, status)
    return HttpResponse(json.dumps({"status": "ok", "btsstatus": btsstatus, "version":version, "powerstatus":powerstatus}), content_type="application/json")

def refresh_bts_info():
    bts_info_list = get_btsinfo()
    for bts_info in bts_info_list[0]:
        btsid = bts_info['btsid']
        btsip = bts_info['btsip']
        btspowerstatus = bts_info['powerstatus']
        btsstatus, btsversion = refresh_status(btsid, btsip)
        if "not Reachable" in btsstatus:
            powerstatus = 'off'
            status = btsstatus
            version = btsversion
        elif "Cannot get info" in btsstatus:
            powerstatus = btspowerstatus
            status = btsstatus
            version = btsversion
        else:
            powerstatus = 'on'
            status = btsstatus
            version = btsversion
        change_refresh_info(btsid, powerstatus, version, status)


def refresh_status(btsid, btsip):    
    print('get bts status...{}'.format(btsid))  
    if not ping_s1(btsip):
        btsstatus = version = "S1 is not Reachable!"
        return btsstatus, version    
    bts = None
    try:
        bts = admin_api_setup(btsid)
        btsstatus = status(bts.admin_api)
        version = bts.admin_api.get_bts_version()
        print('get bts status {} version {}'.format(btsstatus, version))
        import time
        time.sleep(3)
        # bts.admin_api.teardown()
    except Exception as E:
        print('Error: {}'.format(E))
        btsstatus = version = "Cannot get info!"
    finally:
        if bts and bts.admin_api != None:
            bts.admin_api.teardown()
    return btsstatus, version

def block(request):
    btsid = str(request.POST['btsid'])
    btsip = str(request.POST['btsip'])
    if not ping_s1(btsip):
        info = "S1 is not Reachable!"
        change_powerstatus(btsid, "off")
        return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")    
    print('block bts...{}'.format(btsid))
    bts = admin_api_setup(btsid)
    info = bts.admin_api.block_bbu()
    bts.admin_api.teardown()
    info = "bts is block"
    return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")

def unblock(request):
    btsid = str(request.POST['btsid'])
    btsip = str(request.POST['btsip'])
    if not ping_s1(btsip):
        info = "S1 is not Reachable!"
        change_powerstatus(btsid, "off")
        return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")
    print('unblock bts...{}'.format(btsid))
    bts = admin_api_setup(btsid)
    info = bts.admin_api.unblock_bbu()
    bts.admin_api.teardown()
    info = "bts is unblock"
    return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")

def reboot(request):
    btsid = str(request.POST['btsid'])
    btsip = str(request.POST['btsip'])
    if not ping_s1(btsip):
        info = "S1 is not Reachable!"
        change_powerstatus(btsid, "off")
        return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")
    print('reboot bts...{}'.format(btsid))
    bts = None
    try:
        bts = admin_api_setup(btsid)
        info = bts.admin_api.reset_site()
        # bts.admin_api.teardown()
        info = "bts is reboot"
    except Exception as E:
        print('Error: {}'.format(E))
        info = "Cannot reboot bts!"
    finally:
        if bts and bts.admin_api != None:
            bts.admin_api.teardown()
    return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")

def save_scf(request):
    btsid = str(request.POST['btsid'])
    btsip = str(request.POST['btsip'])
    if not ping_s1(btsip):
        info = "S1 is not Reachable!"
        change_powerstatus(btsid, "off")
        return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")
    print('save bts scf...{}'.format(btsid))
    timestamp = get_time()
    local_filename = '/home/quicklink/mysite/temp/scf_bts{}_{}.xml'.format(btsid, timestamp)
    bts = None
    try:
        bts = admin_api_setup(btsid)
        bts.admin_api.get_scf_file_from_bts(local_filename)
        # bts.admin_api.teardown()
        remote_file = remote_folder + local_filename.split('/')[-1]
        os.system('sshpass -p root scp {} root@{}:{}'.format(local_filename, remote_ip, remote_file))
        print(local_filename)
        print(remote_file)
        info = 'http://{}/file/{}'.format(remote_ip, local_filename.split('/')[-1])
    except Exception as E:
        print('Error: {}'.format(E))
        info = "Cannot save scfc!"
    finally:
        if bts.admin_api != None:
            bts.admin_api.teardown()
    return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")

def get_alarm(request):
    btsid = str(request.POST['btsid'])
    btsip = str(request.POST['btsip'])
    if not ping_s1(btsip):
        info = "S1 is not Reachable!"
        change_powerstatus(btsid, "off")
        return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")
    bts = None
    try:
        bts = admin_api_setup(btsid)
        info = bts.admin_api.get_active_alarms()
        # bts.admin_api.teardown()
        print(info)
    except Exception as E:
        print('Error: {}'.format(E))
        info = "Cannot get alarm!"
    finally:
        if bts.admin_api != None:
            bts.admin_api.teardown()
    return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")

def save_snapshot(request):
    btsid = str(request.POST['btsid'])
    btsip = str(request.POST['btsip'])
    if not ping_s1(btsip):
        info = "S1 is not Reachable!"
        change_powerstatus(btsid, "off")
        return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")
    timestamp = get_time()
    local_filename = '/home/quicklink/mysite/temp/snapshot_bts{}_{}.zip'.format(btsid, timestamp)
    bts = None
    try:
        bts = admin_api_setup(btsid)
        bts.admin_api.capture_snapshot(local_filename)
        # bts.admin_api.teardown()
        remote_file = remote_folder + local_filename.split('/')[-1]
        os.system('sshpass -p root scp {} root@{}:{}'.format(local_filename, remote_ip, remote_file))
        info = 'http://{}/file/{}'.format(remote_ip, local_filename.split('/')[-1])
        print(local_filename)
        print(remote_file)
    except Exception as E:
        print('Error: {}'.format(E))
        info = "Cannot save snapshot!"
    finally:
        if bts and bts.admin_api != None:
            bts.admin_api.teardown()
    return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")

def save_swconfig(request):   
    btsid = str(request.POST['btsid'])
    btsip = str(request.POST['btsip'])
    if not ping_s1(btsip):
        info = "S1 is not Reachable!"
        change_powerstatus(btsid, "off")
        return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")
    bts = None
    try:
        sys.path.append('/home/work/tacase_dev/Resource')
        from lib_bts import c_pet_bts_s1
        bts = load_config(btsid)
        bts.s1 = c_pet_bts_s1(bts)
        timestamp = get_time()
        local_filename = '/home/work/temp/bts/swconfig_{}.txt'.format(timestamp)
        bts.s1.download_file(os.sep.join(['/ffs/run', 'swconfig.txt']),
                             local_filename)
        if not os.path.exists(local_filename):
            info = "Download swconfig fail!"
            return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")
        remote_file = remote_folder + local_filename.split('/')[-1]
        os.system('sshpass -p root scp {} root@{}:{}'.format(local_filename, remote_ip, remote_file))
        info = 'http://{}/file/{}'.format(remote_ip, local_filename.split('/')[-1])
        print(local_filename)
        print(remote_file)
    except Exception as E:
        print('Error: {}'.format(E))
        info = "Cannot save swconfig!"
    finally:
        if bts and bts.admin_api != None:
            bts.s1.teardown()
    return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")

def block_all_rru(request):
    btsid = str(request.POST['btsid'])
    bts = None
    from petbase import gv
    try:
        bts = admin_api_setup(btsid)
        gv.master_bts = bts
        from pet_oam import c_pet_oam_manager, parse_oam_commands
        oam_operations = 'block_all_rf'
        command_groups = parse_oam_commands(oam_operations)
        manager = c_pet_oam_manager(command_groups[0].strip())
        if manager.run_oam_command():
            info = "Block all rru Success!"

    except Exception as E:
        print('Error: {}'.format(E))
        info = "Cannot block all rru!"
    finally:
        if bts and bts.admin_api != None:
            bts.admin_api.teardown()
    return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")

def unblock_all_rru(request):
    btsid = str(request.POST['btsid'])
    bts = None
    from petbase import gv
    try:
        bts = admin_api_setup(btsid)
        gv.master_bts = bts
        from pet_oam import c_pet_oam_manager, parse_oam_commands
        oam_operations = 'unblock_all_rf'
        command_groups = parse_oam_commands(oam_operations)
        manager = c_pet_oam_manager(command_groups[0].strip())
        if manager.run_oam_command():
            info = "UnBlock all rru Success!"
    except Exception as E:
        print('Error: {}'.format(E))
        info = "Cannot unblock all rru!"
    finally:
        if bts and bts.admin_api != None:
            bts.admin_api.teardown()
    return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")

def block_all_cell(request):
    btsid = str(request.POST['btsid'])
    bts = None
    from petbase import gv
    try:
        bts = admin_api_setup(btsid)
        gv.master_bts = bts
        from pet_oam import c_pet_oam_manager, parse_oam_commands
        oam_operations = 'block_all_cell'
        command_groups = parse_oam_commands(oam_operations)
        manager = c_pet_oam_manager(command_groups[0].strip())
        if manager.run_oam_command():
            info = "Block all cell Success!"
    except Exception as E:
        print('Error: {}'.format(E))
        info = "Cannot block all cell!"
    finally:
        if bts and bts.admin_api != None:
            bts.admin_api.teardown()
    return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")

def unblock_all_cell(request):
    btsid = str(request.POST['btsid'])
    bts = None
    from petbase import gv
    try:
        bts = admin_api_setup(btsid)
        gv.master_bts = bts
        from pet_oam import c_pet_oam_manager, parse_oam_commands
        oam_operations = 'unblock_all_cell'
        command_groups = parse_oam_commands(oam_operations)
        manager = c_pet_oam_manager(command_groups[0].strip())
        if manager.run_oam_command():
            info = "UnBlock all cell Success!"
    except Exception as E:
        print('Error: {}'.format(E))
        info = "Cannot unblock all cell!"
    finally:
        if bts and bts.admin_api != None:
            bts.admin_api.teardown()
    return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")

def poweroff(request):
    btsid = str(request.POST['btsid'])
    print('poweroff bts id...{}'.format(btsid))
    pbinfo = get_pbinfo(btsid)
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
        change_powerstatus(btsid, "off")
    except Exception as E:
        print('Error: {}'.format(E))
        info = "Cannot Poweroff BTS!"
    return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")

def poweron(request):
    btsid = str(request.POST['btsid'])
    print('poweron bts id...{}'.format(btsid))
    pbinfo = get_pbinfo(btsid)
    print('poweron bts pb info...{}'.format(pbinfo))
    if pbinfo == '':
        info = "BTS PB info is null!"
        return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")
    from pettool import power_control_for_facom
    try:
        power_control_for_facom('ON', pbinfo)
        info = "Poweron BTS Success!"
        change_powerstatus(btsid, "on")
    except Exception as E:
        print('Error: {}'.format(E))
        info = "Cannot Poweron BTS!"
    return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")

def good_night(request):
    btsid_group = str(request.POST['btsid_group'])
    print('good night bts group id...{}'.format(btsid_group))
    success_btslist = ''
    fail_btslist = ''
    locked_btslist = ''
    from pettool import power_control_for_facom
    for btsid in btsid_group.split(','):
        pbinfo = get_pbinfo(btsid)
        lock = get_lock(btsid)
        if lock == "on":
            locked_btslist += btsid + ' '
            continue
        if pbinfo == '' or pbinfo == 'None':
            info = "BTS PB info is null!"
            fail_btslist += btsid + ' '
            continue
        if ":" not in pbinfo:
            info = "BTS PB info not has port info!"
            fail_btslist += btsid + ' '
            continue
        try:
            power_control_for_facom('OFF', pbinfo)
            info = "Poweroff BTS Success!"
            success_btslist += btsid + ' '
        except Exception as E:
            print('Error: {}'.format(E))
            info = "Cannot Poweroff BTS!"
            fail_btslist += btsid + ','
        print('good night bts id {} info {}'.format(btsid, info))
    return HttpResponse(json.dumps({"status": "ok", "success_btslist": success_btslist, "fail_btslist": fail_btslist, "locked_btslist":locked_btslist}), content_type="application/json")

def run_project(request):
    project_name = str(request.POST['project_name'])
    print('run paroject name...{}'.format(project_name))
    cmd = 'curl -i -X POST "http://10.69.82.129/job/{}/build" -u admin:admin123'.format(project_name)
    remote_cmd = 'sshpass -p root ssh root@10.69.82.130 "{}"'.format(cmd)
    out = os.popen(remote_cmd).read()
    location_info = [x for x in out.splitlines() if x.startswith('Location:')]
    if location_info:
        print('Trigger Jenkins job done')
        # self.logger.debug(out)
        instanceid = location_info[0].split('/')[-2]
        print('Instance ID for the job: {}'.format(instanceid))
        time.sleep(10)
        baseurl = 'http://operator:btstest1234@10.69.82.129/queue/item'
        cmd2 = 'curl -X GET "{}/{}/api/json?pretty=true"'.format(baseurl, instanceid)
        remote_cmd2 = 'sshpass -p root ssh root@10.69.82.130 "{}"'.format(cmd2)
        out2 = os.popen(remote_cmd2).read()
        response = json.loads(out2)
        if response['blocked']:
            msg = 'Project is blocked becuse some task is onging.'
            return HttpResponse(json.dumps({"status": "blocked", "url": msg}), content_type="application/json")
        else:
            url = response.get('executable').get('url')
            msg = 'Project is started, url: {}'.format(
                response.get('executable').get('url'))
        print(msg)
        return HttpResponse(json.dumps({"status": "ok", "url": url}), content_type="application/json")
    else:
        print('Trigger Jenkisn job failed: {}'.format(out))
        return HttpResponse(json.dumps({"status": "nok", "url": out}), content_type="application/json")   

def get_project(request):
    btsid = str(request.POST['btsid'])
    print('Get project for {}'.format(btsid))
    jobstr = search_joblist(btsid)
    joblist = []
    for job in jobstr.split(','):
        joblist.append(job)
    return HttpResponse(json.dumps({"status": "ok", "joblist": joblist}), content_type="application/json")

def load_config(btsid):
    print('Log config for {}'.format(btsid))
    from getdata import get_data_by_sql
    field, result = get_data_by_sql('select * from btstable where btsid={};'.format(btsid))
    bts = [x for x in result if x.btsid == btsid][0]
    # if bts:
    #     self._config = bts[0]
    #     for attr in [x for x in dir(self._config) if not x.startswith('_')]:
    #         setattr(self, attr, getattr(self._config, attr))
    bts.bts_id = bts.btsid
    bts.bts_ip = bts.btsip
    bts.workcell = 1
    bts.is5g = 0
    # bts.airscale = True if bts.airscale == '1' else False
    # bts.sran = bts.airscale == '1'
    bts.bts_fcm_ip = '192.168.255.1'
    bts.bts_fcm_username = 'toor4nsn'
    bts.bts_fcm_password = 'oZPS0POrRieRtu'
    bts.bts_ftm_ip = '192.168.255.129'
    bts.bts_ftm_username = 'Nemuadmin'
    bts.bts_ftm_password = 'nemuuser'
    bts.mr_paging_ioc, bts.mr_paging_impair_ioc = '140', '84'
    bts.mr_call_drop_ioc, bts.mr_call_drop_impair_ioc = '140', '84'
    bts.mr_ho_ioc, bts.mr_ho_impair_ioc = '140', '89'
    bts.mr_volte_ioc, bts.mr_volte_impair_ioc = '140', '84'
    bts.conn_bts = None
    bts.ftmctrl = None
    bts.config_id = ''
    bts.cell_count = 0
    bts.used = True
    bts.infomodel_pid = []
    bts.new_earfcn_list = []
    bts.new_eutraCarrierInfo_list = []
    # bts.pcap_interface = (r'\Device\NPF_' +
    #                       bts.pcap_interface.upper().split('NPF_')[-1])
    bts.scf_filename = ''
    bts.infomodel = None
    bts.ute_admin = None
    bts.error_log_list = []
    bts.monitor_error_log = False
    bts.btslog_buffer = []
    bts.pm_counter_path = '/tmp' if bts.sran else '/ram'
    bts.scf_change_is_differ = True
    bts.btsmode = 'S'
    bts.cpc = None
    bts.btslogger = None
    bts.infomodel = None
    bts.admin_api = None
    bts.ftmctrl = None
    bts.fct_cpu_manager = None
    bts.fct_memory_manager = None
    bts.tti = None
    bts.bts_control_pc_lab = ""
    bts.api_version = 2
    return bts

def admin_api_setup(btsid):

    from lib_bts import c_pet_admin_api
    # from pet_bts_c import c_pet_bts
    # bts = c_pet_bts(btsid)
    # bts.load_config()
    bts = load_config(btsid)
    bts.dire_snap = '/home/work/temp/bts/'
    bts.dire_admin = '/home/work/temp/bts/'
    bts.admin_api = c_pet_admin_api(bts)
    bts.admin_api.setup()
    return bts



if __name__ == '__main__':
    sys.path.append('/home/quicklink/mysite/')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
    while(1):
        refresh_bts_info()
        get_job_bts()
        time.sleep(900)
