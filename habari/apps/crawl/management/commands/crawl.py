from django.core.management.base import BaseCommand
from django.utils import timezone

from habari.apps.crawl.crawlers import (dncrawler2, eacrawler, bdcrawler, ctcrawler, dmcrawler,
    smcrawler, tscrawler, secrawler, dmcrawler2)

class Command(BaseCommand):
    help = 'Crawl News Sources for New Articles'

    def get_crawler_class(self, slug):
        crawler_classes = {
        'DN': dncrawler2.DNCrawler,
        'BD': bdcrawler.BDCrawler,
        'EA': eacrawler.EACrawler,
        'CT': ctcrawler.CTCrawler,
        'SM': smcrawler.SMCrawler,
        'DM': dmcrawler2.DMCrawler,
        'TS': tscrawler.TSCrawler,
        'SE': secrawler.SECrawler
        }

        return crawler_classes.get(slug)

    def add_arguments(self, parser):
        parser.add_argument('sources', nargs='+', type=str,
                            help='Indicated the news sources to be crawled')

    def handle(self, *args, **kwargs):
        sources = kwargs['sources']

        for source in sources:
            capitalized_source = source.upper()
            crawler_class = self.get_crawler_class(capitalized_source)
            if crawler_class is not None:
                crawler = crawler_class()
                crawl = crawler.run()
                self.stdout.write(self.style.SUCCESS('Succesfully updated {} Latest Articles'.format(type(crawler).__name__)))
            else:
                self.stdout.write(self.style.WARNING('Crawler with slug {} not found'.format(source)))
