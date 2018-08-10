# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
#from django.shortcuts import render
from django.shortcuts import render_to_response
from models import Apptype,Apps,Ports,Porttype,Group
from django.http import HttpResponse
import json,jenkins,re
from ljops.settings import jkpassword ,jkusername,jkurl
from models import Build_history
from django.contrib.auth.models import User
import logging
logger = logging.getLogger('django')
# Create your views here.

@login_required
def newapp(req):
    if req.method == 'POST':
        appname=req.POST['appname']
        apptype=req.POST['apptype']
        try:
            group = Group.objects.get(pk=req.POST['gid'])
            #print group
            if apptype=='tomcat':
                jdk=req.POST['jdk']
                tomcatversion=req.POST['tomcatversion']
                httpport=req.POST['httpport']
                versiontype = req.POST['versiontype']
                vurl = req.POST['vurl']
                shutdownport=req.POST['shutdownport']
                urllocation = req.POST['urllocation']
                otherport=req.POST.getlist('otherport[]')
                atp=Apptype.objects.get(typename=apptype)
                #print appname,atp,jdk,tomcatversion,otherport,shutdownport,httpport
                app = Apps()
                app.appname=appname
                app.urllocation=urllocation
                app.jdkversion=jdk
                app.tomcatversion=tomcatversion
                app.appsgroup=group
                app.apptype = atp
                app.versionmanage=versiontype
                app.versionurl=vurl
                app.save()
                app.user.add(req.user)
                app.save()
                porttype=Porttype.objects.get(porttype='http')
                port=Ports()
                port.porttype=porttype
                port.portnum=httpport
                port.app=app
                port.save()
                porttype=Porttype.objects.get(porttype='tomcat_shutdown')
                port=Ports()
                port.porttype=porttype
                port.portnum=shutdownport
                port.app=app
                port.save()
                if otherport!=[]:
                    porttype = Porttype.objects.get(porttype='tcp')
                    for p in otherport:
                        port = Ports()
                        port.porttype = porttype
                        port.portnum = p
                        port.app = app
                        port.save()
            elif apptype=='dubbo':
                jdk = req.POST['jdk']
                otherport = req.POST.getlist('dbotherport[]')
                atp = Apptype.objects.get(typename=apptype)
                #print appname,jdk,otherport,atp
                app = Apps()
                app.appname=appname
                app.jdkversion=jdk
                app.appsgroup=group
                app.apptype = atp
                versiontype = req.POST['versiontype']
                vurl = req.POST['vurl']
                app.versionmanage=versiontype
                app.versionurl=vurl
                app.save()
                app.user.add(req.user)
                app.save()
                print otherport
                if otherport!=[]:
                    porttype = Porttype.objects.get(porttype='tcp')
                    for p in otherport:
                        port = Ports()
                        port.porttype = porttype
                        port.portnum = p
                        port.app = app
                        port.save()
            elif apptype=='daemon':
                jdk = req.POST['jdk']
                otherport = req.POST.getlist('daemonotherport[]')
                atp = Apptype.objects.get(typename=apptype)
                app = Apps()
                app.appname=appname
                app.jdkversion=jdk
                app.appsgroup=group
                app.apptype = atp
                versiontype = req.POST['versiontype']
                vurl = req.POST['vurl']
                app.versionmanage=versiontype
                app.versionurl=vurl
                app.save()
                app.user.add(req.user)
                app.save()
                print otherport
                if otherport!=[]:
                    porttype = Porttype.objects.get(porttype='tcp')
                    for p in otherport:
                        port = Ports()
                        port.porttype = porttype
                        port.portnum = p
                        port.app = app
                        port.save()
            resp = {"msg": "立项申请成功，可联系运维审批。", "line": []}
            return HttpResponse(json.dumps(resp), content_type="application/json")
        except:
            resp={"msg": "立项故障，项目名称重复或数据库故障。", "line": []}
            return HttpResponse(json.dumps(resp), content_type="application/json")
    else:
        #print req.user.id
        apptypes=Apptype.objects.all()
        groups=Group.objects.all()
        return render_to_response('apps/newapp.html',locals())



@login_required
def confjks(req):
    if req.method == 'POST':
        appid=req.POST['appid']
        vurl=req.POST['vurl']
        jdk = req.POST['jdk']
        targetpath = req.POST['targetpath']
        versiontype = req.POST['versiontype']
        app=Apps.objects.get(pk=appid)
        app.jdkversion=jdk
        app.versionurl=vurl
        app.targetpath=targetpath
        app.versionmanage=versiontype
        app.save()
        try:
            server = jenkins.Jenkins(jkurl, username=jkusername, password=jkpassword)
            if not server.job_exists(app.appname):
                if app.versionmanage=='git':
                    configxml = server.get_job_config('git_template')
                    newconfigxml = re.sub(u'<url>(.*?)</url>', u'<url>' + vurl.decode('utf-8') + u'</url>', configxml)
                    newconfigxml = re.sub(u'<defaultValue>(.*?)</defaultValue>', u'<defaultValue>' + targetpath.decode('utf-8') + u'</defaultValue>', newconfigxml)
                    newconfigxml = re.sub(u'<jdk>(.*?)</jdk>',u'<jdk>jdk' + jdk.decode('utf-8') + u'</jdk>', newconfigxml)
                    server.create_job( app.appname, newconfigxml)
                else:
                    configxml = server.get_job_config('svn_template')
                    newconfigxml = re.sub(u'<remote>(.*?)</remote>', u'<remote>' + vurl.decode('utf-8') + u'</remote>', configxml)
                    newconfigxml = re.sub(u'<defaultValue>(.*?)</defaultValue>', u'<defaultValue>' + targetpath.decode('utf-8') + u'</defaultValue>', newconfigxml)
                    newconfigxml = re.sub(u'<jdk>(.*?)</jdk>',u'<jdk>jdk' + jdk.decode('utf-8')+ u'</jdk>', newconfigxml)
                    #print newconfigxml
                    server.create_job(app.appname, newconfigxml)

                resp = {"msg": "jenkins配置完成，可以打包发布。", "line": []}
            else:
                resp = {"msg": "jenkins项目已经存在", "line": []}
        except:
            resp = {"msg": "jenkins配置故障。", "line": []}
        return HttpResponse(json.dumps(resp), content_type="application/json")
    else:
        if req.user.is_superuser==1:
            apps=Apps.objects.filter(stats='1')
        else:
            apps=[]
            gs=req.user.groups.all()
            for g in gs:
                aps=g.apps_set.filter(stats='1')
                print type(aps)
                for a in aps:
                    #print a
                    apps.append(a)
        return render_to_response('apps/confjks.html',locals())

@login_required
def maketar(req):
    if req.method == 'POST':
        appid=req.POST['aid']
        ver=req.POST['ver']
        fenzhi = req.POST['fenzhi']
        app=Apps.objects.get(pk=appid)
        try:
            server = jenkins.Jenkins(jkurl, username=jkusername, password=jkpassword)
            if  server.job_exists(app.appname):
                jobnum = server.get_job_info(app.appname)['lastBuild']['number']
                jobnum = int(jobnum)+1
                if fenzhi=='0':
                    server.build_job(app.appname,{'environment':ver,"targetpath":app.targetpath})
                else:
                    server.build_job(app.appname,{'environment':ver,"targetpath":app.targetpath,"branch":fenzhi})

                resp = {"status": "success", "jobnum":str(jobnum)}
            else:
                resp = {"status": "error", "line": []}
        except:
            resp = {"status": "error", "msg":"服务器故障"}
        return HttpResponse(json.dumps(resp), content_type="application/json")
    else:
        if req.user.is_superuser==1:
            apps=Apps.objects.filter(stats='1')
        else:
            apps=[]
            gs=req.user.groups.all()
            for g in gs:
                aps=g.apps_set.filter(stats='1')
                print type(aps)
                for a in aps:
                    #print a
                    apps.append(a)
        return render_to_response('apps/maketar.html',locals())

@login_required
def myproject(req):

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

    return render_to_response('apps/myproject.html', locals())


@login_required
def jkshis(req):

    # if req.user.is_superuser == 1:
    #     apps = Apps.objects.filter(stats='1')
    # else:
    #     apps = []
    #     gs = req.user.groups.all()
    #     for g in gs:
    #         aps = g.apps_set.filter(stats='1')
    #         print type(aps)
    #         for a in aps:
    #             # print a
    #             apps.append(a)
    jkshiss=Build_history.objects.all()[0:100]

    return render_to_response('apps/jkshis.html', locals())