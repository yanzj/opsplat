# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from ljapps.models import Apptype,Apps,Ports,Porttype,Group,Funcevent,Funcexe,Apps_history,Balance,Balance_attr
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponse
import json
import logging
logger = logging.getLogger('django')

@login_required
def update(req):
    if req.method == 'POST':
        appid=req.POST['aid']
        dest=req.POST['dest']
        curver = req.POST['curver']
        destver = req.POST['destver']
        app=Apps.objects.get(pk=appid)
        if dest=='pre':
            if app.prelock=='1' or app.prelock=='2':
                resp = {"msg": "此项目有审批或者更新还没完成"}
                return HttpResponse(json.dumps(resp), content_type="application/json")
            elif app.zippre=='':
                resp = {"msg": "请打包"}
                return HttpResponse(json.dumps(resp), content_type="application/json")
            else:
                app.prelock='1'
                app.save()
                resp = {"msg": "申请完成，等待审批"}
                return HttpResponse(json.dumps(resp), content_type="application/json")
        if dest=='prd':
            if app.prdlock=='1' or app.prdlock=='2':
                resp = {"msg": "此项目有审批或者更新还没完成"}
                return HttpResponse(json.dumps(resp), content_type="application/json")
            elif app.zipprd=='':
                resp = {"msg": "请打包"}
                return HttpResponse(json.dumps(resp), content_type="application/json")
            else:
                app.prdlock='1'
                app.save()
                resp = {"msg": "申请完成，等待审批"}
                return HttpResponse(json.dumps(resp), content_type="application/json")
        resp = {"msg": "申请完成，等待审批，测试环境无需审批。"}
        return HttpResponse(json.dumps(resp), content_type="application/json")

    else:
        if req.user.is_superuser == 1:
            apps = Apps.objects.filter(stats='1')
        else:
            apps = []
            gs = req.user.groups.all()
            for g in gs:
                aps = g.apps_set.filter(stats='1')
                print type(aps)
                for a in aps:
                    # print a
                    apps.append(a)
        return render_to_response('updatemanage/update.html',locals())

@login_required
def callbak(req):
    if req.method == 'POST':
        appid=req.POST['aid']
        dest=req.POST['dest']
        curver = req.POST['curver']
        destver = req.POST['destver']
        app=Apps.objects.get(pk=appid)
        if dest=='pre':
            if app.prelock=='1' or app.prelock=='2':
                resp = {"msg": "此项目有审批或者更新还没完成"}
                return HttpResponse(json.dumps(resp), content_type="application/json")
            else:
                app.prelock='1'
                app.zippre=app.prerb1
                app.save()
                resp = {"msg": "申请完成，等待审批"}
                return HttpResponse(json.dumps(resp), content_type="application/json")
        if dest=='prd':
            if app.prdlock=='1' or app.prdlock=='2':
                resp = {"msg": "此项目有审批或者更新还没完成"}
                return HttpResponse(json.dumps(resp), content_type="application/json")
            else:
                app.prdlock='1'
                app.zipprd=app.rb1
                app.save()
                resp = {"msg": "申请完成，等待审批"}
                return HttpResponse(json.dumps(resp), content_type="application/json")
        resp = {"msg": "申请完成，等待审批，测试环境无需审批。"}
        return HttpResponse(json.dumps(resp), content_type="application/json")
    else:
        if req.user.is_superuser == 1:
            apps = Apps.objects.filter(stats='1')
        else:
            apps = []
            gs = req.user.groups.all()
            for g in gs:
                aps = g.apps_set.filter(stats='1')
                print type(aps)
                for a in aps:
                    # print a
                    apps.append(a)
        return render_to_response('updatemanage/callbak.html',locals())

@login_required
def doupdate(req):
    if req.method == 'POST':
        aid=req.POST['aid']
        appid=aid.split(':')[0]
        destver=aid.split(":")[1]
        app=Apps.objects.get(pk=appid)
        print app.appname
        print destver
        #缺少判断是否已经升级完成，升级完成删除对应的新包字段值
        if destver=='test' and app.testhost.all().exists() :
            if not app.funcevent_set.filter(Q(destenv='test')&Q(status='1')).exists():
                tfunc=Funcevent(app=app,create_time=timezone.now(),exeuser=req.user,eventtype='update',status='1',destenv='test',zip=app.ziptest)
                tfunc.save()
                for h in app.testhost.all():
                    f = Funcexe(funcevent=tfunc,host=h,status='1',destenv='test')
                    f.save()
            exehost={}
            funceventid=''
            for i in app.funcevent_set.filter(Q(destenv='test')&Q(status='1')):
                funceventid=i.id

                for h in i.funcexe_set.filter(destenv='test'):
                    exehost[h.host.hostip]={}
                    exehost[h.host.hostip]["funcexeid"]=h.id
                    exehost[h.host.hostip]["status"]=h.status
                    exehost[h.host.hostip]["success"] = h.success
                    exehost[h.host.hostip]["idc"] = h.host.idc.idcname
                    exehost[h.host.hostip]["nowver"]=h.funcevent.app.tv
                    exehost[h.host.hostip]["destver"] = h.funcevent.app.ziptest
            resp = {"status":"success","hosts":exehost,"funceventid":funceventid}
            return HttpResponse(json.dumps(resp), content_type="application/json")
        if destver=='pre' and app.prehost.all().exists():
            action=""
            if not app.funcevent_set.filter(Q(destenv='pre')&Q(status='1')).exists():
                if app.zippre == app.prerb1:
                    action="rollback"
                    tfunc = Funcevent(app=app, create_time=timezone.now(), exeuser=req.user, eventtype='rollback',status='1', destenv='pre', zip=app.zippre)
                else:
                    action = "update"
                    tfunc=Funcevent(app=app,create_time =timezone.now(),exeuser=req.user,eventtype='update',status='1',destenv='pre',zip=app.zippre)
                tfunc.save()
                for h in app.prehost.all():
                    f = Funcexe(funcevent=tfunc,host=h,status='1',destenv='pre')
                    f.save()
            exehost={}
            funceventid=''
            for i in app.funcevent_set.filter(Q(destenv='pre')&Q(status='1')):
                funceventid=i.id

                for h in i.funcexe_set.filter(destenv='pre'):
                    exehost[h.host.hostip]={}
                    exehost[h.host.hostip]["funcexeid"]=h.id
                    exehost[h.host.hostip]["status"]=h.status
                    exehost[h.host.hostip]["success"] = h.success
                    exehost[h.host.hostip]["idc"] = h.host.idc.idcname
                    exehost[h.host.hostip]["nowver"]=h.funcevent.app.prenow
                    exehost[h.host.hostip]["destver"] = h.funcevent.app.zippre
            resp = {"status":"success","hosts":exehost,"funceventid":funceventid,"action":action}
            return HttpResponse(json.dumps(resp), content_type="application/json")
        if destver=='prd' and app.prdhost.all().exists():
            action = ""
            if not app.funcevent_set.filter(Q(destenv='prd')&Q(status='1')).exists():
                if app.zipprd == app.rb1:
                    action = "rollback"
                    tfunc=Funcevent(app=app,create_time =timezone.now(),exeuser=req.user,eventtype='rollback',status='1',destenv='prd',zip=app.zipprd)
                else:
                    action = "update"
                    tfunc = Funcevent(app=app, create_time=timezone.now(), exeuser=req.user, eventtype='update',status='1', destenv='prd', zip=app.zipprd)
                tfunc.save()
                for h in app.prdhost.all():
                    f = Funcexe(funcevent=tfunc,host=h,status='1',destenv='prd')
                    f.save()
            exehost={}
            funceventid=''
            for i in app.funcevent_set.filter(Q(destenv='prd')&Q(status='1')):
                funceventid=i.id
                for h in i.funcexe_set.filter(destenv='prd'):
                    exehost[h.host.hostip]={}
                    exehost[h.host.hostip]["funcexeid"]=h.id
                    exehost[h.host.hostip]["status"]=h.status
                    exehost[h.host.hostip]["success"] = h.success
                    exehost[h.host.hostip]["idc"] = h.host.idc.idcname
                    exehost[h.host.hostip]["nowver"]=h.funcevent.app.now
                    exehost[h.host.hostip]["destver"] = h.funcevent.app.zipprd
            resp = {"status":"success","hosts":exehost,"funceventid":funceventid,"action":action}
            return HttpResponse(json.dumps(resp), content_type="application/json")
        resp = {"status":"fail","msg":"当前环境没有关联任何机器,请为工程对应环境申请机器。"}
        return HttpResponse(json.dumps(resp), content_type="application/json")
    else:
        if req.user.is_superuser == 1:
            apps = Apps.objects.filter(Q(stats='1')&(Q(prdlock='2')|Q(prelock='2')|~Q(ziptest='')))
        else:
            apps = []
            gs = req.user.groups.all()
            for g in gs:
                aps = g.apps_set.filter(Q(stats='1')&(Q(prdlock='2')|Q(prelock='2')|~Q(ziptest='')))
                print type(aps)
                for a in aps:
                    # print a
                    apps.append(a)
    return render_to_response('updatemanage/doupdate.html',locals())

@login_required
def docallbak(req):
    return render_to_response('updatemanage/docallbak.html',locals())

@login_required
def uphistory(req):
    fexeevents=Funcevent.objects.all()[0:100]
    return render_to_response('updatemanage/uphistory.html',locals())

@login_required
def process(req):
    return render_to_response('updatemanage/process.html',locals())

