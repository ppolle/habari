from django.conf.urls import url
from habari.apps.core import views

urlpatterns = [
    url(r'', views.index, name='index'),
]
