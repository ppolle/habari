from django.core.management.base import BaseCommand
from django.utils import timezone
from habari.apps.crawl import crawler


class Command(BaseCommand):
    help = 'Crawl News Sources for New Articles'

    def add_arguments(self, parser):
        parser.add_argument('sources', type=str,
                            help='Indicated the news sources to be crawled')

    def handle(self, *args, **kwargs):
        source = kwargs['sources']
        if source  == 'SM':
            sm_crawler = crawler.SMCrawler()
            crawl = sm_crawler.update_top_stories()
            self.stdout.write(self.style.SUCCESS('Succesfully updates the Citizen Latest Articles'))
            
        if source == 'CT':
            ct_crawler = crawler.CTCrawler()
            crawl = ct_crawler.update_top_stories()
            self.stdout.write(self.style.SUCCESS(
                'Succesfully updated The Citizen Latest Articles.'))
        
        if source == 'EA':
            ea_crawler = crawler.EACrawler()
            crawl = ea_crawler.update_top_stories()
            self.stdout.write(self.style.SUCCESS(
                'Succesfully updated The East African Latest Articles.'))

        if source == 'BD':
            bd_crawler = crawler.BDCrawler()
            crawl = bd_crawler.update_top_stories()
            self.stdout.write(self.style.SUCCESS(
                'Succesfully updated Business Daily Latest Articles'))

        if source == 'DN':
            dn_crawler = crawler.DNCrawler()
            crawl = dn_crawler.update_top_stories()
            self.stdout.write(self.style.SUCCESS(
                'Succesfully updated Daily Nation Latest Articles.'))

        if source == 'all':
            dn_crawler = crawler.DNCrawler()
            bd_crawler = crawler.BDCrawler()

            dn_crawl = dn_crawler.update_top_stories()
            bd_crawl = bd_crawler.update_top_stories()

            self.stdout.write(self.style.SUCCESS(
                'Succesfully updated Latest Articles'))
