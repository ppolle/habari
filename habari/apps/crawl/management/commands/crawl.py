from django.core.management.base import BaseCommand
from django.utils import timezone
from habari.apps.crawl.crawler import DNCrawler

class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):
    	crawler = DNCrawler()
    	crawl = crawler.update_top_stories()
    	# time = timezone.now().strftime('%X')
    	# self.stdout.write("It's now %s" % time)
    	# for c in crawl:
    	# 	print(c)
