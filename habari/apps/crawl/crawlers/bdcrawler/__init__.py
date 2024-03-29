import re
import pytz
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from habari.apps.crawl.models import Article
from habari.apps.crawl.crawlers import AbstractBaseCrawler
from habari.apps.utils.error_utils import error_to_string, http_error_to_string

logger = logging.getLogger(__name__)


class BDCrawler(AbstractBaseCrawler):
    def __init__(self):
        super().__init__('BD')
        self.url = self.news_source.url
        self.categories = self.get_category_links()

    def partial_links_to_ignore(self, url):
        links = ('https://www.businessdailyafrica.com/author-profile/',
                 'https://www.businessdailyafrica.com/videos/',
                 'https://www.businessdailyafrica.com/datahub/',
                 'https://www.businessdailyafrica.com/news/counties/Traders-suffer-losses-as-Gikomba-market-burns/4003142-5582822-ovxkjr/index.html',
                 'https://www.businessdailyafrica.com/bd/author-profiles/',
                 'https://www.businessdailyafrica.com/bd/videos/',)

        if url.startswith(links):
            return True
        else:
            return False

    def get_category_links(self):
        logger.info('Getting links to all categories and sub-categories')
        categories = [self.url, ]
        try:
            get_categories = self.requests(self.url)
        except Exception as e:
            logger.exception(
                'Error: {0} , while getting categories from: {1}'.format(e, self.url))
            self.errors.append(error_to_string(e))
        else:
            if get_categories.status_code == 200:
                soup = BeautifulSoup(get_categories.content, 'html.parser')
                all_categories = soup.select('.menu-vertical a')

                for category in all_categories:
                    if category.get('href') is not None:
                        cat = self.make_relative_links_absolute(
                            category.get('href'))
                        if not self.partial_links_to_ignore(cat):
                            categories.append(cat)
            else:
                logger.exception(
                    '{0} error while getting categories and sub-categories for {1}'.format(get_categories.status_code, self.url))
                self.errors.append(http_error_to_string(
                    get_categories.status_code, self.url))

        for category in categories:
            try:
                get_all_categories = self.requests(category)
            except Exception as e:
                logger.exception(
                    'Error: {0} while getting categories from {1}'.format(e, category))
                self.errors.append(error_to_string(e))
            else:
                if get_all_categories.status_code == 200:
                    soup = BeautifulSoup(
                        get_all_categories.content, 'html.parser')
                    additional_cat = soup.select(
                        'article.article.article-list-featured header h5 a')
                    for new_cat in additional_cat:
                        if new_cat.get('href') is not None:
                            cat = self.make_relative_links_absolute(
                                new_cat.get('href'))
                            if not self.partial_links_to_ignore(cat) and cat not in categories:
                                categories.append(cat)
                else:
                    logger.exception(
                        '{0} error while getting categories and sub-categories for {1}'.format(get_all_categories.status_code, category))
                    self.errors.append(http_error_to_string(
                        get_all_categories.status_code, category))

        return categories

    def get_top_stories(self):
        logger.info('Getting top stories')
        story_links = []

        for stories in self.categories:
            try:
                top_stories = self.requests(stories)
                if top_stories.status_code == 200:
                    soup = BeautifulSoup(top_stories.content, 'html.parser')
                    articles = soup.select('.article a')

                    for article in articles:
                        try:
                            if article.get('href') is not None:
                                article = self.make_relative_links_absolute(
                                    article.get('href'))
                                if not Article.objects.filter(article_url=article).exists() and article not in story_links and self.check_for_top_level_domain(article) and not self.partial_links_to_ignore(article):
                                    story_links.append(article)
                        except Exception as e:
                            logger.exception('{} error while sanitizing {} and getting stories from {}'.format(
                                e, article.get('href'), stories))
                            self.errors.append(error_to_string(e))

            except Exception as e:
                logger.exception(
                    'Crawl Error: {0} ,while getting top stories for: {1}'.format(e, stories))
                self.errors.append(error_to_string(e))

        return filter(lambda x: x not in self.categories, story_links)

    def update_article_details(self, link):
        story = self.requests(link)
        if story.status_code == 200:
            soup = BeautifulSoup(story.content, 'html.parser')
            try:
                author_page = soup.select_one('header.author-header').get_text()
                return {'author-page':True}
            except AttributeError:
                try:
                    title = soup.find(class_='article-title').get_text().strip()
                except AttributeError:
                    title  = soup.find("meta",  property="og:title").get('content').strip()

                try:
                	publication_date = soup.select_one('.page-box-inner header small.byline').get_text().strip()
                	date = pytz.timezone("Africa/Nairobi").localize(datetime.strptime(publication_date, '%A, %B %d, %Y %H:%M'), is_dst=None)
                except Exception:
                	publication_date = soup.find("meta",  property="og:article:published_time").get('content').strip()
                	date = pytz.timezone("Africa/Nairobi").localize(
    	                datetime.strptime(publication_date, '%Y-%m-%d %H:%M:%S'), is_dst=None)

                author_list = soup.select('.mobileShow article.article.article-summary header.article-meta-summary strong')
                author = self.sanitize_author_iterable(author_list)

                try:
                    image_url = self.make_relative_links_absolute(
                        soup.select_one('.article-img-story img.photo_article').get('src').strip())
                except AttributeError:
                    try:
                        image_url = soup.select_one(
                            '.article-img-story.fluidMedia iframe').get('src').strip()
                    except AttributeError:
                        image_url = 'None'

                try:
                    summary = soup.select_one(
                        '.summary-list').get_text().strip()[:3000]
                except AttributeError:
                    summary = ' '

                return {'article_url': link,
                        'image_url': image_url,
                        'article_title': title,
                        'publication_date': date,
                        'author': author,
                        'summary': summary,
                        'author-page':False
                        }

    def update_top_stories(self):
        top_articles = self.get_top_stories()
        article_info = []
        for article in top_articles:
            logger.info('Updating article details for: ' + article)
            try:
                story = self.update_article_details(article)
                if story['author-page'] is False:
                    article_info.append(Article(title=story['article_title'],
                                                article_url=story['article_url'],
                                                article_image_url=story['image_url'],
                                                author=story['author'],
                                                publication_date=story['publication_date'],
                                                summary=story['summary'],
                                                news_source=self.news_source
                                                ))

            except Exception as e:
                logger.exception(
                    'Crawling Error: {0} while getting data from: {1}'.format(e, article))
                self.errors.append(error_to_string(e))

        try:
            Article.objects.bulk_create(article_info)
            logging.info('')
            logging.info('Succesfully updated Business Daily Latest Articles.{} new articles added'.format(
                len(article_info)))
            self.crawl.total_articles = len(article_info)
            self.crawl.save()
        except Exception as e:
            logger.exception('Error!!!{}'.format(e))
            self.errors.append(error_to_string(e))
