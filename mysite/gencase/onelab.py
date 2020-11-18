import urllib3
from requests import Session, Response
from lxml import etree
from io import StringIO

class WebC(object):

    def __init__(self):
        urllib3.disable_warnings()
        self.session = Session()
        # from all_config import PetSetting
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
        self.proxies = dict(https='10.144.1.10:8080', http='10.144.1.10:8080')
        self.username = 'a3liu'
        self.password = 'Hh888888!'
        self.auth = (self.username, self.password)

    def get(self, url, **kwargs):
        print(f'----> GET {url} {kwargs}')
        response = self.session.get(url, proxies=self.proxies, timeout=120, **kwargs)
        print(f'<---- GET response status code: {response.status_code}')
        return response

    def post(self, url, data=None, json=None, **kwargs):
        print(f"----> POST : {url}  data:{data}  json:{json}  kwargs: {kwargs}")
        response = self.session.post(url, data=data, json=json, **kwargs)
        print(f"<---- POST response: {response.status_code}-{response.reason}")
        return response

class OneLabC(WebC):
  
    def login(self):
        login_page = 'https://onelab.eecloud.dynamic.nsn-net.net/index.php?m=public&a=login'
        response = self.get(login_page, verify=False)
        # Search the hidden hash_value:
        # <input type="hidden" name="__hash__" value="a936f643aab74fe026deb5f1ce790948_67fd6d169190b624d584beff16eba1c1" />
        tree = etree.parse(StringIO(response.text), parser=etree.HTMLParser())
        self.hash_value = tree.xpath('//input[@name="__hash__"]/@value')
        if self.hash_value:
            self.hash_value = self.hash_value[0]
        else:
            raise Exception('Could not find __hash__ in login page.')

        payload = dict(account=self.username, password=self.password, __hash__=self.hash_value)
        login_url = 'https://onelab.eecloud.dynamic.nsn-net.net/index.php?m=public&a=domainLogin'
        response = self.post(login_url, data=payload, verify=False)

    def search(self,sn):
        import json, re
        # page = 'https://onelab.eecloud.dynamic.nsn-net.net/index.php?m=reserve&a=assetlist#1'
        page = '''https://onelab.eecloud.dynamic.nsn-net.net/index.php?m=Inventory&a=ajaxSearchList&search={}
        &_dc=1589522164265&page=1&start=0&limit=20&sort=think_inventory_view.id&dir=DESC&filter=
        %5B%7B%22operator%22%3A%22in%22%2C%22value%22%3A%5B%222%22%2C%223%22%2C%224%22%2C%225%22%2C
        %226%22%2C%228%22%2C%229%22%2C%2210%22%2C%2212%22%2C%2213%22%2C%2214%22%2C%2215%22%2C%2216%
        22%2C%2217%22%2C%2218%22%2C%2220%22%2C%2221%22%5D%2C%22property%22%3A%22status%22%7D%5D'''.format(sn)
        response = self.get(page, verify=False)
        print('===============================')
        web_rn = json.loads(response.text)
        print(web_rn)
        if web_rn['total'] == '1':
            span = web_rn['result'][0]['status']
            self.status = re.search('>([A-Za-z]+)</', span).group(1)
            self.owner = web_rn['result'][0]['item_owner_email']
        elif web_rn['total'] == '0':
            self.status = 'notfind'
            self.owner = 'notfind'
        elif web_rn['total'] > '1':
            self.status = 'total>1'
            self.owner = 'total>1'
        else:
            self.status = 'error'
            self.owner = 'error'
        print(self.status)
        print(self.owner)
        
if __name__ == '__main__':
    sn = 'QTFSPE520170001BE'
    olc = OneLabC()
    olc.login()
    olc.search(sn)