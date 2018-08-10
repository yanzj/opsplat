
from django.conf.urls import url
import views


urlpatterns = [
    url(r'^newapp/', views.newapp),
    url(r'^confjks/', views.confjks),
    url(r'^maketar/', views.maketar),
    url(r'myproject/',views.myproject),
    url(r'jkshis/',views.jkshis),
]
