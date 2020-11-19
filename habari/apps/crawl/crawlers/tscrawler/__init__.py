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

class TSCrawler(AbstractBaseCrawler):
    def __init__(self):
        super().__init__('TS')
        self.url = self.news_source.url

    def partial_links_to_ignore(self, url):
        links = ('https://www.the-star.co.ke/video/',
            'https://www.the-star.co.ke/classifieds/',
            'https://www.the-star.co.ke/cartoon/')

        if url.startswith(links):
            return True
        else:
            return False

    def get_category_links(self):
        logger.info('Getting links to all categories and subcategories')
        categories = [self.url,]

        try:
            get_categories = requests.get(self.url)
        except Exception as e:
            logger.exception('Error: {0} while getting categories from {1}'.format(e,self.url))
        else:
            if get_categories.status_code == 200:
                soup = BeautifulSoup(get_categories.content, 'lxml')
                all_categories = soup.select('.sidebar .nav-sidebar li a')

                for category in all_categories:
                    if category.get('href') is not None:
                        cat = self.make_relative_links_absolute(category.get('href'))
                        if cat not in categories and self.check_for_top_level_domain(cat) and not self.partial_links_to_ignore(cat) and cat is not None:
                            categories.append(cat)

        return categories
        
    def get_top_stories(self):
        logger.info('Getting top stories')
        story_links = []
        ignore_links = ['https://www.the-star.co.ke/news/2020-03-09-photos-filthy-city-markets-raise-health-worries/',]
        
        for category in self.get_category_links():
            try:
                top_stories = requests.get(category)
                if top_stories.status_code == 200:
                    soup = BeautifulSoup(top_stories.content, 'lxml')
                    articles = soup.select('.article-body a')

                    for article in articles:
                        try:
                            article = self.make_relative_links_absolute(article.get('href'))
                            if not Article.objects.filter(article_url=article).exists() and article not in story_links and self.check_for_top_level_domain(article) and not self.partial_links_to_ignore(article):
                                story_links.append(article)
                        except Exception as e:
                            logger.exception('Error: {}, while trying to sanitize link'.format(e))
            except Exception as e:
                logger.exception(
                    'Crawl Error: {0} , while getting top stories for: {1}'.format(e, category))
                self.errors.append(error_to_string(e))

        return filter(lambda x:x not in ignore_links, story_links)

    def update_article_details(self, link):
        story = requests.get(link)
        if story.status_code == 200:
            soup = BeautifulSoup(story.content, 'lxml')
            try:
                title = soup.select_one('.header-primary-title .article-title').get_text().strip()
            except AttributeError:
                title = soup.find("meta",  property="og:title").get('content').strip()
            try:
                publication_date = soup.select_one('.article-body .article-published').get_text().strip()
            except AttributeError:
                publication_date = soup.find("meta",  property="article:published", itemprop="datePublished").get('content')
            try:
                date = pytz.timezone("Africa/Nairobi").localize(datetime.strptime(publication_date, '%d %B %Y - %H:%M'), is_dst=None)
            except ValueError:
                date = pytz.timezone("Africa/Nairobi").localize(datetime.strptime(publication_date, '%Y-%m-%dT%H:%M:%S.%fZ'), is_dst=None)
            try:
                author_string = soup.select_one(
                '.article-body .mobile-display .author-name span').get_text().lower()
                author = [self.sanitize_author_string(a.strip(' /')) for a in re.split(' AND | and |/ |, ',author_string)]
            except AttributeError:
                try:
                    author_list = soup.select('p.Theme-Byline .Theme-ForegroundColor-10')
                    author = self.sanitize_author_iterable(author_list)
                except AttributeError:
                    author = []

            try:
                image_url = soup.select_one('.article-widgets .wrap img').get('src').lstrip(' /')
            except AttributeError:
                try:
                    image_url = soup.select_one('.youtube-wrap iframe').get('src').lstrip(' /')
                except AttributeError:
                    try:
                        image_url = soup.find("meta",  property="og:image").get('content').strip()
                    except AttributeError:
                        image_url ='None'

            try:
                summary = re.sub(r'•|\n', '', soup.select_one('.article-intro').get_text().strip())
            except AttributeError:
                try:
                    summary = soup.find("meta",  property="og:description").get('content').strip()
                except AttributeError:
                    summary = ' '

        return {'article_url': link,
                'image_url': image_url,
                'article_title': title,
                'publication_date': date,
                'author': author,
                'summary': summary
                }

    def update_top_stories(self):
        stories = self.get_top_stories()
        article_info = []

        for article in stories:
            try:
                logger.info('Updating article details for: {}'.format(article))
                story = self.update_article_details(article)
 
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
            logger.info('Succesfully updated Latest The Star Articles.{} new articles added'.format(
                len(article_info)))
            self.crawl.total_articles=len(article_info)
            self.crawl.save()
        except Exception as e:
            logger.exception('Error Populating the database{}'.format(e))
            self.errors.append(error_to_string(e))