from celery import shared_task
from django.utils import timezone
from habari.apps.crawl.models import NewsSource, Crawl
from habari.apps.crawl.crawlers import (smcrawler, tscrawler, dncrawler, dmcrawler,
 eacrawler, bdcrawler, ctcrawler)

@shared_task(name='frequent_crawlers')
def frequent_crawlers():
	crawlers ={
        'DN': dncrawler.DNCrawler,
        'SM': smcrawler.SMCrawler,
        'TS': tscrawler.TSCrawler,
        'DM': dmcrawler.DMCrawler
        }
	for key, value in crawlers.items():
		crawler = value()
		crawl = crawler.run()

@shared_task(name='non_frequent_crawlers')
def non_frequent_crawlers():
	crawlers = {
	'EA':eacrawler.EACrawler,
	'CT':ctcrawler.CTCrawler,
	}

	for key, value in crawlers.items():
		crawler = value()
		crawl = crawler.run()

@shared_task(name='bd_crawler')
def bd_crawler():
	bd = bdcrawler.BDCrawler
	crawler = bd()
	crawl = crawler.run()

@shared_task(name='retry_failed_crawls')
def retry_failed_crawls():
	'''
	Retry crawls that have an error status or stuck in a Crawing status
	'''
	crawler_classes = {
	'DN': dncrawler.DNCrawler,
    'SM': smcrawler.SMCrawler,
    'TS': tscrawler.TSCrawler,
    'DM': dmcrawler.DMCrawler,
    'EA': eacrawler.EACrawler,
	'CT': ctcrawler.CTCrawler,
	'BD': bdcrawler.BDCrawler
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

