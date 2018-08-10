#coding:utf-8
from django.contrib.auth.models import User
from django.contrib.auth import authenticate as authenticate_old
from smtplib import SMTP_SSL
from ljops.settings import mail_host,mail_profix

class mymailBackend:
    def authenticate(self,username=None,password=None):
        if len(password) == 0:
            return None
        try:
            smtp = SMTP_SSL(mail_host, 465)
            res = smtp.login(username+mail_profix,password)
            if  res[0]==235:
                return self.get_or_create_user(username,password)
            else:    
                return authenticate_old(username=username,password=password)
        except:
            return authenticate_old(username=username,password=password)

    def get_or_create_user(self, username,password):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            mail = username + mail_profix
            user = User(username=username,email=mail)
            user.is_staff = True
            user.is_superuser = False
            user.set_password('passwd set by mail!#..')
            user.save()
        return user
