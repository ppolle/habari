import re
import pytz
import logging
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from habari.apps.crawl.models import Article
from habari.apps.crawl.crawlers import AbstractBaseCrawler
from habari.apps.utils.string_utils import printable_text
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
                        title = printable_text(article.title.get_text().strip())
                        summary = printable_text(article.description.get_text().strip()[:3000])
                        link = article.link.get_text().strip()
                        date = article.pubDate.get_text().strip()
                        try:
                            publication_date = pytz.timezone("Africa/Nairobi").localize(datetime.strptime(date, '%Y-%m-%d %H:%M:%S'), is_dst=None)
                        except ValueError:
                            publication_date = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %z').astimezone(pytz.timezone("Africa/Nairobi"))
                        try:
                            author = [printable_text(a.strip().upper()) for a in re.split(' and |, |&',article.author.get_text().lower())]
                        except AttributeError:
                            author = []

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
            if soup.find(string=re.compile('Log in for free access to most premium news and information |Create your free account or log in to continue reading|Log in or register to access premium content only available to our subscribers')):
                if article['title'] == '':
                    article['title'] = 'Title Not Available'

                if len(article['author']) == 0:
                    article['author'] = []

                article['article_image_url'] = 'None'
            else:
                if article['title'] == '':
                    try:
                        title = soup.select_one('.article-title').get_text().strip()
                    except AttributeError:
                        try: 
                            title = soup.select_one('h1.mb-4').get_text().strip()
                        except AttributeError:
                            try:
                                title = soup.select_one('.articleheading').get_text().strip()
                            except AttributeError:
                                try:
                                    title = soup.select_one('.header h2').get_text().strip()
                                except Exception as e:
                                    title = re.sub('-',' ',article.article_url.split('/')[-1])

                    article['title'] = printable_text(title)

                if  len(article['author']) == 0:
                    try:
                        author = [printable_text(a.strip().upper()) for a in re.split('&| and |, ',soup.select_one('.article-meta a').get_text().lower())]
                    except AttributeError:
                        try:
                            author = [a.strip().upper() for a in re.split('&| and |, ', soup.select_one('div .io-hidden-author').get_text().strip().lower())]
                        except AttributeError:
                            try:
                                author = [a.strip().upper() for a in re.split('&| and |, ', soup.select_one('.small.text-muted.mb-3 a').get_text().lower())]
                            except AttributeError:
                                try:
                                    author = [a.strip().upper() for a in re.split('&| and |, ', soup.find("meta",  attrs={'name':'author'}).get('content').lower())]
                                except AttributeError:
                                    author = []
                    if author == [''] or author == [':']:
                        author = []

                    article['author'] = author
                
                try:
                    article_image_url = soup.find("meta",  property="og:image").get('content')
                except AttributeError:
                    article_image_url = soup.find("meta",  property="og:image:secure_url").get('content')

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