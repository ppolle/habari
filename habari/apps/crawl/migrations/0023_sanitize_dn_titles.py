# Generated by Django 2.2.12 on 2020-06-02 23:14

from django.db import migrations
from django.utils import timezone

def sanitize_dn_titles(apps, schema_editor):
	yesterday = timezone.now() - timezone.timedelta(days=3)
	Article = apps.get_model('crawl', 'Article')

	for article in Article.objects.filter(news_source__slug='DN',timestamp__gte=yesterday):
		title = article.title.strip("[\'\"]")
		article.title = title
		article.save()

class Migration(migrations.Migration):

    dependencies = [
        ('crawl', '0022_auto_20200415_2016'),
    ]

    operations = [
    migrations.RunPython(sanitize_dn_titles),
    ]
