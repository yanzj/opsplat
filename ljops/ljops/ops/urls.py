
from django.conf.urls import url
import views


urlpatterns = [
    url(r'^add_appv/', views.add_appv),
    url(r'^app_versiontype/', views.app_versiontype),
    url(r'^checkres/',  views.checkres),
    url(r'^consoleout/',  views.consoleout),
    url(r'^addappversion/',  views.addappversion),
    url(r'^deploy/',  views.deploy),
    url(r'^getdepres/',  views.getdepres),
    url(r'^done/',  views.done),
    url(r'^rollback/',  views.rollback),
    url(r'^getexelog/', views.getexelog),
    url(r'^showproject/',  views.showproject),
]
