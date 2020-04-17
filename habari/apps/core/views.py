from itertools import groupby
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404
from habari.apps.crawl.models import Article, NewsSource
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

def index(request):
	today = datetime.today()
	sources = NewsSource.objects.order_by('pk')
	return render(request, 'core/index.html', {'sources':sources})

def status(request):
	sources = NewsSource.objects.all().order_by('pk')
	return render(request, 'core/status.html', {'sources':sources})

def get_source(request, source):
	source = source.upper()
	news_source = get_object_or_404(NewsSource,slug__iexact=source)
	last_week = datetime.today() - timedelta(days=7)
	article_list = Article.objects.filter(publication_date__gte=last_week,news_source=news_source).order_by('-publication_date', '-timestamp')
	
	paginator = Paginator(article_list, 50)
	page = request.GET.get('page')
	try:
		articles = paginator.page(page)
	except PageNotAnInteger:
		articles = paginator.page(1)
	except EmptyPage:
		articles = paginator.page(paginator.num_pages)
	return render(request, 'core/news_source.html', {'articles':articles,'source':news_source})

def get_author_articles(request, source, author):
	'''
	Get articles belonging to a particular author
	'''
	import re
	author_string = re.sub(r'-',' ',author).upper()  
	news_source = get_object_or_404(NewsSource, slug__iexact=source)
	article_list = Article.objects.filter(news_source=news_source, author__contains=[author_string])

	paginator = Paginator(article_list, 50)
	page = request.GET.get('page')
	try:
		articles = paginator.page(page)
	except PageNotAnInteger:
		articles = paginator.page(1)
	except EmptyPage:
		articles = paginator.page(paginator.num_pages)

	return render(request, 'core/author_articles.html', {'articles':articles, 'source':news_source, 'author':author_string})
