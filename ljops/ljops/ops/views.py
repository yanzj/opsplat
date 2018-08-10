# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
# Create your views here.
from ljops.settings import jkpassword ,jkusername,jkurl,jdk7,jdk8,tomcat7,tomcat8
from ljapps.models import Apps,Funcevent,Funcexe,Host,Idc,Ports,Porttype,Balance,Balance_attr,Apptype,Build_history
from django.http import HttpResponse
from django.db.models import Q
import json,jenkins
from django.core.paginator import Paginator
import threading,subprocess
from time import sleep
from django.utils import timezone
import logging
logger = logging.getLogger('django')
#@login_required
def add_appv(req):
    if req.method == 'POST':
        aid = req.POST['aid']
        appv = req.POST['appv']
        app=Apps.objects.get(pk=aid)
        app.appv=appv
        app.stats='1'
        app.save()
        resp = {"msg": "success"}
        return HttpResponse(json.dumps(resp), content_type="application/json")
    else:
        resp = {"msg": "error"}
        return HttpResponse(json.dumps(resp), content_type="application/json")

def addappversion(req):
    if req.method == 'POST':
        appname = req.POST['appname']
        filename = req.POST['filename']
        dest=req.POST['dest']
        branch=req.POST['branch']
        app=Apps.objects.get(appname=appname)
        #if dest=='test':
        #    app.ziptest=filename
        if dest=='pre':
            if app.prelock=='1' or app.prelock=='2' :
                resp = {"msg": "状态锁定，无法更新新包"}
                return HttpResponse(json.dumps(resp), content_type="application/json")
            else:
                app.zippre=filename
                resp = {"msg": "success"}
        if dest=='prd':
            if app.prdlock=='1' or app.prdlock=='2':
                resp = {"msg": "状态锁定，无法更新新包"}
                return HttpResponse(json.dumps(resp), content_type="application/json")
            else:
                app.zipprd=filename
                resp = {"msg": "success"}
        if dest=='test':
            if  app.funcevent_set.filter(Q(destenv='test') & Q(status='1')).exists():
                resp = {"msg": "测试环境有更新未完成，新包无法更新数据库"}
            else:
                app.ziptest = filename
                resp = {"msg": "success"}
        app.save()
        bh=Build_history()
        bh.app=app
        bh.filename=filename
        bh.dest=dest
        bh.branch=branch
        bh.save()
        return HttpResponse(json.dumps(resp), content_type="application/json")
    else:
        resp = {"msg": "success"}
        return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def app_versiontype(req):
    if req.method == 'POST':
        aid = req.POST['appid']
        app=Apps.objects.get(pk=aid)
        resp = {"data": app.versionmanage}
        return HttpResponse(json.dumps(resp), content_type="application/json")
    else:
        resp = {"msg": "success"}
        return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def checkres(req):
    if req.method == 'POST':
        aid = req.POST['aid']
        jobnum = req.POST['jobnum']
        print jobnum
        app=Apps.objects.get(pk=aid)
        server = jenkins.Jenkins(jkurl, username=jkusername, password=jkpassword)
        res=server.get_build_info(app.appname, int(jobnum))['result']
        building=server.get_build_info(app.appname, int(jobnum))['building']
        print res,building
        if res =="SUCCESS" and building ==False:
            print
            resp = {"status": "SUCCESS"}
            return HttpResponse(json.dumps(resp), content_type="application/json")
        elif res =="FAILURE" and building ==False:
            resp = {"status": "FAILURE"}
            return HttpResponse(json.dumps(resp), content_type="application/json")
        else:
            resp = {"status": "RUNNING"}
            return HttpResponse(json.dumps(resp), content_type="application/json")
    else:
        resp = {"msg": "success"}
        return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def consoleout(req):
    if req.method == 'POST':
        aid = req.POST['aid']
        server = jenkins.Jenkins(jkurl, username=jkusername, password=jkpassword)
        app=Apps.objects.get(pk=aid)
        jobnum=server.get_job_info(app.appname)['lastBuild']['number']
        out = server.get_build_console_output(app.appname, jobnum)
        resp = {"out": out}
        return HttpResponse(json.dumps(resp), content_type="application/json")
    else:
        resp = {"msg": "success"}
        return HttpResponse(json.dumps(resp), content_type="application/json")

class uphost(threading.Thread):
    def __init__(self,  funcexe):
        threading.Thread.__init__(self)
        self.funcexe=funcexe
    def run(self):
        app=self.funcexe.funcevent.app
        #1，判断是测试环境，直接更新；预发布环境直接更新；生产环境，先判断项目类型，dubbo，deamon直接更新，tomcat,判断是否就1台机器，（1台直接更新不切负载）判断有无负载均衡，有在判断负载均衡，切走流量，更新，切回流量
        if self.funcexe.destenv=="test" or self.funcexe.destenv=="pre":
            if self.funcexe.funcevent.app.apptype.typename=="tomcat":
                if app.jdkversion=="1.7":
                    command="salt '%s'  cmd.script   salt://scripts/web.sh 'update %s %s %s %s %s' env='{\"LC_ALL\": \"\"}'"%(self.funcexe.host.hostip,self.funcexe.funcevent.app.appname,self.funcexe.funcevent.app.appv,self.funcexe.funcevent.zip,jdk7,tomcat7)
                if app.jdkversion=="1.8":
                    command="salt '%s'  cmd.script   salt://scripts/web.sh 'update %s %s %s %s %s' env='{\"LC_ALL\": \"\"}'"%(self.funcexe.host.hostip,self.funcexe.funcevent.app.appname,self.funcexe.funcevent.app.appv,self.funcexe.funcevent.zip,jdk8,tomcat8)
                try:
                    p = subprocess.Popen("%s" % command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
                    while p.poll() == None:
                        sleep(1)
                except:
                    #会被else覆盖，输出到日志
                    self.funcexe.output=self.funcexe.output + "执行异常:%s"%command
                    self.funcexe.status="3"
                    self.funcexe.success=False
                    self.funcexe.end_time=timezone.now()
                    self.funcexe.save()
                if p.poll()==0:
                    self.funcexe.output = self.funcexe.output + "command:%s     [output]"%command +  p.stdout.read()
                    self.funcexe.status="3"
                    self.funcexe.success=True
                    self.funcexe.end_time = timezone.now()
                    self.funcexe.save()
                else:
                    self.funcexe.output =self.funcexe.output + "command:%s     [output]"%command +  p.stdout.read()
                    self.funcexe.status = "3"
                    self.funcexe.success = False
                    self.funcexe.end_time = timezone.now()
                    self.funcexe.save()
            else:
                #dubbo与deamon程序上线
                if app.jdkversion=="1.7":
                    command="salt '%s'  cmd.script   salt://scripts/dub.sh 'update %s %s %s ' env='{\"LC_ALL\": \"\"}'"%(self.funcexe.host.hostip,self.funcexe.funcevent.app.appname,self.funcexe.funcevent.zip,jdk7)
                if app.jdkversion=="1.8":
                    command="salt '%s'  cmd.script   salt://scripts/dub.sh 'update %s %s %s ' env='{\"LC_ALL\": \"\"}'"%(self.funcexe.host.hostip,self.funcexe.funcevent.app.appname,self.funcexe.funcevent.zip,jdk8)
                try:
                    p = subprocess.Popen("%s" % command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
                    while p.poll() == None:
                        sleep(1)
                except:
                    #会被else覆盖，输出到日志
                    self.funcexe.output=self.funcexe.output + "执行异常:%s"%command
                    self.funcexe.status="3"
                    self.funcexe.success=False
                    self.funcexe.end_time = timezone.now()
                    self.funcexe.save()
                if p.poll()==0:
                    self.funcexe.output = self.funcexe.output + "command:%s     [output]"%command +  p.stdout.read()
                    self.funcexe.status="3"
                    self.funcexe.success=True
                    self.funcexe.end_time = timezone.now()
                    self.funcexe.save()
                else:
                    self.funcexe.output = self.funcexe.output + "command:%s     [output]"%command +  p.stdout.read()
                    self.funcexe.status = "3"
                    self.funcexe.success = False
                    self.funcexe.end_time = timezone.now()
                    self.funcexe.save()
        if self.funcexe.destenv == "prd":
            #生产tomcat，检查机器数量，两台以上的切流量需要
            if self.funcexe.funcevent.app.apptype.typename=="tomcat":
                if app.jdkversion=="1.7":
                    command="salt '%s'  cmd.script   salt://scripts/web.sh 'update %s %s %s %s %s' env='{\"LC_ALL\": \"\"}'"%(self.funcexe.host.hostip,self.funcexe.funcevent.app.appname,self.funcexe.funcevent.app.appv,self.funcexe.funcevent.zip,jdk7,tomcat7)
                if app.jdkversion=="1.8":
                    command="salt '%s'  cmd.script   salt://scripts/web.sh 'update %s %s %s %s %s' env='{\"LC_ALL\": \"\"}'"%(self.funcexe.host.hostip,self.funcexe.funcevent.app.appname,self.funcexe.funcevent.app.appv,self.funcexe.funcevent.zip,jdk8,tomcat8)
                if self.funcexe.funcevent.app.prdhost.all().count()>1:
                    # 查询是否有负载均衡，没有直接升级，有切流量
                    if app.balance_attr_set.all().exists():
                        for ba in app.balance_attr_set.all():
                            if ba.idc == self.funcexe.host.idc:
                                #如果有多个负载均衡需要切换，
                                #切走流量
                                try:
                                    ports=app.ports_set.all()
                                    for port in ports:
                                        if port.porttype.porttype=="http":
                                            portnum=port.portnum
                                    cmdstr="salt '%s'  cmd.script   salt://scripts/nginx_backend_down.sh '%s %s'"%(ba.balance_vip,self.funcexe.host.hostip,portnum)
                                    p = subprocess.Popen("%s" % cmdstr, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
                                    while p.poll() == None:
                                        sleep(1)
                                    sleep(10)
                                except:
                                    self.funcexe.output = self.funcexe.output+ "切流量失败,command: " +cmdstr
                        try:
                            p = subprocess.Popen("%s" % command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
                            while p.poll() == None:
                                sleep(1)
                        except:
                            # 会被else覆盖，输出到日志
                            self.funcexe.output =self.funcexe.output + "执行异常:%s" % command
                            self.funcexe.status = "3"
                            self.funcexe.success = False
                            self.funcexe.save()
                        for ba in app.balance_attr_set.all():
                            if ba.idc == self.funcexe.host.idc:
                                #切回流量
                                try:
                                    ports=app.ports_set.all()
                                    for port in ports:
                                        if port.porttype.porttype=="http":
                                            portnum=port.portnum
                                    cmdstr="salt '%s'  cmd.script   salt://scripts/nginx_backend_up.sh '%s %s'"%(ba.balance_vip,self.funcexe.host.hostip,portnum)
                                    #tomcat启动加载时间45秒
                                    sleep(45)
                                    p = subprocess.Popen("%s" % cmdstr, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
                                    while p.poll() == None:
                                        sleep(1)
                                    sleep(10)
                                except:
                                    self.funcexe.output = self.funcexe.output + "切流量失败,command: " + cmdstr
                    else:
                        #生产没有负载均衡，直接升级
                        try:
                            p = subprocess.Popen("%s" % command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
                            while p.poll() == None:
                                sleep(1)
                        except:
                            # 会被else覆盖，输出到日志
                            self.funcexe.output =self.funcexe.output + "执行异常:%s" % command
                            self.funcexe.status = "3"
                            self.funcexe.success = False
                            self.funcexe.end_time = timezone.now()
                            self.funcexe.save()
                else:
                    #机器数量1，直接升级
                    try:
                        p = subprocess.Popen("%s" % command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
                        while p.poll() == None:
                            sleep(1)
                    except:
                        #会被else覆盖，输出到日志
                        self.funcexe.output=self.funcexe.output + "执行异常:%s"%command
                        self.funcexe.status="3"
                        self.funcexe.success=False
                        self.funcexe.end_time = timezone.now()
                        self.funcexe.save()
                if p.poll()==0:
                    self.funcexe.output =self.funcexe.output + "command:%s     [output]"%command +  p.stdout.read()
                    self.funcexe.status="3"
                    self.funcexe.success=True
                    self.funcexe.end_time = timezone.now()
                    self.funcexe.save()
                else:
                    self.funcexe.output = self.funcexe.output + "command:%s     [output]"%command +  p.stdout.read()
                    self.funcexe.status = "3"
                    self.funcexe.success = False
                    self.funcexe.end_time = timezone.now()
                    self.funcexe.save()
            else:
                #dubbo与deamon程序上线
                if app.jdkversion=="1.7":
                    command="salt '%s'  cmd.script   salt://scripts/dub.sh 'update %s %s %s ' env='{\"LC_ALL\": \"\"}'"%(self.funcexe.host.hostip,self.funcexe.funcevent.app.appname,self.funcexe.funcevent.zip,jdk7)
                if app.jdkversion=="1.8":
                    command="salt '%s'  cmd.script   salt://scripts/dub.sh 'update %s %s %s ' env='{\"LC_ALL\": \"\"}'"%(self.funcexe.host.hostip,self.funcexe.funcevent.app.appname,self.funcexe.funcevent.zip,jdk8)
                try:
                    p = subprocess.Popen("%s" % command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
                    while p.poll() == None:
                        sleep(1)
                except:
                    #会被else覆盖，输出到日志
                    self.funcexe.output=self.funcexe.output + "执行异常:%s"%command
                    self.funcexe.status="3"
                    self.funcexe.success=False
                    self.funcexe.end_time = timezone.now()
                    self.funcexe.save()
                if p.poll()==0:
                    self.funcexe.output = self.funcexe.output + "command:%s     [output]"%command +  p.stdout.read()
                    self.funcexe.status="3"
                    self.funcexe.success=True
                    self.funcexe.end_time = timezone.now()
                    self.funcexe.save()
                else:
                    self.funcexe.output = self.funcexe.output + "command:%s     [output]"%command +  p.stdout.read()
                    self.funcexe.status = "3"
                    self.funcexe.success = False
                    self.funcexe.end_time = timezone.now()
                    self.funcexe.save()



@login_required
def deploy(req):
    if req.method == 'POST':
        aid = req.POST['aid']
        funcexe=Funcexe.objects.get(pk=aid)
        if funcexe.status=='1':
            #开始running
            funcexe.status='2'
            funcexe.exec_time=timezone.now()
            funcexe.save()
            x=uphost(funcexe)
            x.start()
            resp = {"status": '1'}
            return HttpResponse(json.dumps(resp), content_type="application/json")
        elif funcexe.status=='2':
            resp = {"status": '2'}
            return HttpResponse(json.dumps(resp), content_type="application/json")
        else :
            resp = {"status": '3'}
            return HttpResponse(json.dumps(resp), content_type="application/json")
    else:
        resp = {"msg": "success"}
        return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def getdepres(req):
    #app=Apps.objects.get(pk='1')
    #app.balance_attr_set.all()
    if req.method == 'POST':
        aid = req.POST['aid']
        funcexe=Funcexe.objects.get(pk=aid)
        print funcexe.status
        print funcexe.success
        if funcexe.status=='3' and funcexe.success==True:
            resp = {"status": "SUCCESS"}
            return HttpResponse(json.dumps(resp), content_type="application/json")
        elif funcexe.status=='3' and funcexe.success==False:
            resp = {"status": "FAILURE"}
            return HttpResponse(json.dumps(resp), content_type="application/json")
        else:
            resp = {"status": "RUNNING"}
            return HttpResponse(json.dumps(resp), content_type="application/json")
    else:
        resp = {"msg": "success"}
        return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def done(req):
    if req.method == 'POST':
        fentid = req.POST['fentid']
        funcevent=Funcevent.objects.get(pk=fentid)
        f=False
        if  funcevent.funcexe_set.all().exists():
            n=funcevent.funcexe_set.all().count()
            x=0
            for fexe in funcevent.funcexe_set.all():
                if fexe.status=="3" and fexe.success==True:
                    x+=1
            if x==n:
                funcevent.end_time=timezone.now()
                funcevent.event_over=True
                funcevent.status='2'
                funcevent.result='1'
                funcevent.save()
                app=funcevent.app
                if funcevent.destenv=="test":
                    app.testlock='0'
                    app.tv=app.ziptest
                    app.ziptest=''
                    app.save()
                if funcevent.destenv=="pre":
                    if funcevent.eventtype=="rollback":
                        app.prelock = '0'
                        app.prenow=app.prerb1
                        app.prerb1=app.prerb2
                        app.prerb2 = ""
                        app.zippre = ''
                        app.save()
                    else:
                        app.prelock='0'
                        app.prerb2=app.prerb1
                        app.prerb1=app.prenow
                        app.prenow=app.zippre
                        app.zippre=''
                        app.save()
                if funcevent.destenv=="prd":
                    if funcevent.eventtype == "rollback":
                        app.prelock="0"
                        app.now=app.rb1
                        app.rb1=app.rb2
                        app.rb2=""
                        app.zipprd=""
                        app.save()
                    else:
                        app.prelock='0'
                        app.prdrb2=app.prdrb1
                        app.prdrb1=app.prdnow
                        app.prenow=app.zipprd
                        app.zipprd=''
                        app.save()
                resp = {"status":"success","msg": "上线完成"}
                return HttpResponse(json.dumps(resp), content_type="application/json")
            else:
                resp = {"status":"error","msg": "上线未完成，或者有主机上线失败"}
                return HttpResponse(json.dumps(resp), content_type="application/json")
        resp = {"status":"error","msg": "还未开始上线"}
        return HttpResponse(json.dumps(resp), content_type="application/json")
    else:
        resp = {"msg": "success"}
        return HttpResponse(json.dumps(resp), content_type="application/json")


class roll(threading.Thread):
    def __init__(self,  funcexe):
        threading.Thread.__init__(self)
        self.funcexe=funcexe
    def run(self):
        app=self.funcexe.funcevent.app




@login_required
def rollback(req):
    if req.method == 'POST':
        fentid = req.POST['fentid']
        funcevent = Funcevent.objects.get(pk=fentid)
        app=funcevent.app
        if funcevent.destenv=='test':
            resp = {"status":"error","msg": "test环境不回滚"}
            return HttpResponse(json.dumps(resp), content_type="application/json")
        #预发布环境回滚
        if funcevent.destenv == 'pre' :
            status=True
            for fexe in funcevent.funcexe_set.all():
                if fexe.status=='2':
                    status=False
            if status==False:
                resp = {"status": "error", "msg": "有机器正在升级无法回滚"}
                return HttpResponse(json.dumps(resp), content_type="application/json")
            else:
                for fexe in funcevent.funcexe_set.all():
                    if fexe.status=='3':
                        if app.apptype=="tomcat":
                            if app.jdkversion == "1.7":
                                command = "salt '%s'  cmd.script   salt://scripts/web.sh 'update %s %s %s %s %s' env='{\"LC_ALL\": \"\"}'" % (fexe.host.hostip, fexe.funcevent.app.appname,fexe.funcevent.app.appv, fexe.funcevent.app.pv, jdk7, tomcat7)
                            if app.jdkversion == "1.8":
                                command = "salt '%s'  cmd.script   salt://scripts/web.sh 'update %s %s %s %s %s' env='{\"LC_ALL\": \"\"}'" % (fexe.host.hostip, fexe.funcevent.app.appname,fexe.funcevent.app.appv, fexe.funcevent.app.pv, jdk8, tomcat8)
                            try:
                                p = subprocess.Popen("%s" % command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
                                while p.poll() == None:
                                    sleep(1)
                            except:
                                # 会被else覆盖，输出到日志
                                fexe.output = fexe.output + "回滚command:%s     [output]"%command
                                fexe.status = "3"
                                fexe.success = False
                                fexe.rollback='2'
                                fexe.save()
                            if p.poll() == 0:
                                fexe.output = fexe.output + "回滚command:%s     [output]"%command +  p.stdout.read()
                                fexe.status = "3"
                                fexe.success = True
                                fexe.rollback='1'
                                fexe.save()
                            else:
                                fexe.output = fexe.output + "回滚command:%s     [output]"%command +  p.stdout.read()
                                fexe.status = "3"
                                fexe.success = False
                                fexe.rollback='2'
                                fexe.save()
                        else:
                            #dubbo与deamon项目
                            if app.jdkversion == "1.7":
                                command = "salt '%s'  cmd.script   salt://scripts/dub.sh 'update %s %s %s ' env='{\"LC_ALL\": \"\"}'" % (fexe.host.hostip, fexe.funcevent.app.appname, fexe.funcevent.app.pv, jdk7)
                            if app.jdkversion == "1.8":
                                command = "salt '%s'  cmd.script   salt://scripts/dub.sh 'update %s %s %s ' env='{\"LC_ALL\": \"\"}'" % (fexe.host.hostip, fexe.funcevent.app.appname, fexe.funcevent.app.pv, jdk8)
                            try:
                                p = subprocess.Popen("%s" % command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
                                while p.poll() == None:
                                    sleep(1)
                            except:
                                # 会被else覆盖，输出到日志
                                fexe.output = fexe.output + "回滚command:%s     [output]"%command
                                fexe.status = "3"
                                fexe.success = False
                                fexe.rollback='2'
                                fexe.save()
                            if p.poll() == 0:
                                fexe.output = fexe.output + "回滚command:%s     [output]"%command +  p.stdout.read()
                                fexe.status = "3"
                                fexe.success = True
                                fexe.rollback='1'
                                fexe.save()
                            else:
                                fexe.output = fexe.output + "回滚异常command:%s     [output]"%command +  p.stdout.read()
                                fexe.status = "3"
                                fexe.success = False
                                fexe.rollback='2'
                                fexe.save()
                funcevent.result='0'
                funcevent.status='2'
                funcevent.event_over=True
                funcevent.end_time=timezone.now()
                funcevent.save()
                app.zippre=''
                app.prelock='0'
                app.save()
                resp = {"status": "success", "msg": "回滚完成"}
                return HttpResponse(json.dumps(resp), content_type="application/json")
        #生产环境回滚
        if funcevent.destenv=="prd":
            status=True
            for fexe in funcevent.funcexe_set.all():
                if fexe.status=='2':
                    status=False
            if status==False:
                resp = {"status": "error", "msg": "有机器正在升级无法回滚"}
                return HttpResponse(json.dumps(resp), content_type="application/json")
            else:
                for fexe in funcevent.funcexe_set.all():
                #生产tomcat，检查机器数量，两台以上的切流量需要
                    if fexe.funcevent.app.apptype.typename=="tomcat":
                        if app.jdkversion=="1.7":
                            command="salt '%s'  cmd.script   salt://scripts/web.sh 'update %s %s %s %s %s' env='{\"LC_ALL\": \"\"}'"%(fexe.host.hostip,fexe.funcevent.app.appname,fexe.funcevent.app.appv,fexe.funcevent.app.now,jdk7,tomcat7)
                        if app.jdkversion=="1.8":
                            command="salt '%s'  cmd.script   salt://scripts/web.sh 'update %s %s %s %s %s' env='{\"LC_ALL\": \"\"}'"%(fexe.host.hostip,fexe.funcevent.app.appname,fexe.funcevent.app.appv,fexe.funcevent.app.now,jdk8,tomcat8)
                        if fexe.funcevent.app.prdhost.all().count()>1:
                            # 查询是否有负载均衡，没有直接升级，有切流量
                            if app.balance_attr_set.all().exists():
                                for ba in app.balance_attr_set.all():
                                    if ba.idc == fexe.host.idc:
                                        #如果有多个负载均衡需要切换，
                                        #切走流量
                                        try:
                                            ports = app.ports_set.all()
                                            for port in ports:
                                                if port.porttype.porttype == "http":
                                                    portnum = port.portnum
                                            cmdstr = "salt '%s'  cmd.script   salt://scripts/nginx_backend_down.sh '%s %s'" % (ba.balance_vip, fexe.host.hostip, portnum)
                                            p = subprocess.Popen("%s" % cmdstr, stdin=subprocess.PIPE,
                                                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                                 shell=True)
                                            while p.poll() == None:
                                                sleep(1)
                                            sleep(10)
                                        except:
                                            fexe.output = fexe.output + "回滚切流量失败 command: %s"%cmdstr
                                try:
                                    p = subprocess.Popen("%s" % command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                                    while p.poll() == None:
                                        sleep(1)
                                except:
                                    # 会被else覆盖，输出到日志
                                    fexe.output = fexe.output + "回滚异常:%s" % command
                                    fexe.status = "3"
                                    fexe.success = False
                                    fexe.rollback='2'
                                    fexe.save()
                                for ba in app.balance_attr_set.all():
                                    if ba.idc == fexe.host.idc:
                                        #切回流量
                                        try:
                                            ports = app.ports_set.all()
                                            for port in ports:
                                                if port.porttype.porttype == "http":
                                                    portnum = port.portnum
                                            cmdstr = "salt '%s'  cmd.script   salt://scripts/nginx_backend_up.sh '%s %s'" % (ba.balance_vip, fexe.host.hostip, portnum)
                                            sleep(45)
                                            p = subprocess.Popen("%s" % cmdstr, stdin=subprocess.PIPE,
                                                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                                 shell=True)
                                            while p.poll() == None:
                                                sleep(1)
                                            sleep(10)
                                        except:
                                            fexe.output + "回滚切流量失败 command: %s" % cmdstr
                            else:
                                #生产没有负载均衡，直接升级
                                try:
                                    p = subprocess.Popen("%s" % command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
                                    while p.poll() == None:
                                        sleep(1)
                                except:
                                    # 会被else覆盖，输出到日志
                                    fexe.output = fexe.output + "回滚异常:%s" % command
                                    fexe.status = "3"
                                    fexe.success = False
                                    fexe.rollback='2'
                                    fexe.save()
                        else:
                            #机器数量1，直接升级
                            try:
                                p = subprocess.Popen("%s" % command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
                                while p.poll() == None:
                                    sleep(1)
                            except:
                                #会被else覆盖，输出到日志
                                fexe.output=fexe.output + "回滚异常:%s"%command
                                fexe.status="3"
                                fexe.success=False
                                fexe.rollback='2'
                                fexe.save()
                        if p.poll()==0:
                            fexe.output = fexe.output + "回滚command:%s     [output]"%command +  p.stdout.read()
                            fexe.status="3"
                            fexe.success=True
                            fexe.rollback='1'
                            fexe.save()
                        else:
                            fexe.output = fexe.output + "回滚异常command:%s     [output]"%command +  p.stdout.read()
                            fexe.status = "3"
                            fexe.success = False
                            fexe.rollback = '2'
                            fexe.save()
                funcevent.result='0'
                funcevent.status='2'
                funcevent.event_over=True
                funcevent.end_time=timezone.now()
                funcevent.save()
                app.zipprd=''
                app.prdlock='0'
                app.save()
                resp = {"status": "success", "msg": "回滚完成"}
                return HttpResponse(json.dumps(resp), content_type="application/json")
    else:
        resp = {"msg": "success"}
        return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def showproject(req):
    offset = req.GET.get('offset')
    limit= req.GET.get('limit')

    if req.user.is_superuser == 1:
        apps = Apps.objects.filter(stats='1')
        all_records_count=apps.count()
    else:
        apps = []
        gs = req.user.groups.all()
        for g in gs:
            aps = g.apps_set.filter(stats='1')
            apps.extend(aps)
        all_records_count=apps.count()
    print '1111111111'
    if not offset:
        offset = 0
    if not limit:
        limit=25
    print apps
    pageinator = Paginator(apps, limit)
    page = int(int(offset) / int(limit) + 1)
    resp={'total':all_records_count,'rows':[]}
    for asset in pageinator.page(page):
        #print asset
        testhost=''
        prehost=''
        prdhost=''
        for i in asset.testhost.all():
            testhost=testhost+i.hostip+';'

        for i in asset.prehost.all():
            prehost=prehost+i.hostip+';'
        for i in asset.prdhost.all():
            prdhost=prdhost+i.hostip+';'
        http=''
        tomcat_shutdown=''
        tcp=''
        for i in asset.ports_set.all():
            if i.porttype.porttype == 'http':
                http=i.portnum
            if i.porttype.porttype == 'tomcat_shutdown':
                tomcat_shutdown=i.portnum
            if i.porttype.porttype == 'tcp':
                tcp = tcp + i.portnum +';'
        resp['rows'].append({
            'appname':asset.appname,
            'apptype':asset.apptype.typename,
            'appsgroup':asset.appsgroup.name,
            'versionmanage':asset.versionmanage,
            'versionurl':asset.versionurl,
            'jdkversion':asset.jdkversion,
            'tomcatversion':asset.tomcatversion,
            'http':http,
            'tomcat_shutdown':tomcat_shutdown,
            'tcp':tcp,
            'testhost':testhost,
            'prehost':prehost,
            'prdhost':prdhost,
            'now':asset.now,
            'prenow':asset.prenow,
            'tv':asset.tv
        })


    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def getexelog(req):
    if req.method == 'POST':
        aid = req.POST['aid']
        funcexe = Funcexe.objects.get(pk=aid)
        resp = {"msg": funcexe.output}
        return HttpResponse(json.dumps(resp), content_type="application/json")
    else:
        resp = {"msg": ""}
        return HttpResponse(json.dumps(resp), content_type="application/json")
