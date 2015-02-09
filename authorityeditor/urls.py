__author__ = 'jblowe'

from django.conf.urls import patterns, url
from authorityeditor import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^change$', views.change, name='change'),
                       )
