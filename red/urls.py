from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

import views

urlpatterns = patterns('', 
    url(r'^$', direct_to_template, {'template': 'index.html' }, name="red-index"),
    url(r'^upload$', views.upload, name="red-upload"),
    url(r'^matrix$', views.display_matrices, name="red-display-all-matrices"),
    url(r'^matrix/(\d+)$', views.display_matrix, name="red-display-matrix"),         
    url(r'^matrix/(\d+)/(\w+)$', views.display_matrix_functions, name="red-display-functions"),
    url(r'^matrix/(\d+)/(\w+)/fever$', views.run_fever_report, name="red-fever-report"),
    url(r'^matrix/(\d+)/(\w+)/fever/report\.txt$', views.run_text_report, name="red-text-report"),
    url(r'^matrix/(\d+)/(\w+)/fever/report\.xls$', views.run_xls_report, name="red-xls-report"),
)
