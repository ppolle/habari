from django.conf.urls import url
from habari.apps.core import views

urlpatterns = [
 	# Auth Urls
 	url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^register/$', views.register, name='register'),
    url(r'^status/$', views.status, name='status'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^(?P<source>\w+)/$', views.get_source, name='sources'),
    url(r'^(?P<source>\w+)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', views.day, name='day'),
    url(r'^(?P<source>\w+)/(?P<author>.+)/$', views.get_author_articles, name='author'),


]
