from autoslug import AutoSlugField
from django.db import models

# Create your models here.
class Article(models.Model):
	'''Model that saves crawled articles'''
	title = models.CharField(max_length=500)
	article_url = models.URLField(max_length=500)
	article_image_url = models.URLField(max_length=500)
	summary = models.CharField(max_length=3000)
	slug = AutoSlugField(blank=False, populate_from='title', unique=True)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.title