from autoslug import AutoSlugField
from django.db import models

# Create your models here.
class Article(models.Model):
	'''Model that saves crawled articles'''
	NEWS_SOURCE_CHOICES = (
			('DN', 'DAILY NATION'),
			('BD', 'BUSINESS DAILY'),
		)

	title = models.CharField(max_length=500)
	article_url = models.URLField(max_length=500, unique=True)
	article_image_url = models.URLField(max_length=500)
	author = models.CharField(max_length=500)
	publication_date = models.DateField()
	summary = models.CharField(max_length=3000)
	news_source = models.CharField(max_length=100, choices=NEWS_SOURCE_CHOICES)
	slug = AutoSlugField(blank=False, populate_from='title', unique=True)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.title

	class Meta:
		ordering = ['-publication_date']