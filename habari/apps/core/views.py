from django.shortcuts import render
from habari.apps.crawl.models import Article

# Create your views here.

def index(request):
	articles = Article.objects.all()
	return render(request, 'core/index.html', {'articles':articles})
