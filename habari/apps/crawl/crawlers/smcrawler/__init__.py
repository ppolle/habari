import logging
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from habari.apps.crawl.models import Article
from habari.apps.crawl.crawlers import AbstractBaseCrawler
from habari.apps.utils.error_utils import error_to_string, http_error_to_string

logger = logging.getLogger(__name__)

class SMCrawler(AbstractBaseCrawler):
    def __init__(self):
        super().__init__('SM')
        self.url = self.news_source.url
    
    def get_top_stories(self):
        rss_feeds = [
        'https://www.standardmedia.co.ke/rss/headlines.php',
        'https://www.standardmedia.co.ke/rss/kenya.php',
        'https://www.standardmedia.co.ke/rss/world.php',
        'https://www.standardmedia.co.ke/rss/politics.php',
        'https://www.standardmedia.co.ke/rss/opinion.php',
        'https://www.standardmedia.co.ke/rss/sports.php',
        'https://www.standardmedia.co.ke/rss/business.php',
        'https://www.standardmedia.co.ke/rss/columnists.php',
        'https://www.standardmedia.co.ke/rss/magazines.php',
        'https://www.standardmedia.co.ke/rss/evewoman.php'
        # 'https://www.standardmedia.co.ke/rss/agriculture.php'
        ]

        # Look at the rss links that I have left out. They are about 
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
                        date = article.pubDate.get_text().strip()
                        try:
                            publication_date = datetime.strptime(
                            date, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            publication_date = datetime.strptime(
                                date, '%a, %d %b %Y %H:%M:%S %z')
                        try:
                            author = [a.strip().upper() for a in article.author.get_text().split(' and ')]
                        except AttributeError:
                            author = ['']

                        article_details = {
                            'title': title,
                            'article_url': link,
                            'publication_date': publication_date,
                            'summary': summary,
                            'author': author}

                        if article_details not in stories and not Article.objects.filter(article_url=article_details['article_url']).exists():
                            stories.append(article_details)
                else:
                    logger.exception('{0} error!!Failed to get top stories from: {1}.'.format(request.status_code,rss))
                    self.errors.append(http_error_to_string(request.status_code, rss))

            except Exception as e:
                logger.exception(
                    'Error:{0} while getting stories from {1}'.format(e, rss))
                self.errors.append(error_to_string(e))

        return {story['article_url']:story for story in stories}.values()

    def update_article_details(self, article):
        request = requests.get(article['article_url'])

        if request.status_code == 200:
            soup = BeautifulSoup(request.content, 'lxml')
            
            if article['title'] == '':
                try:
                    title = soup.select_one('.article-title').get_text().strip()
                except AttributeError:
                    title = soup.select_one('h1.mb-4').get_text().strip()
                article['title'] = title

            if  article['author'] == ['']:
                try:
                    author = [a.strip().upper() for a in soup.select_one('.article-meta a').get_text().split(' and ')]
                except AttributeError:
                    try:
                        author = [soup.select_one('div .io-hidden-author').get_text().strip().upper()]
                    except AttributeError:
                        author = ['']
                article['author'] = author
            
            try:
                article_image_url = self.make_relative_links_absolute(soup.select_one('.article-body img').get('src'))
            except AttributeError:
                try:
                    article_image_url = self.make_relative_links_absolute(soup.select_one('figure img').get('src'))
                except AttributeError:
                    try:
                        article_image_url = soup.select_one('iframe').get('src') 
                    except AttributeError:
                        article_image_url = 'None'

            article['article_image_url'] = article_image_url
        else:
            logger.exception('{} Error while updating article details for {}'.format(request.status_code, article['article_url']))
            self.errors.append(http_error_to_string(request.status_code,article['article_url']))

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
                logger.exception('Error {}: updating article details for {}'.format(e, article['article_url']))
                self.errors.append(error_to_string(e))

        try:
            Article.objects.bulk_create(article_info)
            logger.info('')
            logger.info("Succesfully updated The Daily Standard's Articles.{} new articles added".format(
                len(article_info)))
            self.crawl.total_articles=len(article_info)
            self.crawl.save()
        except Exception as e:
            logger.exception('Error!!!{}'.format(e))
            self.errors.append(error_to_string(e))