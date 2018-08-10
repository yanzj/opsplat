# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User, Group
from django.db import models
import django.utils.timezone as timezone
from django.contrib import admin
# Create your models here.

#环境  测试test  预发布pre  生产prd
class Line(models.Model):
    line_name = models.CharField(max_length=100,verbose_name='名称',unique=True)
    #line_describtion = models.CharField(max_length=100,verbose_name='描述',unique=True)
    line_level = models.IntegerField(default=0,verbose_name='等级')
    def __unicode__(self):
        return self.line_name

#机器类型,云主机，物理机，docker，kvm等
class Ostype(models.Model):
    ostype = models.CharField(max_length=100,unique=True)
    def __unicode__(self):
        return self.ostype
#机房，阿里云，腾讯云，自建机房等
class Idc(models.Model):
    idcname = models.CharField(max_length=100,unique=True)
    num = models.CharField(max_length=20,default=0)
    def __unicode__(self):
        return self.idcname

class Host(models.Model):
    idc = models.ForeignKey(Idc,blank=True)
    hostip = models.CharField(max_length=200,unique=True)
    line = models.ManyToManyField(Line,blank=True)
    ostype = models.ForeignKey(Ostype,blank=True)
    os_user = models.ManyToManyField(User,blank=True)
    os_group = models.ManyToManyField(Group,blank=True)
    lock = models.CharField(max_length=200,default=0)
    def __unicode__(self):
        return u'%s:%s'%(self.idc,self.hostip)


class Apptype(models.Model):
    typename = models.CharField(max_length=200,unique=True)
    def __unicode__(self):
        return self.typename

class Apps(models.Model):
    appname = models.CharField(max_length=200,unique=True)
    jdkversion = models.CharField(max_length=50,blank=True)
    tomcatversion = models.CharField(max_length=50,blank=True)
    urllocation = models.CharField(max_length=60,blank=True)
    prdhost = models.ManyToManyField(Host,related_name='prd_host',blank=True)
    prehost = models.ManyToManyField(Host,related_name='pre_host', blank=True)
    testhost = models.ManyToManyField(Host,related_name='test_host', blank=True)
    user = models.ManyToManyField(User,blank=True)
    appsgroup = models.ForeignKey(Group,blank=True)
    apptype = models.ForeignKey(Apptype,blank=True)
    #版本 now当前版本   rb1上个版本  rb2前个版本
    now =  models.CharField(max_length=200,blank=True)
    rb1 = models.CharField(max_length=200,blank=True)
    rb2 = models.CharField(max_length=200,blank=True)
    #生产的准备版本，刚打完的新包，更新后与now相同
    zipprd = models.CharField(max_length=200,blank=True)
    #test环境版本号
    tv = models.CharField(max_length=200,blank=True)
    # 测试的准备版本，刚打完的新包，更新后与tv相同
    ziptest = models.CharField(max_length=200, blank=True)
    #预发布环境版本号(字段废弃)
    pv = models.CharField(max_length=200,blank=True)
    #预发布环境版本 now当前版本   rb1上个版本  rb2前个版本
    prenow =  models.CharField(max_length=200,blank=True)
    prerb1 = models.CharField(max_length=200,blank=True)
    prerb2 = models.CharField(max_length=200,blank=True)
    # y预发布的准备版本，刚打完的新包,更新后与pv相同
    zippre = models.CharField(max_length=200, blank=True)
    lock = models.CharField(max_length=200,default=0)
    #newhostlock = models.CharField(max_length=200,default=0)
    #atype = models.CharField(max_length=20,blank=True)
    #0为新立项未审批的项目，1为审批通过,2为拒绝立项
    stats=models.CharField(max_length=10,default=0)
    #版本管理是git还是svn
    versionmanage = models.CharField(max_length=10, blank=True)
    #git的ssh地址，svn的ssh地址
    versionurl = models.CharField(max_length=200, blank=True)
    targetpath = models.CharField(max_length=200, blank=True)
    #appv, 立项后的tomcat包名称（独立进程无）
    appv=models.CharField(max_length=200, blank=True)
    #0没有开始升级，1为申请审批发布，1状态pre与prd不允许更新新包，审批通过后状态为2，为发布状态，发布状态不允许更新包，删除各环境的ziptest.zippre,zipprd字段,审批不通过lock为0删除各环境对应字段,
    testlock=models.CharField(max_length=10,default=0)
    prelock=models.CharField(max_length=10,default=0)
    prdlock=models.CharField(max_length=10,default=0)
    def __unicode__(self):
        return self.appname

class Funcevent(models.Model):
    app = models.ForeignKey(Apps,blank=True)
    create_time = models.DateTimeField(null=True, blank=True)
    exec_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    exeuser = models.CharField(max_length=50, blank=True)
    event_over = models.BooleanField(default=False)
    #表示事件类型，上线，回滚update   rollback
    eventtype = models.CharField(max_length=20,blank=True)
    #1 表示执行事件刚刚建立，2执行事件已经完成
    status=models.CharField(max_length=10,blank=True)
    #那个环境的上线
    destenv=models.CharField(max_length=10,blank=True)
    #要上线的包
    zip=models.CharField(max_length=200,blank=True)
    #上线结果0失败1成功
    result=models.CharField(max_length=10,blank=True)
    def __unicode__(self):
        return u'id:%s 项目名称:%s  事件类型:%s 提交时间:%s'%(self.id,self.app.appname,self.eventtype,self.create_time)
    class Meta:
        ordering = ['-id']

class Funcexe(models.Model):
    funcevent = models.ForeignKey(Funcevent,blank=True)
    host = models.ForeignKey(Host)
    exec_time = models.DateTimeField(null=True, blank=True)
    #1 notstart,2 running,3 end
    status=models.CharField(max_length=10,blank=True)
    success  = models.NullBooleanField()
    output = models.TextField(max_length=20000,blank=True)
    #要更新的目标环境test   pre  prd
    destenv=models.CharField(max_length=10,blank=True)
    #1 为回滚完成,2为回滚失败
    rollback=models.CharField(max_length=10,blank=True)
    def __unicode__(self):
        return u"时间id:%s 主机:%s 状态:%s 项目:%s"%(self.funcevent.id,self.host,self.status,self.funcevent.app.appname)

#暂未使用此表
class Action(models.Model):
    app=models.ForeignKey(Apps,blank=True)
    actionname=models.CharField(max_length=40)
    # 0
    status=models.CharField(max_length=10,default=0)
    output = models.TextField(max_length=10000, blank=True)


class Porttype(models.Model):
    porttype = models.CharField(max_length=30, unique=True)
    def __unicode__(self):
        return self.porttype

class Ports(models.Model):
    portnum = models.CharField(max_length=50)
    app = models.ForeignKey(Apps)
    porttype = models.ForeignKey(Porttype)
    comment = models.CharField(max_length=200)
    def __unicode__(self):
        return u'%s:%s' % (self.portnum, self.app.appname)


class Build_history(models.Model):
    app = models.ForeignKey(Apps, blank=True)
    filename=models.CharField(max_length=200, blank=True)
    dest=models.CharField(max_length=20, blank=True)
    branch=models.CharField(max_length=20, blank=True)
    def __unicode__(self):
        return self.filename
    class Meta:
        ordering = ['-id']

# 执行上线动作后产生历史记录
class Apps_history(models.Model):
    app = models.ForeignKey(Apps, blank=True)
    versions = models.CharField(max_length=200, blank=True)
    use_time = models.DateTimeField('上线日期', default=timezone.now)


# 负载均衡 lvs  haproxy  nginx
class Balance(models.Model):
    #lvs  haproxy  nginx
    balance_type = models.CharField(max_length=200)
    #负载均衡vip
    balance_name = models.CharField(max_length=200)
    def __unicode__(self):
        return u'%s:%s' % (self.balance_type, self.balance_name)


# 一个负载均衡服务，上面会对不同的服务做不同的监听vip配置
class Balance_attr(models.Model):
    app = models.ForeignKey(Apps, blank=True)
    balance = models.ForeignKey(Balance, blank=True)
    # 云主机的vip可以与真实ip相同
    balance_vip = models.CharField(max_length=200, blank=True)
    # port是lvs，haproxy等监听的端口(像lvs只对3层转发，不能解析域名，必须通过多端口转发不同的后端服务)
    balance_port = models.CharField(max_length=200, blank=True)
    #哪个环境的负载均衡？生产，预发？测试？（测试环境不部署负载均衡或者不需要切流量，就不配置）
    line = models.ManyToManyField(Line, blank=True)
    #（多机房，如果有2个机房，配置了2个负载均衡）
    idc = models.ForeignKey(Idc)
    def __unicode__(self):
        return u'%s:%s' % (self.app, self.balance)


# 审批表
class Approval(models.Model):
    # 需要创建approvalname=default的审批
    approvalname = models.CharField(max_length=50, blank=True)
    user = models.ManyToManyField(User, blank=True)

    def __unicode__(self):
        return u'%s' % self.user.all()





class ApprovalAdmin(admin.ModelAdmin):
    filter_horizontal = ('user',)

class AppsAdmin(admin.ModelAdmin):
    filter_horizontal = ('user','prdhost','prehost','testhost')


admin.site.register(Apps,AppsAdmin)
admin.site.register(Ostype)
admin.site.register(Idc)
admin.site.register(Host)
admin.site.register(Ports)
admin.site.register(Line)
admin.site.register(Apptype)
#Porttype 为固定值http  tomcat_shutdown  tcp
admin.site.register(Porttype)
admin.site.register(Balance)
admin.site.register(Funcevent)
admin.site.register(Funcexe)
admin.site.register(Balance_attr)
admin.site.register(Approval,ApprovalAdmin)
