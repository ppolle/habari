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
        'https://www.nation.co.ke/video')

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
                all_categories = soup.select('.menu-vertical a') + soup.select('.hot-topics a')

                for category in all_categories:
                    cat = self.make_relative_links_absolute(category.get('href'))
                    if not self.partial_links_to_ignore(cat):
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
            title = [t.get_text().strip()
                     for t in soup.select('.story-view header h2')][0]
            publication_date = [p.get_text().strip()
                                for p in soup.select('.story-view header h6')][0]
            date = datetime.strptime(publication_date, '%A %B %d %Y')
            author = [self.sanitize_author_string(
                a.get_text().strip()) for a in soup.select('.story-view .author')]

            try:
                image_url = self.make_relative_links_absolute(
                    soup.select_one('.story-view header img').get('src'))
            except AttributeError:
                try:
                    image_url = soup.select_one(
                        '.videoContainer iframe').get('src')
                except AttributeError:
                    image_url = 'None'

            try:
                summary = soup.select_one('.summary div ul').get_text().strip()[:3000]
            except AttributeError:
                summary = ' '

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
            publication_date = soup.select('date')[0].get_text().strip()
            date = self.create_datetime_object_from_string(publication_date)
            author = [self.sanitize_author_string(
                a.get_text().strip()) for a in soup.select('.byline figcaption h6')]
            try:
                image_url = self.make_relative_links_absolute(
                soup.select_one('.hero.hero-chart .figcap-box img').get('src'))
            except AttributeError:
                image_url = self.make_relative_links_absolute(
                    soup.select_one('.hero.hero-chart .figcap-box iframe').get('src'))
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
            date = datetime.strptime(publication_date, '%A %B %d %Y')
            author = [self.sanitize_author_string(
                a.get_text().strip()) for a in soup.select('.article-content h6.name')]
            image = cssutils.parseStyle(soup.select_one('.hero-image').get('style'))['background-image']
            image_url = image.replace('url(', '').replace(')', '')
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
        startswith_newsplex = ('https://www.nation.co.ke/health',
          'https://www.nation.co.ke/newsplex',
          'https://www.nation.co.ke/brandbook', 
          'https://www.nation.co.ke/gender', 
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
