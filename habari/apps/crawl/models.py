from autoslug import AutoSlugField
from django.db import models

# Create your models here.
class Article(models.Model):
	'''Model that saves crawled articles'''
	NEWS_SOURCE_CHOICES = (
			('DN', 'THE DAILY NATION'),
			('BD', 'THE BUSINESS DAILY'),
			('EA', 'THE EAST AFRICAN'),
			('CT', 'THE CITIZEN'),
			('SM', 'THE DAILY STANDARD'),
			('DM', 'THE DAILY MONITOR'),
			('TS', 'THE STAR KENYA')
		)

	title = models.CharField(max_length=500)
	article_url = models.URLField(max_length=500, unique=True)
	article_image_url = models.URLField(max_length=500)
	author = models.CharField(max_length=500)
	publication_date = models.DateField()
	summary = models.CharField(max_length=3000)
	news_source = models.CharField(max_length=100, choices=NEWS_SOURCE_CHOICES)
	source = models.ForeignKey('NewsSource', null=True, on_delete=models.SET_NULL)
	slug = AutoSlugField(blank=False, populate_from='title')
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.title

	class Meta:
		ordering = ['-publication_date']

class NewsSource(models.Model):
	'''Model that saves details about a news source'''
	name = models.CharField(max_length=300)
	slug = models.CharField(max_length=5)
	url = models.URLField()

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']
