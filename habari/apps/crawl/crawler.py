import re
import requests
import tldextract
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from habari.apps.crawl.models import Article


class AbstractBaseCrawler:
    def make_relative_links_absolute(self, link):
        print('Sanitizing ' + str(link))
        try:
            from urlparse import urljoin
        except ImportError:
            from urllib.parse import urljoin

        if not link.startswith(self.url):
            link = urljoin(self.url, link)

        return link

    def create_datetime_object_from_string(self, date_string):
        date_pattern_1 = re.search(
            r"(\d+ weeks?,? )?(\d+ days?,? )?(\d+ hours?,? )?(\d+ mins?,? )?(\d+ secs? )?ago", date_string)
        date_pattern_2 = re.search(
            r"^(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.](19|20)\d\d$", date_string)
        date_pattern_3 = re.search(
            r"^(Sun|Mon|Tue|Wed|Thur|Fri|Sat)\s(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s(0[1-9]|[12][0-9]|3[01])\s[0-5][0-9]:[0-5][0-9]:[0-5][0-9]\s(UTC|IST|CST|EAT|EST)\s(19|20)\d\d$", date_string)

        if date_pattern_1:
            parsed_date_String = [date_string.split()[:2]]
            time_dict = dict((fmt, float(amount))
                             for amount, fmt in parsed_date_String)
            dt = timedelta(**time_dict)
            return datetime.now() - dt

        if date_pattern_2:
            return datetime.strptime(date_string, '%d/%m/%Y')

        if date_pattern_3:
            return datetime.strptime(date_string, '%a %b %d %H:%M:%S %Z %Y')

    def check_for_top_level_domain(self, link):
        '''
        makes sure that links are the same top level domain as the news site being crawled
        '''
        base_tld = tldextract.extract(self.url).registered_domain
        link_tld = tldextract.extract(link).registered_domain

        if link.startswith('https://') or link.startswith('http://'):
            if base_tld == link_tld:
                return True
            else:
                return False
        else:
            return False


class DNCrawler(AbstractBaseCrawler):
    def __init__(self):
        self.url = 'https://www.nation.co.ke/'

    def get_category_links(self):
        print('Getting links to all categories and sub-categories')
        get_categories = requests.get(self.url)
        categories = [self.url, ]

        if get_categories.status_code == 200:
            soup = BeautifulSoup(get_categories.content, 'html.parser')
            all_categories = soup.select(
                '.menu-vertical a') + soup.select('.hot-topics a')

            for category in all_categories:
                cat = self.make_relative_links_absolute(category.get('href'))

                if cat.startswith('https://www.nation.co.ke/photo/') or cat.startswith('https://www.nation.co.ke/video/'):
                    pass
                else:
                    categories.append(cat)

        return categories

    def get_top_stories(self):
        print('Getting the latest stories')
        story_links = []
        for stories in self.get_category_links():
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
                        story = self.make_relative_links_absolute(story.get('href'))
                        if story not in story_links and self.check_for_top_level_domain(story):
                            story_links.append(story)

            except Exception as e:
                print(
                    '{0} error while getting top stories for {1}'.format(e, stories))

        return story_links

    def get_main_story_details(self, link):
        story = requests.get(link)

        if story.status_code == 200:
            soup = BeautifulSoup(story.content, 'html.parser')
            image_url = self.make_relative_links_absolute(
                soup.select('.story-view header img')[0].get('src'))
            title = [t.get_text()
                     for t in soup.select('.story-view header h2')][0]
            publication_date = [p.get_text()
                                for p in soup.select('.story-view header h6')][0]
            date = datetime.strptime(publication_date, '%A %B %d %Y')
            author = [a.get_text() for a in soup.select(
                '.story-view .author strong')][0].strip()[2:]
        else:
            print('Failed to get {} details.'.format(link))

        return {'article_url': link,
                'image_url': image_url,
                'article_title': title,
                'publication_date': date,
                'author': author}

    def get_newsplex_and_healthynation_story_details(self, link):
        story = requests.get(link)

        if story.status_code == 200:
            soup = BeautifulSoup(story.content, 'html.parser')
            image_url = self.make_relative_links_absolute(
                soup.select_one('.hero.hero-chart .figcap-box img').get('src'))
            title = soup.select_one('.hero.hero-chart').get_text()
            publication_date = soup.select_one('date').get_text()
            date = self.create_datetime_object_from_string(publication_date)
            author = soup.select_one(
                '.byline figcaption h6').get_text().strip()[2:]

        else:
            print('Failed to get {} details'. format(link))

        return {'article_url': link,
                'image_url': image_url,
                'article_title': title,
                'publication_date': date,
                'author': author
                }

    def update_top_stories(self):
        top_articles = self.get_top_stories()
        article_info = []
        for article in top_articles:
            try:
                print('Updating story content for ' + article)
                if article.startswith('https://www.nation.co.ke/health') or article.startswith('https://www.nation.co.ke/newsplex'):
                    story = self.get_newsplex_and_healthynation_story_details(
                        article)
                else:
                    story = self.get_main_story_details(article)
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
            print('')
            print('Succesfully updated Daily Nation Latest Articles.{} new articles added'.format(
                len(article_info)))
        except Exception as e:
            print('Error!!!{}'.format(e))

        return article_info


class BDCrawler(AbstractBaseCrawler):
    def __init__(self):
        self.url = 'https://www.businessdailyafrica.com/'

    def get_category_links(self):
        print('Getting links to all categories and sub-categories')
        get_categories = requests.get(self.url)
        categories = [self.url, ]

        if get_categories.status_code == 200:
            soup = BeautifulSoup(get_categories.content, 'html.parser')
            all_categories = soup.select('.menu-vertical a')

            for category in all_categories:
                cat = self.make_relative_links_absolute(category.get('href'))

                if cat.startswith('https://www.businessdailyafrica.com/videos/') or cat.startswith('https://www.businessdailyafrica.com/datahub/'):
                    pass
                else:
                    categories.append(cat)

        return categories

    def get_top_stories(self):
        print('Getting top stories')
        story_links = []

        for stories in self.get_category_links():
            try:
                top_stories = requests.get(stories)
                if top_stories.status_code == 200:
                    soup = BeautifulSoup(top_stories.content, 'html.parser')
                    articles = soup.select('.article a')

                    for article in articles:
                        article = self.make_relative_links_absolute(
                            article.get('href'))
                        if article not in story_links and self.check_for_top_level_domain(article):
                            story_links.append(article)

            except Exception as e:
                print(
                    '{0} error while getting top stories for {1}'.format(e, stories))

        return story_links

    def get_story_details(self, link):
        story = requests.get(link)
        if story.status_code == 200:
            soup = BeautifulSoup(story.content, 'html.parser')

            title = soup.find(class_='article-title').get_text()
            image_url = self.make_relative_links_absolute(
                soup.select_one('.article-img-story img.photo_article').get('src'))
            publication_date = soup.select_one(
                '.page-box-inner header small.byline').get_text()
            date = datetime.strptime(publication_date, '%A, %B %d, %Y %H:%M')
            author = soup.select_one(
                '.page-box-inner .mobileShow small.byline').get_text().strip()[2:]

        return {'article_url': link,
                'image_url': image_url,
                'article_title': title,
                'publication_date': date,
                'author': author
                }

    def update_top_stories(self):
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
                                                news_source='BD'
                                                ))

            except Exception as e:
                print('{0} error while getting {1}'.format(e, article))

        try:
            Article.objects.bulk_create(article_info)
            print('')
            print('Succesfully updated Business Daily Latest Articles.{} new articles added'.format(
                len(article_info)))
        except Exception as e:
            print('Error!!!{}'.format(e))

class EACrawler(AbstractBaseCrawler):
    def __init__(self):
        self.url = 'https://www.theeastafrican.co.ke/'

    def get_rss_feed_links(self):
        print('Getting RSS feeds links')
        categories = [self.url, ]
        rss_feeds = []

        try:
            get_categories= requests.get(self.url)
            if get_categories.status_code == 200:
                soup = BeautifulSoup(get_categories.content, 'html.parser')
                all_categories = soup.select('.menu-vertical a')

                for category in all_categories:
                    category = self.make_relative_links_absolute(category.get('href'))
                    categories.append(category)

            for category in categories:
                request = requests.get(category)
                if request.status_code == 200:
                    soup = BeautifulSoup(request.content, 'html.parser')
                    rss = self.make_relative_links_absolute(soup.select('.social-networks a')[4].get('href'))
                    rss_feeds.append(rss)

            return rss_feeds
        except Exception as e:
            print('Error!!{} while getting rss feeds'.format(e))

    def get_top_stories(self):
        rss_feeds = self.get_rss_feed_links()
        stories = []
        for rss in rss_feeds:
            try:
                print('Getting top stories from {}'.format(rss))
                request = requests.get(rss)
                if request.status_code == 200:
                    soup = BeautifulSoup(request.content, 'xml')
                    articles = soup.find_all('item')

                    for article in articles:
                        title = article.title.get_text()
                        summary = article.description.get_text()
                        link = article.link.get_text()
                        date = article.date.get_text()
                        publication_date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')

                        article_details = {
                            'title': title,
                            'article_url': link,
                            'publication_date': publication_date,
                            'summary': summary,}

                        if article_details not in stories:
                            stories.append(article_details)

            except Exception as e:
                print('Error:{0} while getting stories from {1}'.format(e,rss))
        return stories

    def update_article_details(self, article):
        request = requests.get(article['article_url'])

        if request.status_code == 200:
            soup = BeautifulSoup(request.content, 'lxml')
            image_url = self.make_relative_links_absolute(
                soup.select('.story-view header img')[0].get('src'))
            author = [a.get_text() for a in soup.select(
                '.story-view .author strong')][0].strip()[2:]
            article['article_image_url'] = image_url
            article['author'] = author

        return article

    def update_top_stories(self):
        articles = self.get_top_stories()
        article_info = []
        for article in articles:
            try:
                print('Updating article details for: {}'.format(article['article_url']))
                self.update_article_details(article)
                if not Article.objects.filter(article_url=article['article_url']).exists():
                    article_info.append(Article(title=article['title'],
                                                article_url=article['article_url'],
                                                article_image_url=article['article_image_url'],
                                                author=article['author'],
                                                publication_date=article['publication_date'],
                                                summary=article['summary'],
                                                news_source='EA'
                                                ))

            except Exception as e:
                print('Error!!:{0} .. While getting {1}'.format(e, article))


        try:
            Article.objects.bulk_create(article_info)
            print('')
            print('Succesfully updated Latest East African Articles.{} new articles added'.format(
                len(article_info)))
        except Exception as e:
            print('Error!!!{}'.format(e))

class CTCrawler(AbstractBaseCrawler):
    def __init__(self):
        self.url = 'https://www.thecitizen.co.tz/'

    def get_rss_feed_links(self):
        print('Getting RSS feeds links')      
        categories = [self.url, ]
        rss_feeds = []

        try:
            get_categories = requests.get(self.url)
            if get_categories.status_code == 200:
                soup = BeautifulSoup(get_categories.content, 'html.parser')
                all_categories = soup.select('.menu-vertical a')

                for category in all_categories:
                    category = self.make_relative_links_absolute(category.get('href'))
                    categories.append(category)

            for category in categories:
                request = requests.get(category)
                if request.status_code == 200:
                    soup = BeautifulSoup(request.content, 'html.parser')
                    social_links = soup.select('.social-networks a')
                    for social_link in social_links:
                        link = social_link.get('href')
                        if link.endswith('.xml'):
                            rss_feeds.append(self.make_relative_links_absolute(link))

            return rss_feeds

        except Exception as e:
            print('Error!!{} while getting rss feeds'.format(e))

    def get_top_stories(self):
        rss_feeds = self.get_rss_feed_links()
        stories = []
        for rss in rss_feeds:
            try:
                print('Getting top stories from {}'.format(rss))
                request = requests.get(rss)
                if request.status_code == 200:
                    soup = BeautifulSoup(request.content, 'xml')
                    articles = soup.find_all('item')

                    for article in articles:
                        title = article.title.get_text()
                        summary = article.description.get_text()
                        link = article.link.get_text()
                        date = article.date.get_text()
                        publication_date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')

                        article_details = {
                            'title': title,
                            'article_url': link,
                            'publication_date': publication_date,
                            'summary': summary,}

                        if article_details not in stories:
                            stories.append(article_details)

            except Exception as e:
                print('Error:{0} while getting stories from {1}'.format(e,rss))
        return stories
    
    def update_article_details(self, article):
        request = requests.get(article['article_url'])

        if request.status_code == 200:
            soup = BeautifulSoup(request.content, 'lxml')
            try:
                image_url = self.make_relative_links_absolute(
                soup.select_one('.story-view header img').get('src'))
            except AttributeError:
                try:
                    image_url = soup.select_one('.videoContainer iframe').get('src')
                except:
                    image_url = 'None'
                    print('Get Image Error: while getting ...{}.'.format(article['article_url']))
                    raise
            
            try:
                author = soup.select_one('section .author').get_text()
                author  = re.sub(r'\w*@.*|(\w+[.|\w])*@(\w+[.])*\w+|More by this Author|By', '', author).strip()
            except AttributeError:
                author = 'None'
            except:
                print('Error getting author details')
                


            article['article_image_url'] = image_url
            article['author'] = author

        return article

    def update_top_stories(self):
        articles = self.get_top_stories()
        article_info = []

        for article in articles:
            try:
                print('Updating article details for: {}'.format(article['article_url']))
                self.update_article_details(article)
                if not Article.objects.filter(article_url=article['article_url']).exists():
                    article_info.append(Article(title=article['title'],
                                                article_url=article['article_url'],
                                                article_image_url=article['article_image_url'],
                                                author=article['author'],
                                                publication_date=article['publication_date'],
                                                summary=article['summary'],
                                                news_source='CT'
                                                ))
                # print(article['title'])
                # # print(article['article_image_url'])
                # print(article['author'])
                # print(article['article_image_url'])
                # print('')

            except Exception as e:
                print('Error!!:{0} .. While getting {1}'.format(e, article['article_url']))

        try:
            Article.objects.bulk_create(article_info)
            print('')
            print("Succesfully updated The Citizen's Articles.{} new articles added".format(
                len(article_info)))
        except Exception as e:
            print('Error!!!{}'.format(e))

        print('A total of {} articles found'.format(len(articles)))