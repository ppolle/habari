from itertools import groupby
from django.shortcuts import render
from datetime import datetime
from habari.apps.crawl.models import Article, NewsSource

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
