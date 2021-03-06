import re
from celery import shared_task
from django.utils import timezone
from habari.apps.crawl.models import NewsSource, Crawl, Article
from habari.apps.crawl.crawlers import (smcrawler, tscrawler, dncrawler2, dmcrawler,
 eacrawler, bdcrawler, ctcrawler, secrawler)

@shared_task(autoretry_for=(Exception,))
def frequent_crawlers():
	crawlers ={
        'DN': dncrawler2.DNCrawler,
        'SM': smcrawler.SMCrawler,
        'TS': tscrawler.TSCrawler,
        'DM': dmcrawler.DMCrawler
        }
	for key, value in crawlers.items():
		crawler = value()
		crawl = crawler.run()

@shared_task(autoretry_for=(Exception,))
def non_frequent_crawlers():
	crawlers = {
	'EA':eacrawler.EACrawler,
	'CT':ctcrawler.CTCrawler,
	'SE':secrawler.SECrawler
	}

	for key, value in crawlers.items():
		crawler = value()
		crawl = crawler.run()

@shared_task(autoretry_for=(Exception,))
def bd_crawler():
	bd = bdcrawler.BDCrawler
	crawler = bd()
	crawl = crawler.run()

@shared_task(autoretry_for=(Exception,))
def retry_failed_crawls():
	'''
	Retry crawls that have an error status or stuck in a Crawing status
	'''
	crawler_classes = {
	'DN': dncrawler2.DNCrawler,
    'SM': smcrawler.SMCrawler,
    'TS': tscrawler.TSCrawler,
    'DM': dmcrawler.DMCrawler,
    'EA': eacrawler.EACrawler,
	'CT': ctcrawler.CTCrawler,
	'BD': bdcrawler.BDCrawler,
	'SE': secrawler.SECrawler
	}
	a_while_ago = timezone.now() - timezone.timedelta(minutes=45)

	sources = NewsSource.objects.all()
	for source in sources:
		if source.crawl_set.last().status == Crawl.StatusType.Error:
			crawl_class = crawler_classes.get(source.slug)
			crawl = crawl_class().run()

		if source.crawl_set.last().status != Crawl.StatusType.Good and source.crawl_set.last().crawl_time <= a_while_ago:
			crawl_class = crawler_classes.get(source.slug)
			crawl = crawl_class().run()

@shared_task(autoretry_for=(Exception,))
def sanitize_author_lists_with_empty_strings():
	'''
	Correct Standard Media author lists that crawl for lists with a empty strings. This causes author url errors on standard media pages
	'''
	crawler_classes = {
	'DN': dncrawler2.DNCrawler,
    'SM': smcrawler.SMCrawler,
    'TS': tscrawler.TSCrawler,
    'DM': dmcrawler.DMCrawler,
    'EA': eacrawler.EACrawler,
	'CT': ctcrawler.CTCrawler,
	'BD': bdcrawler.BDCrawler,
	'SE': secrawler.SECrawler
	}
	non_dictionary_classes = ['DN','TS','BD','SE']

	articles = Article.objects.filter(author__contains=[''])
	for article in articles:
		slug = article.news_source.slug
		article_url = {'article_url':article.article_url}
		crawler_class = crawler_classes.get(slug)
		
		if slug in non_dictionary_classes:
			update_details = crawler_class().update_article_details(article_url['article_url'])
		else:
			update_details = crawler_class().update_article_details(article_url)
		
		article.author = update_details['author']
		article.save()
