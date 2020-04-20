from celery import shared_task
from habari.apps.crawl.crawlers import (smcrawler, tscrawler, dncrawler, dmcrawler,
 eacrawler, bdcrawler, ctcrawler)

@shared_task(name='frequent_crawlers')
def frequent_crawlers():
	crawlers ={
        'DN': dncrawler.DNCrawler,
        'SM': smcrawler.SMCrawler,
        'TS': tscrawler.TSCrawler,
        'DM':dmcrawler.DMCrawer
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
