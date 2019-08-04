# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from habari.apps.crawl.models import Article
from .serializers import ArticleSerializer
from rest_framework import generics

# Create your views here.
class ArticleList(generics.ListAPIView):
	"""
	Retrieve a list of news articles from different sources
	"""
	queryset = Article.objects.all()
	serializer_class = ArticleSerializer
