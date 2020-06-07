from django.contrib import admin
from .models import Article, NewsSource, Crawl
# Register your models here.
admin.site.register(Article)
admin.site.register(NewsSource)
admin.site.register(Crawl)
