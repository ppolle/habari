from django.shortcuts import render
from habari.apps.crawl.models import Article, NewsSource

# Create your views here.

def index(request):
	sources = NewsSource.objects.all()
	return render(request, 'core/index.html', {'sources':sources})

def status(request):
	sources = NewsSource.objects.all().order_by('pk')
	return render(request, 'core/status.html', {'sources':sources})
