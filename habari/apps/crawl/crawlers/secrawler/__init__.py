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
		self.categories = self.get_category_links()

	def partial_links_to_ignore(self, url):
		links = ('https://www.standardmedia.co.ke/entertainment/video',
			'https://www.standardmedia.co.ke/entertainment/author',
			'https://www.standardmedia.co.ke/entertainment/gallery')

		if url.startswith(links):
			return False
		else:
			return True

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
					if (category.get('href') is not None):
						cat = self.make_relative_links_absolute(
        					category.get('href'))

						if cat not in categories and self.check_for_top_level_domain(cat) and \
						self.partial_links_to_ignore(cat):
							categories.append(cat)
			else:
				logger.exception(
                        '{0} error while getting categories and sub-categories for {1}'.format(get_categories.status_code, self.url))
				self.errors.append(http_error_to_string(
                        get_categories.status_code, self.url))

		return categories

	def get_top_stories(self):
		logger.info('Getting top stories')
		story_links = []

		for category in self.categories:
			try:
				stories = requests.get(category)
				if stories.status_code == 200:
					soup = BeautifulSoup(stories.content, 'lxml')

					right_side_bar = soup.select('.media-body a')
					main_bar = soup.select('.body-text-formart-two a')
					top_stories = soup.select('.gradient-cover a')
					card_stories = soup.select('.body-text-formart a')

					articles = right_side_bar+main_bar+top_stories+card_stories

					for article in articles:
						if article.get('href') is not None:
							article_link = self.make_relative_links_absolute(article.get('href'))
							if article_link not in story_links and self.check_for_top_level_domain(article_link) and not \
							Article.objects.filter(article_url=article_link).exists() and self.partial_links_to_ignore(article_link):
								story_links.append(article_link)

			except Exception as e:
				logger.exception(
                    'Crawl Error: {0} ,while getting top stories for: {1}'.format(e, category))
				self.errors.append(error_to_string(e))

		return story_links

	def update_top_stories(self):
		links = self.get_top_stories()
		
		total_links = len(links)

		for link in links:
			print(link)

		print('All links amount to: {}'.format(total_links))