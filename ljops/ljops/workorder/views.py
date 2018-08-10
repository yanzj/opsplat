# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
#from django.shortcuts import render
from django.shortcuts import render_to_response
from ljapps.models import Apps ,Ports,Porttype
from django.http import HttpResponse
from ljops.settings import fix7script,fix8script,tomcat7,tomcat8
import json,re
from django.db.models import Q
#import jenkins
from time import sleep
import threading,subprocess,signal
import logging
logger = logging.getLogger('django')

@login_required
def newapp(req):
    if req.method == 'POST':
        aid = req.POST['aid']
        action = req.POST['action']
        app=Apps.objects.get(pk=aid)
        if action=="tongguo":
            if app.apptype.typename=='dubbo' or app.apptype.typename=='daemon':
                app.stats = 1
                app.save()
                resp = {"msg": "此立项通过。"}
                return HttpResponse(json.dumps(resp), content_type="application/json")

            #1 设置jenkins，拷贝template项目到对应的jenkins新项目
            #server = jenkins.Jenkins(jkurl, username=jkusername, password=jkpassword)
            #configxml=server.get_job_config('template')
            #newconfigxml=re.sub('<url>(.*?)</url>','</url>'+app.versionurl+'</url>',configxml)
            #server.create_job(app.appname,configxml)
            # 2 生成tomcat的包
            print app.urllocation
            if app.apptype.typename == 'tomcat':
                s=True
                if app.jdkversion=="1.7":
                    cmdstr="%s %s %s %s %s %s"%(fix7script,app.appname,Ports.objects.get(app=app,porttype=Porttype.objects.get(porttype='http')).portnum,Ports.objects.get(app=app,porttype=Porttype.objects.get(porttype='tomcat_shutdown')).portnum,tomcat7,app.id)
                    cmdstr= cmdstr +" "+ '"'+app.urllocation+'"'
                    p = subprocess.Popen(cmdstr,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,close_fds=True)
                    while p.poll() == None:
                        sleep(1)
                    if p.poll() == 0:
                        pass
                    else:
                        s = False
                if app.jdkversion=="1.8":
                    cmd="%s %s %s %s %s %s"%(fix8script,app.appname,Ports.objects.get(app=app,porttype=Porttype.objects.get(porttype='http')).portnum,Ports.objects.get(app=app,porttype=Porttype.objects.get(porttype='tomcat_shutdown')).portnum,tomcat8,app.id)
                    print cmd
                    smdstr="%s %s %s %s %s %s"%(fix8script,app.appname,Ports.objects.get(app=app,porttype=Porttype.objects.get(porttype='http')).portnum,Ports.objects.get(app=app,porttype=Porttype.objects.get(porttype='tomcat_shutdown')).portnum,tomcat8,app.id)
                    cmdstr = cmdstr + " " + '"' + app.urllocation + '"'
                    p = subprocess.Popen(cmdstr, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True, close_fds=True)
                    while p.poll() == None:
                        sleep(1)
                    if p.poll() == 0:
                        pass
                    else:
                        s = False
                print p.stdout.read()
                try:
                    if p.stdin:
                        p.stdin.close()
                    if   p.stdout:
                        p.stdout.close()
                    if p.stderr:
                        p.stderr.close()
                except:
                    print 'ok'
                if s == False:
                    resp = {"msg": "立项脚本故障。"}
                    return HttpResponse(json.dumps(resp), content_type="application/json")
                else:
                    #app.stats=1
                    #app.save()
                    resp = {"msg": "此立项通过。"}
                    return HttpResponse(json.dumps(resp), content_type="application/json")
        else:
            app.stats=2
            app.save()
            resp={"msg": "此立项废弃。"}
            return HttpResponse(json.dumps(resp), content_type="application/json")
    else:
        #print req.user.id
        apps=Apps.objects.filter(stats='0')
        return render_to_response('workorder/newapp.html',locals())


@login_required
def update(req):
    if req.method == 'POST':
        aid = req.POST['aid']
        v = req.POST['v']
        action=req.POST['action']
        app=Apps.objects.get(pk=aid)
        print aid,v,action
        if v=='prd':
            if action=="tongguo":
                app.prdlock=2
            else:
                app.prdlock=0
                app.zipprd=''
            app.save()
        if v=="pre":
            if action=="tongguo":
                app.prelock=2
            else:
                app.prelock=0
                app.zippre=''
            app.save()
        #if action=="tongguo":
        resp = {"msg": "审批完成"}
        return HttpResponse(json.dumps(resp), content_type="application/json")
    else:
        if req.user.is_superuser == 1:
            apps = Apps.objects.filter(Q(stats='1')&(Q(prdlock='1')|Q(prelock='1')))
        else:
            apps = []
            gs = req.user.groups.all()
            for g in gs:
                aps = g.apps_set.filter(Q(stats='1')&(Q(prdlock='1')|Q(prelock='1')))
                print type(aps)
                for a in aps:
                    # print a
                    apps.append(a)
        print apps
        return render_to_response('workorder/update.html', locals())
