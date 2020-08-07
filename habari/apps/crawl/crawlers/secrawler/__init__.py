import re
import pytz
import logging
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from habari.apps.crawl.models import Article
from habari.apps.crawl.crawlers import AbstractBaseCrawler
from habari.apps.utils.error_utils import error_to_string, http_error_to_string

logger = logging.getLogger(__name__)

class SECrawler(AbstractBaseCrawler):
	def __init__(self):
		super().__init__('SE')
		self.url = self.news_source.url

	def get_category_links(self):
		'''
		Get and return links to all categories as shown on self.url
		'''
		logger.info('Getting links to all categories and sub-categories')
		categories = [self.url]

		try:
			get_categories = requests.get(self.url)
		except Exception as e:
			logger.exception(
                'Error: {0} , while getting categories from: {1}'.format(e, self.url))
			self.errors.append(error_to_string(e))
		else:
			if get_categories.status_code == 200:
				soup = BeautifulSoup(get_categories.content, 'lxml')
				all_categories = soup.select('.sidenav.sidenavMob a')

				for category in all_categories:
					if category.get('href') is not None:
						cat = self.make_relative_links_absolute(
        					category.get('href'))
						# print('Adding category: {}'.format(cat))
						if cat not in categories:
							categories.append(cat)
			else:
				logger.exception(
                        '{0} error while getting categories and sub-categories for {1}'.format(get_categories.status_code, self.url))
				self.errors.append(http_error_to_string(
                        get_categories.status_code, self.url))

		return categories

	def update_top_stories(self):
		links = self.get_category_links()

		for link in links:
			print(link)