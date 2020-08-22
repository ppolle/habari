import logging
import requests
from bs4 import BeautifulSoup
from habari.apps.crawl.crawlers import AbstractBaseCrawler
from habari.apps.utils.error_utils import error_to_string, http_error_to_string

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

		try:
			get_categories = requests.get(self.url)
		except Exception as e:
			logger.exception('Error: {0} while getting categories from {1}'.format(e,self.url))
			self.errors.append(error_to_string(e))
		else:
			if get_categories.status_code == 200:
				soup = BeautifulSoup(get_categories.content, 'html.parser')
				main_categories = soup.select('.menu-vertical a')

				for cat in main_categories:
					if cat.get('href') is not None:
						link = self.make_relative_links_absolute(cat.get('href'))
						if not self.partial_links_to_ignore(link):
							categories.append(link)

		return categories

	def get_top_stories(self):
		logger.info('Getting the latest stories')
		story_links = []
		for category in self.categories:
			try:
				top_stories = requests.get(category)
				if top_stories.status_code == 200:
					soup = BeautifulSoup(top_stories.content, 'html.parser')
					stories = soup.select('a article')
					for story in stories:
						story_links.append(story)
			except Exception as e:
				logger.exception(
                    '{0} error while getting top stories for {1}'.format(e, stories))
				self.errors.append(error_to_string(e))

		return story_links

	def update_top_stories(self):
		top_categories = self.get_top_stories()
		for cat in top_categories:
			print('-'*50)
			print(cat)
