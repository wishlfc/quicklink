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
sys.path.append('/home/work/tacase_dev/Resource')
filename_dir = './templates/txt/'


def pr_description(request):  
    print('pr description init...')
    if 'submit' in request.POST:
        return transf(request)
    elif 'goldencheck' in request.POST:
        return goldencheck(request)
    elif 'getflag' in request.POST:
        return getflag(request)
    elif 'getflag_btsip' in request.POST:
        return getflag_btsip(request)
    elif 'gethw' in request.POST:
        return gethw(request)
    elif 'gethw_btsip' in request.POST:
        return gethw_btsip(request)
    else:
        return HttpResponse(json.dumps({"status": "nok"}), content_type="application/json")

def init_description(request):  
    print('pr description init...')
    return init(request)

def get_time():
    import datetime
    # now_time = datetime.datetime.now()
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return timestamp

def init(request):
    pass

def ping_s1(btsip):
    result = os.popen('ping -c 3 {}'.format(btsip)).read()
    print(result)
    if "100% packet loss" in result:
        return False
    return True

def hw_version(bts):
    from lib_bts import c_pet_admin_api
    from lib_common import json_to_ipammlitem
    bts.dire_snap = '/home/work/temp/bts/'
    bts.dire_admin = '/home/work/temp/bts/'
    try:
        bts.admin_api = c_pet_admin_api(bts)
        bts.admin_api.setup()
        bts.admin_api.connect()
        state1 = bts.admin_api.ute_admin.get_parameters_for_all(class_name='SMOD', alias=bts.admin_api.ute_admin_alias)
        state2 = bts.admin_api.ute_admin.get_parameters_for_all(class_name='BBMOD', alias=bts.admin_api.ute_admin_alias)
        state3 = bts.admin_api.ute_admin.get_parameters_for_all(class_name='RMOD', alias=bts.admin_api.ute_admin_alias)
        keylist = ["id", "productCode", "productName", "serialNumber", "buildVersion", "hwVersion", "l3Protocol"]
        state_new1 = [json_to_ipammlitem(dict(item)) for item in state1]
        state_new2 = [json_to_ipammlitem(dict(item)) for item in state2]
        state_new3 = [json_to_ipammlitem(dict(item)) for item in state3]
        info = ""
        for state in state_new1:
            for key in keylist:
                if hasattr(state, key):
                    info = info + '{}:{}\n'.format(key, getattr(state, key))
        info = info + '\n'
        for state in state_new2:
            for key in keylist:
                if hasattr(state, key):
                    info = info + '{}:{}\n'.format(key, getattr(state, key))
        info = info + '\n'
        for state in state_new3:
            for key in keylist:
                if hasattr(state, key):
                    info = info + '{}:{}\n'.format(key, getattr(state, key))
    except Exception as E:
        print('Error: {}'.format(E))
        info = "Cannot get info!"
    finally:
        if bts.admin_api != None:
            bts.admin_api.teardown()
    print('11111')
    print(info)
    print('22222')
    return info

def gethw(request):
    print('gethw init...')
    btsid = str(request.POST['btsid']).strip()
    if btsid == "":
        info = "Not found btsid!"
        return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")   
    from lib_bts.pet_bts_c import c_pet_bts
    bts = c_pet_bts(btsid)
    bts.load_config()
    info = hw_version(bts)
    return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")


def gethw_btsip(request):
    print('gethw init...')
    btsip = str(request.POST['btsip']).strip()
    # issran = str(request.POST['issran']).strip()
    if btsip == "":
        info = "Not found btsip!"
        return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")
    if not ping_s1(btsip):
        info = "S1 is not Reachable!"
        return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")
    # sran = 1 if issran == 'true' else 0
    sran = 1
    bts = load_config(btsip, sran)
    info = hw_version(bts)
    print(info)
    return HttpResponse(json.dumps({"status": "ok", "info": info}), content_type="application/json")


def getflag_btsip(request):
    from lib_bts.pet_bts_s1_c import c_pet_bts_s1
    print('getflag init...')
    btsip = str(request.POST['btsip']).strip()
    # issran = str(request.POST['issran']).strip()
    if btsip == "":
        flags = "Not found btsip!"
        return HttpResponse(json.dumps({"status": "ok", "flags": flags}), content_type="application/json")   
    if not ping_s1(btsip):
        flags = "S1 is not Reachable!"
        return HttpResponse(json.dumps({"status": "ok", "flags": flags}), content_type="application/json")
    # sran = 1 if issran == 'true' else 0
    sran = 1
    bts = load_config(btsip, sran)
    bts.s1 = c_pet_bts_s1(bts)
    bts.s1.setup()
    timestamp = get_time()
    filename = '/home/work/temp/bts/swconfig_{}.txt'.format(timestamp)
    bts.s1.download_file(os.sep.join(['/ffs/run', 'swconfig.txt']),
                         filename)
    bts.s1.teardown()
    lines = open(filename).read().splitlines()
    flags = ''
    for line in lines:
        if line != '':
            flags += line + '\n'
    return HttpResponse(json.dumps({"status": "ok", "flags": flags}), content_type="application/json")

def getflag(request):
    print('getflag init...')
    btsid = str(request.POST['btsid']).strip()
    if btsid == "":
        flags = "Not found btsid!"
        return HttpResponse(json.dumps({"status": "ok", "flags": flags}), content_type="application/json")   
    from lib_bts.pet_bts_s1_c import c_pet_bts_s1
    from lib_bts.pet_bts_c import c_pet_bts
    try:
        bts = c_pet_bts(btsid)
        bts.load_config()
        bts._set_default_values()
        bts.dire_im = '/home/work/temp/bts/'
        bts.s1 = c_pet_bts_s1(bts)
        bts.s1.setup()
        timestamp = get_time()
        filename = '/home/work/temp/bts/swconfig_{}.txt'.format(timestamp)
        bts.s1.download_file(os.sep.join(['/ffs/run', 'swconfig.txt']),
                             filename)
        bts.s1.teardown()
        lines = open(filename).read().splitlines()
        flags = ''
        for line in lines:
            if line != '':
                flags += line + '\n'
        return HttpResponse(json.dumps({"status": "ok", "flags": flags}), content_type="application/json")
    except Exception as E:
        print('Error: {}'.format(E))
        flags = "Some error occured, please fill by yourself!"
        return HttpResponse(json.dumps({"status": "nok", "flags": flags}), content_type="application/json")

def transf(request):
    print('transf init...')
    import importlib
    importlib.reload(sys)
    steps = str(request.POST['steps'])
    expected_result = str(request.POST['expected_result'])
    actual_result = str(request.POST['actual_result'])
    test_analysis = str(request.POST['test_analysis'])
    swbot_info = str(request.POST['swbot_info'])    
    logs = str(request.POST['logs'])
    hw_info = str(request.POST['hw_info'])
    sw_info = str(request.POST['sw_info'])
    subframe_config = str(request.POST['subframe_config'])
    ue_type = str(request.POST['ue_type'])
    cell_type = str(request.POST['cell_type'])
    # mimo_mode = str(request.POST['mimo_mode'])
    # deploy = str(request.POST['deploy'])
    hw_version = str(request.POST['hw_version'])
    flags = str(request.POST['flags'])
    scenario_times = str(request.POST['scenario_times'])
    reproduced_times = str(request.POST['reproduced_times'])
    same_sites = str(request.POST['same_sites'])
    passed_info = str(request.POST['passed_info'])
    swversion_passed = str(request.POST['swversion_passed'])
    changes_testline = str(request.POST['changes_testline'])
    changes_scenario = str(request.POST['changes_scenario'])
    reference = str(request.POST['reference'])

    output = ''
    output += "[1. Detail Test Steps:]\n"
    output += "Scenario/Step:\n"
    output += steps + '\n'
    output += '\n'
    output += "[2. Expected Result:]\n"
    output += expected_result + '\n'
    output += '\n'
    output += "[3. Actual Result:]\n"
    output += actual_result + '\n'
    output += '\n'
    output += "[4. Tester analysis:]\n"
    output += "Analysis of Logs:\n"
    output += test_analysis + '\n'
    output += "SWBOT information:\n"
    output += swbot_info + '\n'
    output += '\n'
    output += "[5. Log(s) file name containing a fault: (clear indication (exact file name) and timestamp where fault can be found in attached logs)]\n"
    output += logs + '\n'
    output += '\n'
    output += "[6. Test-Line Reference/used HW/configuration/tools/SW version]\n"
    output += "HW:" + hw_info + "\n"
    output += "SW:" + sw_info + "\n"
    output += "UL/DL sub-Frame Configuration:" + subframe_config + "\n"
    output += "UE Type:" + ue_type + "\n"
    output += "Cell Type:" + cell_type + "\n"
    # output += "MIMO Mode:" + mimo_mode + "\n"
    # output += "Deploy:" + deploy + "\n"
    output += "HW versions:" + "\n"
    output += hw_version + "\n"
    output += '\n'
    output += "[7. Used Flags: (list here used R&D flags)]" + "\n"
    output += flags + "\n"
    output += '\n'
    output += "[8. Fault Occurrence Rate:]\n"
    output += "How many times Test Scenario was run?" + scenario_times + "\n"
    output += "How many times fault was reproduced?" + reproduced_times + "\n"
    output += "How many sites in the same live operation was run in case of customer fault?" + \
            same_sites + "\n"
    output += '\n'
    output += "[9. Test Scenario History of Execution: (what was changed since it was tested successfully for the last time)]\n"
    output += "Was Test Scenario passing before?" + passed_info + "\n"
    output += "What was the last SW version Test Scenario was passing?" + \
            swversion_passed + "\n"
    output += "Were there any differences between test-lines since last time Test Scenario was passing?" + \
     changes_testline + "\n"
    output += "Were there any changes in Test Scenario since last run it passed?" + \
     changes_scenario + "\n"
    output += '\n'
    output += "[10. Test Case Reference: (QC, RP or UTE link)]\n"
    output += reference + "\n"
    print(output)
    return HttpResponse(json.dumps({"status": "ok", "output": output}), content_type="application/json")

def load_config(btsip, sran):
    btsid = btsip.replace('.', '')
    print('Log config for {}'.format(btsip))
    # if bts:
    #     self._config = bts[0]
    #     for attr in [x for x in dir(self._config) if not x.startswith('_')]:
    #         setattr(self, attr, getattr(self._config, attr))
    from pet_ipalib import IpaMmlItem
    bts = IpaMmlItem()
    bts.sran = sran
    bts.btsid = btsid
    bts.btsip = btsip
    bts.bts_id = btsid
    bts.bts_ip = btsip
    bts.workcell = 1
    bts.airscale = 1
    bts.is5g = 0
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
    bts.admin_port = 3600 if bts.sran == 1 else 443
    return bts

def goldencheck(request):
    import requests
    import lib_common
    print('golden check init...')
    description = str(request.POST['description'])
    valid_url = 'https://golden-standard.dynamic.nsn-net.net/api/validator#description'
    payload = {"type": "internal", 'description': description}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
               "Content-Type": "application/json"}
    from requests.packages import urllib3
    urllib3.disable_warnings()
    rn = requests.post(url=valid_url, data=json.dumps(payload), verify=False, headers=headers)
    if rn.status_code == 200:
        # print(rn.text)
        response = lib_common.json_to_ipammlitem(json.loads(rn.text))
        result = response.messages
        # result = rn.text.messages
        alert_list = [line.alert for line in result]
        info_list = [line.info for line in result]
        print(alert_list)
        print(info_list)
        return HttpResponse(json.dumps({"status": "ok", "alert_list": alert_list, "info_list": info_list}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"status": "nok", "alert_list": [], "info_list": []}), content_type="application/json")
