from django.conf.urls.defaults import *

import views

urlpatterns = patterns('', 
    url(r'^$', views.index, name="red-index"),
    url(r'^upload/$', views.upload, name="red-upload"),
    url(r'^matrix/$', views.display_matrices, name="red-display-all-matrices"),
    url(r'^matrix/(\d+)/$', views.display_matrix, name="red-display-matrix"),         
)
