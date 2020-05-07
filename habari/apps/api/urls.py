from django.conf.urls import url
from habari.apps.api.views import ArticleList

urlpatterns = [
	url(r'^news/$', ArticleList.as_view()),

]
