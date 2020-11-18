# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse

def index(request):
    if request.method == 'POST':
        from view_gencase import gen_case
        return gen_case(request)
    else:
        return render(request, "index.html")

def login(request):
    if request.method == 'POST': 
        from view_login import login_auth
        return login_auth(request)
    else:
        backurl = request.GET.get('back', None)
        return render(request, "login.html", {'back': backurl})

# def gencase(request):
#     if request.method == 'POST':
#         from view_gencase import gen_case
#         return gen_case(request)
#     else:
#         return render(request, "gencase.html")

def prdescription(request):
    from view_prdescription import pr_description
    if request.method == 'POST':
        return pr_description(request)
    else:
        return render(request, "prdescription.html")

def btsmgmt(request):
    from view_bts import view_bts, view_bts_get
    if request.method == 'POST':
        return view_bts(request)
    elif request.method == 'GET':
        return view_bts_get(request)
    else:
        return render(request, "btsmgmt.html")

def whitelist(request):
    if request.method == 'POST':
        from view_whitelist import white_list
        return white_list(request)
    else:
        return render(request, "whitelist.html")

def topo(request):
    if request.method == 'GET':
        return render(request, "jtopo.html")
    else:
        return render(request, "jtopo.html")

def testline(request):
    from view_testline import testline, view_testline_get
    if request.method == 'POST':
        return testline(request)
    elif request.method == 'GET':
        return view_testline_get(request)
    else:
        return render(request, "testline.html")

def testlinechange(request):
    from view_testlinechange import testlinechange, view_testlinechange_get
    if request.method == 'POST':
        return testlinechange(request)
    elif request.method == 'GET':
        return view_testlinechange_get(request)
    else:
        return render(request, "testlinechange.html")
