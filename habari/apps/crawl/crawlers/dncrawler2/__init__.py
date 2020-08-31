import pytz
import logging
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from habari.apps.crawl.models import Article
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
				main_categories = soup.select('footer ul.categories-nav_categories a')

				for cat in main_categories:
					if cat.get('href') is not None:
						link = self.make_relative_links_absolute(cat.get('href'))
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
					stories = soup.select('a.teaser-image-large') + soup.select('a.article-collection-teaser')
					for story in stories:
						story = self.make_relative_links_absolute(story.get('href'))
						if not Article.objects.filter(article_url=story).exists() and \
						story not in story_links and self.check_for_top_level_domain(story):
							story_links.append(story)
			except Exception as e:
				logger.exception(
                    '{0} error while getting top stories for {1}'.format(e, category))
				self.errors.append(error_to_string(e))

		return story_links

	def get_story_details(self, link):
		story = requests.get(link)

		if story.status_code == 200:
			soup = BeautifulSoup(story.content, 'html.parser')

			title = soup.select_one('h1.title-medium').get_text().strip()
			publication_date = soup.select_one('time.date').get('datetime')
			date = pytz.timezone("Africa/Nairobi").localize(datetime.strptime(publication_date, '%Y-%m-%dT%H:%M:%SZ'), is_dst=None)
			author_list = soup.select('.article-authors_texts .article-authors_authors')
			authors = self.sanitize_author_iterable(author_list)
			try:
				summary = soup.select_one('.article-content_summary .text-block').get_text().strip()
			except AttributeError:
				summary = soup.find("meta",  property="og:description").get('content').strip()
			try:
				image_url = self.make_relative_links_absolute(\
				soup.select_one('figure.article-picture img').get('data-src'))
			except AttributeError:
				try:
					image_url = soup.select_one('figure iframe.lazy-iframe_iframe').get('data-src')
				except AttributeError:
					image_url = soup.select_one('figure iframe').get('src')

		return {'article_url':link,
				'article_title':title,
				'publication_date':date,
				'author':authors,
				'summary':summary,
				'image_url':image_url}

	def update_top_stories(self):
		articles = self.get_top_stories()
		article_info = []
		for article in articles:
			try:
				logger.info('Updating story content for ' + article)
				story = self.get_story_details(article)
				article_info.append(Article(title=story['article_title'],
                                            article_url=story['article_url'],
                                            article_image_url=story['image_url'],
                                            author=story['author'],
                                            publication_date=story['publication_date'],
                                            summary=story['summary'],
                                            news_source=self.news_source
                                            ))

			except Exception as e:
				logger.exception('Crawling Error: {0} while getting data from: {1}'.format(e, article))
				self.errors.append(error_to_string(e))
		try:
			Article.objects.bulk_create(article_info)
			logger.info('')
			logger.info('Succesfully updated Daily Nation Latest Articles.{} new articles added'.format(
                len(article_info)))
			self.crawl.total_articles=len(article_info)
			self.crawl.save()
		except Exception as e:
			logger.exception('Error!!!{}'.format(e))
			self.errors.append(error_to_string(e))
