# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from habari.apps.crawl.models import Article
from .serializers import ArticleSerializer
from django_filters import rest_framework as filters
from rest_framework import generics
from .filters import ArticleFilter
from django.utils import timezone

# Create your views here.
class ArticleList(generics.ListAPIView):
	"""
	Retrieve a list of news articles from different sources
	"""
	serializer_class = ArticleSerializer
	filterset_class = ArticleFilter

	def get_queryset(self):
		last_day = timezone.localtime(timezone.now() - timezone.timedelta(days=1))
		return Article.objects.filter(publication_date__gte=last_day)
