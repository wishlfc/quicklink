# from django.urls import path
from django.conf.urls import url

from . import views

from view_gencase import gencase_url


urlpatterns = [
    url('', views.gencase, name='gencase'),
    url('', views.btsmgmt, name='btsmgmt'),
    url('', views.prdescription, name='prdescription'),
]
