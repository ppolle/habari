import logging
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from habari.apps.crawl.models import Article
from habari.apps.crawl.crawlers import AbstractBaseCrawler
from habari.apps.utils.error_utils import error_to_string

logger = logging.getLogger(__name__)

class DMCrawler(AbstractBaseCrawler):
    def __init__(self):
        super().__init__('DM')
        self.url = self.news_source.url

    def get_rss_feed_links(self):
        logger.info('Getting RSS feeds links')
        categories = [self.url, ]
        rss_feeds = []

        try:
            get_categories = requests.get(self.url)
        except Exception as e:
            logger.exception('Error!! {}while getting rss feeds'.format(e))
            self.errors.append(error_to_string(e))
        else:
            if get_categories.status_code == 200:
                soup = BeautifulSoup(get_categories.content, 'html.parser')
                all_categories = soup.select('.menu-vertical a')

                for category in all_categories:
                    if category.get('href') is not None:
                        category = self.make_relative_links_absolute(
                            category.get('href'))
                        categories.append(category)
            else:
                logger.exception(
                    '{0} error while getting rss links from: {1}'.format(get_categories.status_code, self.url))
                self.errors.append(http_error_to_string(get_categories.status_code,self.url))

        for category in categories:
            try:
                request = requests.get(category)
            except Exception as e:
                logger.exception('Error: {0} while getting RSS from {1}'.format(e,category))
                self.errors.append(error_to_string(e))
            else:
                if request.status_code == 200:
                    soup = BeautifulSoup(request.content, 'html.parser')
                    social_links = soup.select('.social-networks a')
                    for social_link in social_links:
                        link = social_link.get('href')
                        if link.endswith('.xml') and link is not None:
                            rss_feeds.append(
                                self.make_relative_links_absolute(link))
                else:
                    logger.exception(
                    '{0} error while getting rss links from: {1}'.format(request.status_code, category))
                    self.errors.append(http_error_to_string(request.status_code,category))

        return rss_feeds

    def get_top_stories(self):
        rss_feeds = self.get_rss_feed_links()
        stories = []
        for rss in rss_feeds:
            try:
                logger.info('Getting top stories from {}'.format(rss))
                request = requests.get(rss)
                if request.status_code == 200:
                    soup = BeautifulSoup(request.content, 'xml')
                    articles = soup.find_all('item')

                    for article in articles:
                        title = article.title.get_text().strip()
                        summary = article.description.get_text().strip()[:3000]
                        link = article.link.get_text().strip()
                        date = article.date.get_text().strip()
                        publication_date = datetime.strptime(
                            date, '%Y-%m-%dT%H:%M:%SZ')

                        article_details = {
                            'title': title,
                            'article_url': link,
                            'publication_date': publication_date,
                            'summary': summary, }

                        if article_details not in stories and not Article.objects.filter(article_url=article_details['article_url']).exists():
                            stories.append(article_details)
                else:
                    logger.exception(
                    '{0} error while getting rss details from: {1}'.format(get_categories.status_code, rss))
                    self.errors.append(http_error_to_string(get_categories.status_code,rss))

            except Exception as e:
                logger.exception(
                    'Error:{0} while getting stories from {1}'.format(e, rss))
                self.errors.append(error_to_string(e))
        return {story['article_url']:story for story in stories}.values()

    def update_article_details(self, article):
        request = requests.get(article['article_url'])

        if request.status_code == 200:
            soup = BeautifulSoup(request.content, 'lxml')
            try:
                image_url = self.make_relative_links_absolute(
                    soup.select_one('.story-view header img').get('src'))
            except AttributeError:
                try:
                    image_url = soup.select_one(
                        '.videoContainer iframe').get('src')
                except:
                    image_url = 'None'

            try:
                author = [self.sanitize_author_string(
                    a.get_text()) for a in soup.select('.story-view .author')]
            except AttributeError:
                author = []

            article['article_image_url'] = image_url
            article['author'] = author

        return article

    def update_top_stories(self):
        articles = self.get_top_stories()
        article_info = []
        for article in articles:
            try:
                logger.info('Updating article details for: {}'.format(
                    article['article_url']))
                self.update_article_details(article)
                article_info.append(Article(title=article['title'],
                                            article_url=article['article_url'],
                                            article_image_url=article['article_image_url'],
                                            author=article['author'],
                                            publication_date=article['publication_date'],
                                            summary=article['summary'],
                                            news_source=self.news_source
                                            ))

            except Exception as e:
                logger.exception('Error!!:{0} .. While getting {1}'.format(e, article['article_url']))
                self.errors.append(error_to_string(e))

        try:
            Article.objects.bulk_create(article_info)
            logger.info('')
            logger.info('Succesfully updated Latest The Daily Monitor Articles.{} new articles added'.format(
                len(article_info)))
            self.crawl.total_articles=len(article_info)
        except Exception as e:
            logger.exception('Error!!!{}'.format(e))
            self.errors.append(error_to_string(e))

