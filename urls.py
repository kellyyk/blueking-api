# -*- coding: utf-8 -*-
from django.conf.urls import url

from esb.views import APIView


urlpatterns = [
    url(r'^c/compapi/(?P<system_name>\w+)/(?P<component_name>\w+)/$', APIView.as_view()),
]
