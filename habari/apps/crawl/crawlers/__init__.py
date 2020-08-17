import re
import string
import logging
import tldextract
from datetime import datetime, timedelta
from habari.apps.crawl.models import Article, NewsSource, Crawl

logger = logging.getLogger(__name__)

class AbstractBaseCrawler:
    def __init__(self, slug):
        self.news_source = NewsSource.objects.get(slug=slug)
        self.crawl = Crawl.objects.create(news_source=self.news_source)
        self.errors = []

    def run(self):
        self.crawl.status = Crawl.StatusType.Crawling
        self.crawl.save()
        self.update_top_stories()
        if len(self.errors) > 0:
            self.crawl.status = Crawl.StatusType.Error
            self.crawl.crawl_error = self.errors
        else:
            self.crawl.status = Crawl.StatusType.Good
        self.crawl.save()
        
    def make_relative_links_absolute(self, link):
        logger.info('Sanitizing ' + str(link))
        try:
            from urlparse import urljoin
        except ImportError:
            from urllib.parse import urljoin

        if not link.startswith(self.url):
            link = urljoin(self.url, link)

        return link

    def create_datetime_object_from_string(self, date_string):
        date_pattern_1 = re.search(
            r"(\d+ year?years?,? )?(\d+ months?month?,? )?(\d+ week?weeks?,? )?(\d+ days?day?,? )?(\d+ hours?hour?,? )?(\d+ minutes?minute?,? )?(\d+ seconds?second? )?ago", date_string)
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

        elif date_pattern_2:
            return datetime.strptime(date_string, '%d/%m/%Y')

        elif date_pattern_3:
            return datetime.strptime(date_string, '%a %b %d %H:%M:%S %Z %Y')
        else:
            return datetime.now()

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

    def sanitize_author_string(self, author):
        new_author = re.sub(
            r'\w*@.*|(\w+[.|\w])*@(\w+[.])*\w+|more by this author|By|BY |by|\n', '', author.lower()).strip().upper()
        return new_author

    def sanitize_author_iterable(self, author_iterable):
        author_list = []
        for item in author_iterable:
            if item is not None:
                authors = re.split('&| and |,', item.get_text().strip().lower())
                new_authors = [author_list.append(a) for a in map(lambda x:self.sanitize_author_string(x), authors)]

        return author_list


