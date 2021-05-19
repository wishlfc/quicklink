import os
import sys
import time

sys.path.append('/home/work/tacase_dev/Resource')
sys.path.append('/home/work/tacase_dev')
from pet_ipalib import IpaMmlItem

def ping_s1(btsip):
    if btsip == 'NULL' or btsip == '' or btsip == '0.0.0.0':
        return False
    result = os.popen('ping -c 3 {}'.format(btsip)).read()
    print(result)
    if "100% packet loss" in result or "Invalid argument" in result :
        return False
    return True

def hw_version(bts):
    from lib_bts import c_pet_admin_api
    info = ""
    version = ""
    try:
        bts.admin_api = c_pet_admin_api(bts)
        bts.admin_api.setup()
        bts.admin_api.connect()
        state1 = bts.admin_api.ute_admin.get_parameters_for_all(class_name='SMOD', alias=bts.admin_api.ute_admin_alias)
        state2 = bts.admin_api.ute_admin.get_parameters_for_all(class_name='BBMOD', alias=bts.admin_api.ute_admin_alias)
        state3 = bts.admin_api.ute_admin.get_parameters_for_all(class_name='RMOD', alias=bts.admin_api.ute_admin_alias)
        state4 = bts.admin_api.ute_admin.get_gps_status(alias=bts.admin_api.ute_admin_alias)
        version = bts.admin_api.ute_admin.get_software_info(alias=bts.admin_api.ute_admin_alias)
        keylist = ["id", "productName", "productCode", "serialNumber"]
        for state in state1:
            for key in keylist:
                if key in state:
                    info = info + '{}:{}\n'.format(key, state[key])
        info = info + '\n'
        for state in state2:
            for key in keylist:
                if key in state:
                    info = info + '{}:{}\n'.format(key, state[key])
        info = info + '\n'
        for state in state3:
            print(state)
            for key in keylist:
                if key in state:
                    info = info + '{}:{}\n'.format(key, state[key])
        info = info + '\n'
        if 'requestMessage' in state4:
            state4 = state4['requestMessage']
        if 'gnsse' in state4:
            for state in state4['gnsse']:
                print('111')
                print(state)
                gpsid = state['id']['internal']
                info = info + '{}:{}\n'.format('id', gpsid)
                state = state['parameters']
                for key in keylist:
                    if key in state:
                        info = info + '{}:{}\n'.format(key, state[key])
        print(info)
        if 'Active SW version' in version:
            version = version['Active SW version']
    except Exception as E:
        print('Error: {}'.format(E))
    finally:
        if bts.admin_api != None:
            bts.admin_api.teardown()
    return info, version

def get_hw(btsid, btss1ip, flag):
    hwinfo = ''
    version = ''
    if not ping_s1(btss1ip):
        return hwinfo, version
    bts = IpaMmlItem()
    bts.btsid = str(btsid)
    bts.bts_ip = btss1ip
    bts.is5g = 1 if flag == '5g' else 0
    bts.iscoam = bts.is5g
    bts.sran = 1
    bts.admin_api = None
    bts.dire_snap = '/home/work/temp/bts/'
    bts.dire_admin = '/home/work/temp/bts/'
    print('get bts hw info...{}'.format(btsid))
    hwinfo, version = hw_version(bts)
    return hwinfo, version

def anaysis_hw_info(hw_info, btsid):
    import re
    # line = ''
    infolist = []
    if hw_info == '':
        return infolist
    for info in hw_info.split('id:'):
        hinfo = {}
        for line in info.split('\n'):
            if 'productName' in line:
                pn = re.search('productName:(.*)', line).group(1)
                if 'Flexi System Module Indoor' in pn:
                    pn = pn.replace('Flexi System Module Indoor', '')
                if 'BB Extension Indoor Sub-Module' in pn:
                    pn = pn.replace('BB Extension Indoor Sub-Module', '')
                if 'AirScale Common' in pn:
                    pn = pn.replace('AirScale Common', '')
                if 'AirScale Capacity' in pn:
                    pn = pn.replace('AirScale Capacity', '')
                hinfo['productName'] = pn.strip()
            if 'serialNumber' in line:
                sn = re.search('serialNumber:(.*)', line).group(1)
                hinfo['serialNumber'] = sn
                hinfo['owner'], hinfo['status'] = search_onelab_status(sn)
            if 'productCode' in line:
                pc = re.search('productCode:(.*)', line).group(1)
                hinfo['productCode'] = pc
        if hinfo:
            infolist.append(hinfo)
    return infolist

def get_hw_info():
    import MySQLdb
    db = MySQLdb.connect('10.69.68.42', 'root', 'root', 'quicklink')
    cursor = db.cursor()
    cursor.execute('SELECT btsid,btss1ip,flag FROM testlinetopo;')
    results = cursor.fetchall()
    # hwlist = []
    noinfo_btslist = []
    for i in range(1, 3):
        print('=====================Time {} begin====================='.format(i))
        for result in results:
            # if result[0] in [6001]:
            info = {}
            info['btsid'] = result[0]
            info['btss1ip'] = result[1]
            hwinfo, version = get_hw(result[0], result[1], result[2])
            anainfo = anaysis_hw_info(hwinfo, result[0])
            info['hwinfo'] = anainfo
            # hwlist.append(info)
            if len(info) != 0:
                update_hwinfo(info, version)
                if info['btsid'] in noinfo_btslist:
                    noinfo_btslist.remove(info['btsid'])
            else:
                if info['btsid'] not in noinfo_btslist:
                    noinfo_btslist.append(info['btsid'])
            # break
        print('Cannot get info for btslist {}'.format(noinfo_btslist))
        print('=====================Time {} end====================='.format(i))
        time.sleep(300)
    if len(noinfo_btslist) != 0:
        print('Finally cannot get info for btslist {}'.format(noinfo_btslist))
    # return hwlist

def update_hwinfo(info, version):
    from getdata import run_sql
    data = ''
    for hw in info['hwinfo']:
        # data = data + hw['productName'] + '_' + hw['productCode'] + '_' + hw['serialNumber'] + ' ' 
        if 'productName' in hw and 'productCode' in hw and 'serialNumber' in hw:
            data = data + hw['productName'] + '_' + hw['productCode'] + '_' + hw['serialNumber'] + '_' + hw['status'] + '_' + hw['owner'] + ' '
            run_sql('update testlinetopo set `hw_info`="{}" where btsid={};'.format(data, int(info['btsid'])))
            run_sql('update testlinetopo set `version`="{}" where btsid={};'.format(version, int(info['btsid'])))

def search_onelab_status(sn):
    import requests
    from lxml import etree
    from io import StringIO
    import time
    import urllib3
    import json
    import re
    urllib3.disable_warnings()
    owner = ''
    status = ''
    if sn == "-1" or sn == "":
        return owner, status

    PROXY = '10.144.1.10:8080'
    PROXIES = dict(https=PROXY, http=PROXY)

    page2 = '''https://onelab.eecloud.dynamic.nsn-net.net/index.php?m=Inventory&a=ajaxSearchList&search={}\
    &_dc=1616638335340&page=1&start=0&limit=20&sort=think_inventory_view.id&dir=DESC&\
filter=%5B%7B%22operator%22%3A%22in%22%2C%22value%22%3A%5B%222%22%2C%223%22%2C%224%22%2C%225%22%2C%\
226%22%2C%228%22%2C%229%22%2C%2210%22%2C%2212%22%2C%2213%22%2C%2214%22%2C%2215%22%2C%2216%22%2C%2217%\
22%2C%2218%22%2C%2220%22%2C%2221%22%2C%2222%22%2C%2223%22%2C%2224%22%2C%2225%22%5D%2C%22property%22%\
3A%22status%22%7D%2C%7B%22operator%22%3A%22in%22%2C%22value%22%3A%5B%223%22%5D%2C%22property%22%3A%\
22site_name%22%7D%5D'''.format(sn)
    response = requests.get(page2, proxies=PROXIES, verify=False)
    if response.status_code == 200:
        total = json.loads(response.text)["total"]
        if int(total) >= 1:
            result = json.loads(response.text)["result"][0]
            owner = result["user_email"].split('@')[0]
            status = re.findall(r'>(.*)</span>', result["status"])[0].replace(" ", "")
            return owner, status
    return owner, status


if __name__ == '__main__':
    sys.path.append('/home/quicklink/mysite/')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
    get_hw_info()
    # owner, status = search_onelab_status('L1184709163')
    # print(owner)
    # print(status)
