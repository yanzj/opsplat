
from django.conf.urls import url
import views


urlpatterns = [
    url(r'^newapp/', views.newapp),
    url(r'^update/', views.update),
]
