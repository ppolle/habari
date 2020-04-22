from django.conf.urls import url
from habari.apps.core import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^status/$', views.status, name='status'),
    url(r'^(?P<source>\w+)/$', views.get_source, name='sources'),
    url(r'^(?P<source>\w+)/(?P<author>.+)/$', views.get_author_articles, name='author'),
    url(r'^(?P<source>\w+)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', views.day, name='day'),
]
