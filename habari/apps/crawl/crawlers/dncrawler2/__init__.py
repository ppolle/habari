import logging
from habari.apps.crawl.crawlers import AbstractBaseCrawler

logger = logging.getLogger(__name__)

class DNCrawler(AbstractBaseCrawler):
	def __init__(self):
		super().__init__('DN')
		self.url = self.news_source.url
		self.categories = self.get_category_links()

	def partial_links_to_ignore(self, url):
		links = ('https://www.nation.co.ke/kenya/news',
			'https://www.nation.co.ke/kenya/business',
			'https://www.nation.co.ke/kenya/counties'
			)

		if url.startswith(links):
			return True
		else:
			return False

	def get_category_links(self):
		logger.info('Getting links to all categories and sub-categories')
		categories = [self.url, ]

	def update_top_stories(self):
		top_categories = self.cagetogies
		for cat in top_categories:
			print(cat)
