from django.shortcuts import render
from habari.apps.crawl.models import Article, NewsSource

# Create your views here.

def index(request):
	articles = Article.objects.all()
	return render(request, 'core/index.html', {'articles':articles})

def status(request):
	sources = NewsSource.objects.all()
	return render(request, 'core/status.html', {'sources':sources})
