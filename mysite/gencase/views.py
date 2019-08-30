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

def gencase(request):
    if request.method == 'POST':
        from view_gencase import gen_case
        return gen_case(request)
    else:
        return render(request, "gencase.html")

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
