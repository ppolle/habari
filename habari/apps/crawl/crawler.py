import requests
from bs4 import BeautifulSoup


class DNCrawler:
	def __init__(self):
		self.url = 'https://www.nation.co.ke/'

	def get_top_stories(self):
		top_stories = requests.get(self.url)
		story_links = []
		if top_stories.status_code == 200:
			soup = soup = BeautifulSoup(top_stories.content, 'html.parser')
			teaser = soup.select('.story-teaser a')
			for t in teaser:
				while t not in story_links:
					story_links.append(
					    {'url': self.make_relative_links_absolute(t.get('href'))})

				print(self.make_relative_links_absolute(t.get('href')))
		return story_links
			# print(teaser)
			# print(soup.prettify())

	def make_relative_links_absolute(self, link):
		import re
        try:
            from urlparse import urljoin
        except ImportError:
            from urllib.parse import urljoin

        if not link.starts_with(self.url):
			link = urljoin(self.url, link)
        
        return link

    def get_story_details(self, link):
    	story= request.get(link)
    	if story.status_code == 200:
    		soup = BeautifulSoup(story.content, 'html.parser')
    		url = link
    		image_url = soup.select('.story-view header img')
    		title = soup.select('.story-view header h2').get_text()
    		publication_date = soup.select('.story-view header h6').get_text()
    		author = soup.select('.story-view .author strong').get_text()
    		return {'article_url':url,
    				'article_url':image_url,
    				'article_title':title,
    				'publication_date':publication_date,
    				'author':author}

    def update_top_stories(self):
    	top_articles = self.get_top_stories()
    	article_info = []
    	for article in top_articles:
    		article_info.append(article)

    	return article_info



crawler = DNCrawler()
crawl = print(crawler.get_story_details('https://www.nation.co.ke/news/PSC-to-hire-gardeners-cooks-for-Kibaki-and-Moi/1056-5201290-p2wuou/index.html'))
