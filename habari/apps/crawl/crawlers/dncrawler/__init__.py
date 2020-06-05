import pytz
import logging
import requests
import cssutils
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
        links = ('https://www.nation.co.ke/photo',
        'https://www.nation.co.ke/video',
        'https://www.nation.co.ke/newsplex/deadly-force-database',
        'https://www.nation.co.ke/newsplex/murder-at-home-database',
        'https://www.nation.co.ke/oped/cartoon/',
        'https://www.nation.co.ke/health/3476990-5485696-da2r6w/index.html')

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
                main_categories = soup.select('.menu-vertical a') + soup.select('li.story-teaser.tiny-teaser a')[:9]
                additional_categories = soup.select('.hot-topics a')
                sup_categories = []

                for cat in main_categories:
                    try:
                        if cat.get('href') is not None:
                            link = self.make_relative_links_absolute(cat.get('href'))
                            request = requests.get(link)
                    except Exception as e:
                        logger.exception('Error {} while getting categories from {}'.format(e,cat.get('href')))
                        self.errors.append(error_to_string(e))
                    else:
                        if request.status_code == 200:
                            soup = BeautifulSoup(request.content, 'html.parser')
                            item = soup.select('.gallery-words h4 a')
                            if len(item) > 0:
                                sup_categories.extend(item)

                for cat in additional_categories:
                    try:
                        if cat.get('href') is not None:
                            link = self.make_relative_links_absolute(cat.get('href'))
                            request = requests.get(link)
                    except Exception as e:
                        logger.exception('Error {} while getting additonal categories from {}'.format(e,cat.get('href')))
                        self.errors.append(error_to_string(e))
                    else:
                        if request.status_code == 200:
                            soup = BeautifulSoup(request.content, 'html.parser')
                            items = soup.select('.breadcrumb-item a')
                            if len(items) > 0:
                                sup_categories.extend(items)

                all_categories = main_categories+additional_categories+sup_categories

                for category in all_categories:
                    if category.get('href') is not None:
                        cat = self.make_relative_links_absolute(category.get('href'))
                        if not self.partial_links_to_ignore(cat) and cat not in categories:
                            categories.append(cat)
            else:
                logger.exception(
                        '{0} error while getting categories and sub-categories for {1}'.format(get_categories.status_code, self.url))
                self.errors.append(http_error_to_string(get_categories.status_code,sel.url))

        return categories

    def get_top_stories(self):
        logger.info('Getting the latest stories')
        story_links = []
        for stories in self.categories:
            try:
                top_stories = requests.get(stories)
                if top_stories.status_code == 200:
                    soup = BeautifulSoup(top_stories.content, 'html.parser')

                    if stories.startswith('https://www.nation.co.ke/health') or stories.startswith('https://www.nation.co.ke/newsplex'):
                        stories = soup.select('article a')
                    else:
                        soup = BeautifulSoup(
                            top_stories.content, 'html.parser')
                        small_story_list = soup.select('.small-story-list a')
                        story_teaser = soup.select('.story-teaser a')
                        nation_prime = soup.select('.gallery-words a')
                        latest_news = soup.select('.most-popular-item a')

                        stories = small_story_list + story_teaser + nation_prime + latest_news

                    for story in stories:
                        try:
                            if story.get('href') is not None:
                                story = self.make_relative_links_absolute(
                                    story.get('href'))
                                if not Article.objects.filter(article_url=story).exists() and story not in story_links and self.check_for_top_level_domain(story) and not self.partial_links_to_ignore(story):
                                    story_links.append(story)
                        except Exception as e:
                            logger.exception(
                    '{0} error while sanitizing {1} and getting top stories from:'.format(e, story.get('href'), stories))
                            self.errors.append(error_to_string(e))

            except Exception as e:
                logger.exception(
                    '{0} error while getting top stories for {1}'.format(e, stories))
                self.errors.append(error_to_string(e))

        return filter(lambda x:x not in self.categories, story_links)

    def get_main_story_details(self, link):
        story = requests.get(link)

        if story.status_code == 200:
            soup = BeautifulSoup(story.content, 'html.parser')
            try:
                title = soup.select_one('header h2').get_text().strip()
            except TypeError:
                title = soup.find("h3",  itemprop="name").get_text()
            publication_date = [p.get_text().strip()
                                for p in soup.select('header h6')][0]
            date = pytz.timezone("Africa/Nairobi").localize(datetime.strptime(publication_date, '%A %B %d %Y'), is_dst=None)
            author_list = soup.select('section.author strong')
            author = self.sanitize_author_iterable(author_list)

            try:
                image_url = self.make_relative_links_absolute(
                    soup.find("meta",  property="og:image").get('content'))
            except AttributeError:
                try:
                    image_url = soup.select_one(
                        '.videoContainer iframe').get('src')
                except AttributeError:
                    try:
                        image_url = soup.select_one('video').get('src')
                    except AttributeError:
                        image_url = 'None'

            try:
                summary = soup.select_one('.summary div ul').get_text().strip()[:3000]
            except AttributeError:
                summary = soup.find("meta",  property="og:description").get('content')

        else:
            logger.exception('Failed to get {} details.'.format(link))
            self.errors.append(http_error_to_string(story.status_code,link))


        return {'article_url': link,
                'image_url': image_url,
                'article_title': title,
                'publication_date': date,
                'author': author,
                'summary': summary}

    def get_newsplex_and_healthynation_story_details(self, link):
        story = requests.get(link)

        if story.status_code == 200:
            soup = BeautifulSoup(story.content, 'html.parser')
            title = soup.select_one('.hero.hero-chart').get_text().strip()
            publication_date = soup.find("meta",  property="og:article:published_time").get('content')
            date = pytz.timezone("Africa/Nairobi").localize(datetime.strptime(publication_date, '%Y-%m-%d %H:%M:%S'), is_dst=None)
            author_list = soup.select('.byline figcaption h6')
            author = self.sanitize_author_iterable(author_list)
            image_url = self.make_relative_links_absolute(
                soup.find("meta",  property="og:image").get('content'))
            summary = soup.select_one('article.post header').get_text().strip()[:3000]

        else:
            logger.exception('Failed to get {} details'. format(link))
            self.errors.append(http_error_to_string(story.status_code,link))

        return {'article_url': link,
                'image_url': image_url,
                'article_title': title,
                'publication_date': date,
                'author': author,
                'summary': summary}

    def get_nationprime_story_details(self, link):
        story = requests.get(link)

        if story.status_code == 200:
            soup = BeautifulSoup(story.content, 'html.parser')
            title = soup.select_one('.page-title').get_text().strip()
            publication_date = soup.select_one('.date').get_text().strip()
            date = pytz.timezone("Africa/Nairobi").localize(datetime.strptime(publication_date, '%A %B %d %Y'), is_dst=None)
            author_list = soup.select('.article-content h6.name')
            author = self.sanitize_author_iterable(author_list)
            image_url = self.make_relative_links_absolute(soup.find("meta",  property="og:image").get('content'))
            summary = 'None'
        else:
            logger.exception('Failed to get {} details'. format(link))
            self.errors.append(http_error_to_string(story.status_code,link))

        return {'article_url': link,
                'image_url': image_url,
                'article_title': title,
                'publication_date': date,
                'author': author,
                'summary': summary}

    def update_top_stories(self):
        top_articles = self.get_top_stories()
        article_info = []
        startswith_newsplex = ('https://www.nation.co.ke/dailynation/health',
          'https://www.nation.co.ke/newsplex',
          'https://www.nation.co.ke/dailynation/brand-book',
          'https://www.nation.co.ke/gender',
          'https://www.nation.co.ke/dailynation/healthy-nation',
          )

        for article in top_articles:
            try:
                logger.info('Updating story content for ' + article)
                if article.startswith(startswith_newsplex):
                    story = self.get_newsplex_and_healthynation_story_details(
                        article)
                elif article.startswith('https://www.nation.co.ke/nationprime/'):
                    story = self.get_nationprime_story_details(article)
                else:
                    story = self.get_main_story_details(article)

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
