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
from django.contrib.auth import authenticate, login as auth_login,logout as auth_logout
from django.contrib.auth.models import User
from gencase.models import AuthUser
import json
import base64

def login_auth(request):  
    print('login init...')
    if 'login' in request.POST:
        return doauth(request)
    elif 'team' in request.POST:
        return addteamforuser(request)
    else:
        return HttpResponse(json.dumps({"status": "nok"}), content_type="application/json")

def doauth(request):
    print('doauth...')
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    print(username)
    print(password)
    if username is not None and password is not None:
        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            # request.session['username'] = user.username
            # request.session['password'] = base64.b64encode(password.encode())
            # request.session.set_expiry(144000)
            # if AuthUser.objects.get(username=user.username).team is None:
            #     code = "0004"
            #     msg = "Select a team!"
            # else:
            code = "0000"
            msg = "Login success!"
        else:
            code = "0002"
            msg = "Auth Error!"
    else:
        code = "0001"
        msg = "missing username or password!"
    print(code)
    print(msg)
    return HttpResponse(json.dumps({"code": code, "msg": msg}), content_type='application/json')

def addteamforuser(request):
    team = request.POST.get('team', None)
    if team is not None:
        AuthUser.objects.filter(username=request.session['username']).update(team=team)
        code = "0000"
        msg = 'success'
    else:
        code = "0001"
        msg = 'please select team'
    return HttpResponse(json.dumps({"code": code, "msg": msg}), content_type='application/json')
