# -*- coding: utf-8 -*-
#from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth import  login as Lg
import json
from django.http import HttpResponse
import logging
logger = logging.getLogger('django')

@login_required
def index(req):
    logger.info('aaa')
    logger.error('error')
    print req.user.id
    return render_to_response('index.html',locals())

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username,password=password)
        if user is not None :
            Lg(request , user)
            print  request.POST.get('next')
            if request.POST.get('next'):
                response = HttpResponseRedirect(request.POST.get('next'))
                return  response
            else:
                return HttpResponseRedirect('/home/')
        else:
            return render_to_response('login.html')
    else:
        next=request.GET.get('next','/home/')
        return render_to_response('login.html',locals())

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')

@login_required
def showloading(req):
    offset = req.POST['offset']
    limit= req.POST['limit']
    print req.user.id,limit,offset
    resp={'total':'220','rows':[]}
    resp['rows'].append({'Name':'sds','ParentName':'dfsdgg','Level':'1','Desc':'haha'})
    resp['rows'].append({'Name': '11sds', 'ParentName': 'dfs33dgg', 'Level': '12', 'Desc': 'h22aha'})
    resp['rows'].append({'Name': '11sds', 'ParentName': 'dfs33dgg', 'Level': '12', 'Desc': 'h22aha'})
    resp['rows'].append({'Name': '11sds', 'ParentName': 'dfs33dgg', 'Level': '12', 'Desc': 'h22aha'})
    resp['rows'].append({'Name': '11sds', 'ParentName': 'dfs33dgg', 'Level': '12', 'Desc': 'h22aha'})
    resp['rows'].append({'Name': '11sds', 'ParentName': 'dfs33dgg', 'Level': '12', 'Desc': 'h22aha'})
    resp['rows'].append({'Name': '11sds', 'ParentName': 'dfs33dgg', 'Level': '12', 'Desc': 'h22aha'})
    resp['rows'].append({'Name': '11sds', 'ParentName': 'dfs33dgg', 'Level': '12', 'Desc': 'h22aha'})
    resp['rows'].append({'Name': '11sds', 'ParentName': 'dfs33dgg', 'Level': '12', 'Desc': 'h22aha'})
    resp['rows'].append({'Name': '11sds', 'ParentName': 'dfs33dgg', 'Level': '12', 'Desc': 'h22aha'})
    resp['rows'].append({'Name': '11sds', 'ParentName': 'dfs33dgg', 'Level': '12', 'Desc': 'h22aha'})
    resp['rows'].append({'Name': '11sds', 'ParentName': 'dfs33dgg', 'Level': '12', 'Desc': 'h22aha'})
    resp['rows'].append({'Name': '11sds', 'ParentName': 'dfs33dgg', 'Level': '12', 'Desc': 'h22aha'})
    resp['rows'].append({'Name': '11sds', 'ParentName': 'dfs33dgg', 'Level': '12', 'Desc': 'h22aha'})
    resp['rows'].append({'Name': '11sds', 'ParentName': 'dfs33dgg', 'Level': '12', 'Desc': 'sdsads'})
    resp['rows'].append({'Name': '11sds', 'ParentName': 'dfs33dgg', 'Level': '12', 'Desc': 'h22aha'})
    resp['rows'].append({'Name': '11sds', 'ParentName': 'dfs33dgg', 'Level': '12', 'Desc': 'h22aha'})
    resp['rows'].append({'Name': '11sds', 'ParentName': 'dfs33dgg', 'Level': '12', 'Desc': 'h22aha'})
    resp['rows'].append({'Name': '11sds', 'ParentName': 'dfs33dgg', 'Level': '12', 'Desc': 'h22aha'})
    resp['rows'].append({'Name': '11sds', 'ParentName': 'dfs33dgg', 'Level': '12', 'Desc': 'h22aha'})
    resp['rows'].append({'Name': '11sds', 'ParentName': 'dfs33dgg', 'Level': '12', 'Desc': 'h22aha'})
    resp['rows'].append({'Name': '11sds', 'ParentName': 'dfs33dgg', 'Level': '12', 'Desc': 'h22aha'})
    resp['rows'].append({'Name': '11sds', 'ParentName': 'dfs33dgg', 'Level': '12', 'Desc': 'h22aha'})
    resp['rows'].append({'Name': '11sds', 'ParentName': 'dfs33dgg', 'Level': '12', 'Desc': 'h22aha'})
    resp['rows'].append({'Name': '11sds', 'ParentName': 'dfs33dgg', 'Level': '12', 'Desc': 'h22aha'})

    return HttpResponse(json.dumps(resp), content_type="application/json")
    #return render_to_response('showloading.html',locals())

@login_required
def test(req):

    return render_to_response('test.html',locals())