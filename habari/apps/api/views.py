# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from habari.apps.crawl.models import Article
from .serializers import ArticleSerializer
from django_filters import rest_framework as filters
from rest_framework import generics
from .filters import ArticleFilter

# Create your views here.
class ArticleList(generics.ListAPIView):
	"""
	Retrieve a list of news articles from different sources
	"""
	serializer_class = ArticleSerializer
	filterset_class = ArticleFilter

	def get_queryset(self):
		from datetime import datetime, timedelta

		time_threshold = datetime.today() - timedelta(days=1)
		results = Article.objects.filter(publication_date__gte=time_threshold)
		return results
