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

@shared_task(name='sanitize_sm_author_lists_with_empty_strings')
def sanitize_sm_author_lists_with_empty_strings():
	'''
	Correct Standard Media author lists that crawl for lists with a empty strings. This causes author url errors on standard media pages
	'''
	source = NewsSource.objects.get(slug='SM')
	articles = Articles.objects.filter(news_source=source, author__contains=[''])
	for article in articles:
		request = requests.get(article.article_url)
		if request.status_code == 200:
            soup = BeautifulSoup(request.content, 'lxml')
            try:
                author = [a.strip().upper() for a in soup.select_one('.article-meta a').get_text().split(' and ') if a is not '']
            except AttributeError:
            	author = [a.strip().upper() for a in soup.select('div .io-hidden-author').get_text()]
            except AttributeError:
            	author = [a.strip().upper() for a in soup.select_one('.small.text-muted.mb-3 a').get_text().lower().split(' and ')]
            except AttributeError:
                        author = []
        if author == [''] or author == [':']:
            author = []
        article.author = author
        article.save()
