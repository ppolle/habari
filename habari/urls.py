"""habari URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Habari API",
        default_version='v1',
        description="An API that gives users access to Habari\'s news articles. The API currently only \
        avails news items over the past 24 hours, from various sources within East Africa.\
        The contries include Kenya, Uganda and Tanzania. There are currently 6 news sources from \
        which a user can retrieve news articles from, i.e, The Daily Nation, The Business Daily, The Star, The daily Monitor, The Daily Standard,\
        The Citizen and The East African",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="peter.m.polle@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    url(r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger',
                                           cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc',
                                         cache_timeout=0), name='schema-redoc'),

    url(r'^admin/', admin.site.urls),
    url(r'^api/v1/', include('habari.apps.api.urls')),
    url(r'', include('habari.apps.core.urls')),

]
