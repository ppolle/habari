from rest_framework import serializers
from habari.apps.crawl.models import Article

class ArticleSerializer(serializers.ModelSerializer):
	class Meta:
		model = Article
		fields = ('title', 'article_url', 'article_image_url', 'author', 'news_source', 'publication_date')
		read_only_fields = ('title', 'article_url', 'article_image_url', 'author', 'news_source', 'publication_date')