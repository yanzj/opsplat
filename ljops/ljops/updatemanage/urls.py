
from django.conf.urls import url
import views


urlpatterns = [
    url(r'^update/', views.update),
    url(r'^callbak/', views.callbak),
    url(r'^doupdate/', views.doupdate),
    url(r'^docallbak/', views.docallbak),
    url(r'^uphistory/', views.uphistory),
    url(r'^process/', views.process),
]
