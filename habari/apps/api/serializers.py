from rest_framework import serializers
from habari.apps.crawl.models import Article, NewsSource

class NewsSourceSerializer(serializers.ModelSerializer):
	class Meta:
		model = NewsSource
		fields = ('name',)
		read_only_fields = ('name')

class ArticleSerializer(serializers.ModelSerializer):
	news_source = NewsSourceSerializer(many=False)
	class Meta:
		model = Article
		fields = ('title', 'article_url', 'article_image_url', 'author', 'news_source', 'publication_date')
		read_only_fields = ('title', 'article_url', 'article_image_url', 'author', 'news_source', 'publication_date')
