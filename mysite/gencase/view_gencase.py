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

def gen_case(request):  
    print('gen case init...')
    if 'config' in request.POST:
        return config(request)
    elif 'transf' in request.POST:
        return transf(request)
    else:
        return HttpResponse(json.dumps({"status": "nok"}), content_type="application/json")

def get_time():
    import datetime
    # now_time = datetime.datetime.now()
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return timestamp

def get_case_type(string):
    case_type_dict = {
        'mix_cap': ['THROUGHPUT', 'RATE', 'SPEED', '速率', '流量'],
        'oam': ['OAM', 'BLOCK', 'RESET', '操作'],
        'uc_mix': ['KPI', 'COUNTER', 'LTE_', 'SUCCESSFUL RATE', 'DROP RATE', 'SUCCESS RATIO', 'DROP RATIO', '指标', '成功率', '失败率'],
    }
    for item in case_type_dict.keys():
        case_type_list = case_type_dict[item]
        for value in case_type_list:
            if value in string:
                return item
    return ''


def config(request):
    print('config init...')
    reload(sys)
    sys.setdefaultencoding("utf8")
    input1 = str(request.POST['input1'])
    output = ''
    print(input1.upper())
    case_type = get_case_type(input1.upper())
    if case_type == '':
        output = 'Not Support!'
        return HttpResponse(json.dumps({"status": "nok", "output": output}), content_type="application/json")
    print(case_type)
    filename = filename_dir + case_type + '_config.txt'
    lines = open(filename, 'r').readlines()
    for line in lines:
        output += line
    return HttpResponse(json.dumps({"status": "ok", "output": output}), content_type="application/json")

def transf(request):
    print('transf init...')
    reload(sys)
    sys.setdefaultencoding("utf8")
    input1 = str(request.POST['input1'])
    input2 = str(request.POST['input2'])
    output = ''
    case_type = get_case_type(input1.upper())
    if case_type == '':
        output = 'Not Support!'
        return HttpResponse(json.dumps({"status": "nok", "output": output}), content_type="application/json")
    print(case_type)
    # print(input2.split('\n'))
    filename = filename_dir + case_type + '.txt'
    lines = open(filename, 'r').readlines()
    timestamp = get_time()
    setid = 'QC Set ID                                =  {}\n'.format(timestamp)
    instanceid = 'QC Instance ID                           =  {}\n'.format(timestamp)
    for line in lines:
        flag = 0
        for modify_line in input2.split('\n'):
            line_key = line.split('=')[0].rstrip()
            modify_line_key = modify_line.split('=')[0].rstrip()
            if modify_line_key != '' and modify_line_key == line_key:
                output += modify_line
                flag = 1
        if flag == 0:
            output += line
    output += setid
    output += instanceid
    return HttpResponse(json.dumps({"status": "ok", "output": output}), content_type="application/json")

# class c_gen_case_content(TemplateView):
#     template_name = "index.html"

#     def __init__(self):
#         print('init c_gen_case_content')
#         logger.info('init c_gen_case_content')
#         self.filename_dir = '/txt/'
#         self.init_logger()

#     def init_logger(self):
#         log_filename = '/var/log/gencase.log'
#         logging.basicConfig(
#             format='%(asctime)s,%(msecs)3d [%(levelname)5s] %(message)s',
#             datefmt='%D-%H:%M:%S', level=logging.DEBUG, filename=log_filename)
#         self.logger = logging.getLogger(__file__)
#         self.logger.info('========= Start Clean Pybot ========')

#         root = logging.getLogger()
#         root.setLevel(logging.DEBUG)

#         ch = logging.StreamHandler(sys.stdout)
#         ch.setLevel(logging.DEBUG)
#         formatter = logging.Formatter('%(asctime)s [%(levelname)5s] %(message)s',
#                                       datefmt='%Y-%m-%d %H:%M:%S')
#         ch.setFormatter(formatter)
#         root.addHandler(ch)

#     def get(self, request):
#         self.logger.info(request.GET)
#         if request.method == 'GET':
#             return render(request, self.template_name, {'status': 'ok'})

#     def post(self, request):
#         self.logger.info(request.POST)
#         if 'input1' or 'input2' in request.POST:
#             return self.gen_case(request)
#         return render(request, self.template_name, {'status': 'ok'})

#     def gen_case(self, request):
#         self.logger.info('update snapshot file...')
#         input1 = request.POST['input1']
#         input2 = request.POST['input2']
#         if 'THROUGHPUT' or '速率' in input1.upper():
#             case_type = 'mix_cap'
#         elif 'OAM' in input1.upper():
#             case_type = 'oam'
#         elif 'KPI' in input1.upper():
#             case_type = 'uc_mix'
#         else:
#             output = 'Not Support!'
#             return HttpResponse(json.dumps({"status": 'nok'}), content_type="application/json")
#         filename = self.filename_dir + case_type + '.txt'
#         output = open(filename, 'r').readlines()
#         return HttpResponse(json.dumps({"status": 'ok', "output": output}), content_type="application/json")

# gencase_url = url('^index/', c_gen_case_content.as_view(), name="index")
