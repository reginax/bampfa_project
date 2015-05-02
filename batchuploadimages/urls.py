__author__ = 'jblowe'
from django.conf.urls import patterns, include, url

# Function based API views
from batchuploadimages.views import image_list, image_detail
#from batchuploadimages.views import ImageView

urlpatterns = patterns('',

                       # Regular URLs  # url(r'^images/$', image_list, name='image_list'),
                       # url(r'^images/(?P<pk>[0-9]+)$', image_detail, name='image_detail'),

                       # Class based URLs,
                       url(r'^images/$', image_list, name='image_list'),
                       url(r'^images/(?P<pk>[0-9]+)$', image_detail, name='image_detail'),
                       #url(r'^images/(?P<pk>[0-9]+)$', ImageView, name='image_detail'),
)