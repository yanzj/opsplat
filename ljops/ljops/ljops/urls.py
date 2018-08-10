"""ljops URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""


from django.conf.urls import url,include
from django.contrib import admin
from ljops.views import index,login,logout,showloading,test

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^home/$', index, name='index'),
    url(r'^$', index, name='index'),
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^showloading/$', showloading, name='showloading'),
    url(r'^ljapps/', include('ljapps.urls')),
    url(r'^workorder/', include('workorder.urls')),
    url(r'^ops/api/', include('ops.urls')),
    url(r'updatemanage/',include('updatemanage.urls')),
    url(r'^test/',test,name='test'),
]
