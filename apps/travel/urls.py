from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^main$', views.index),
    url(r'^travels$', views.success),
    url(r'^process$', views.process),
    url(r'^login$', views.login),
    url(r'^logout$', views.logout),
    url(r'^travels/add$', views.addtrip),
    url(r'^travels/addprocess$', views.addprocess),
    url(r'^travels/destination/(?P<dest_id>\d+)$', views.destination),
    url(r'^travels/join/(?P<dest_id>\d+)$', views.join),
]
