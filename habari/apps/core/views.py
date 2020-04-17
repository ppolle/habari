from itertools import groupby
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404
from habari.apps.crawl.models import Article, NewsSource
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

def index(request):
	today = datetime.today()
	sources = NewsSource.objects.all()
	articles = Article.objects.filter(publication_date=today).order_by('-publication_date')
	grpd_articles = groupby(articles, key=lambda x:x.news_source)
	num1 = 0
	a_list = [("Animal", "cat"),  
          ("Animal", "dog"),  
          ("Bird", "peacock"),  
          ("Bird", "pigeon"),
          ("Animal", "mouse")] 
	for key, group in groupby(a_list, key=lambda x:x[0]):
		print(key + " :", list(group)) 
		# grpd_articles[key] = group
		# for item, grp in grpd_articles.items():
		# 	print(item, grp)

			# for x in grp:
			# 	print(x)
		# num1 += 1
		# print('('+str(num1)+')'+'. '+key.name)
		# num = 0
		# for item in group:
		# 	num += 1
		# 	print(str(num) +'. '+item.title)
	return render(request, 'core/index.html', {'sources':sources,'articles':grpd_articles})

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
	news_source = get_object_or_404(NewsSource, slug__iexact=source)
	article_list = Article.objects.filter(news_source=news_source, author__contains=[author])

	paginator = Paginator(article_list, 50)
	page = request.GET.get('page')
	try:
		articles = paginator.page(page)
	except PageNotAnInteger:
		articles = paginator.page(1)
	except EmptyPage:
		articles = paginator.page(paginator.num_pages)

	return render(request, 'core/author_articles.html', {'articles':articles, 'source':source, 'author':author})
