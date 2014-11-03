__author__ = 'jblowe'

import os

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response
from django import forms

from utils import loginfo, doApp, getAppList, setConstants


#@login_required()
def index(request):
    context = setConstants({'appname' : 'listapps', 'apps' : getAppList()})
    return render(request, 'toolbox.html', context)


#@login_required()
def tool(request, appname):

    context = {}
    if request.method == 'GET':
        requestObject = request.GET
        form = forms.Form(requestObject)

        if form.is_valid():
            context = {'searchValues': requestObject}
            context['appname'] = appname
            loginfo(appname, context, request)
            context = doApp(context)
    else:
        form = forms.Form()
        context = {}

    context = setConstants(context)
    loginfo(appname, context, request)
    return render(request, 'toolbox.html', context)
