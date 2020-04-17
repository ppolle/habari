from django.db import models
from autoslug import AutoSlugField
from djchoices import ChoiceItem, DjangoChoices
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class Article(models.Model):
	'''Model that saves crawled articles'''
	title = models.CharField(max_length=500)
	article_url = models.URLField(max_length=500, unique=True)
	article_image_url = models.URLField(max_length=500)
	author = ArrayField(models.CharField(max_length=500), blank=True, null=True)
	publication_date = models.DateField()
	summary = models.CharField(max_length=3000)
	news_source = models.ForeignKey('NewsSource', null=True, on_delete=models.SET_NULL)
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

	def front_page_filtered_Set(self):
		from datetime import datetime
		today = datetime.today()
		return Article.objects.filter(news_source=self).order_by('-publication_date','-timestamp')[:10]

class Crawl(models.Model):
	'''Model to save details of a crawl run'''
	class StatusType(DjangoChoices):
		Crawling = ChoiceItem('crawling','Crawling')
		Error = ChoiceItem('error','Error')
		Good = ChoiceItem('good','Good')
		Start = ChoiceItem('start', 'Start')

	news_source = models.ForeignKey('NewsSource', null=True, on_delete=models.SET_NULL)
	status = models.CharField(max_length=30, choices=StatusType.choices, default=StatusType.Start)
	total_articles = models.IntegerField(null=True, blank=True, default=0)
	crawl_error = models.TextField(null=True, blank=True)
	crawl_time = models.DateTimeField(auto_now_add=True)

