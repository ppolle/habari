import requests
from bs4 import BeautifulSoup


class DNCrawler:
	def __init__(self):
		self.url = 'https://www.nation.co.ke/'

	def get_top_stories(self):
		print('Getting top stories')
		top_stories = requests.get(self.url)
		story_links = []
		if top_stories.status_code == 200:
			soup = soup = BeautifulSoup(top_stories.content, 'html.parser')
			teaser = soup.select('.small-story-list a')
			teaser =  teaser + soup.select('.story-teaser a')
			for t in teaser:
				t =  self.make_relative_links_absolute(t.get('href'))
				if t not in story_links:
					story_links.append(t)
		return story_links

	def make_relative_links_absolute(self, link):
		print('Sanitizing '+ str(link))
		import re
		try:
			from urlparse import urljoin
		except ImportError:
			from urllib.parse import urljoin

		if not link.startswith(self.url):
			link = urljoin(self.url, link)

		return link

	def get_story_details(self, link):
		from datetime import datetime
		story= requests.get(link)
		if story.status_code == 200:
			soup = BeautifulSoup(story.content, 'html.parser')
			url = link
			image_url = self.make_relative_links_absolute(soup.select('.story-view header img')[0].get('src'))
			title = [t.get_text() for t in soup.select('.story-view header h2')][0]
			publication_date = [p.get_text() for p in soup.select('.story-view header h6')][0]
			date = datetime.strptime(publication_date, '%A %B %d %Y')
			author = [a.get_text() for a in soup.select('.story-view .author strong')][0]
		else:
			print('Getting stuff failed')

		return {'article_url':url,
    			'image_url':image_url,
    			'article_title':title,
    			'publication_date':date,
    			'author':author}

	def update_top_stories(self):
		from habari.apps.crawl.models import Article
		top_articles = self.get_top_stories()
		article_info = []
		for article in top_articles:
			try:
				print('Updating story content for ' + article)
				story = self.get_story_details(article)
				if not Article.objects.filter(article_url=article).exists():
					article_info.append(Article(title=story['article_title'],
						article_url=story['article_url'],
						article_image_url=story['image_url'],
						author=story['author'],
						publication_date=story['publication_date'],
						summary='blah blah blah',
						news_source='DN'
						))

			except Exception as e:
				print('{0} error while getting {1}'.format(e, article))
		try:
			Article.objects.bulk_create(article_info)
			print('Succesfully updated Daily Nation Latest Articles')
		except Exception as e:
			print('Error!!!{}'.format(e))

		return article_info