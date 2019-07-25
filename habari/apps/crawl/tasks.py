from celery import shared_task
from habari.apps.crawl import crawler

@shared_task
def dn_crawler():
	crawler = crawler.DNCrawler()
	crawl = crawler.update_top_stories()