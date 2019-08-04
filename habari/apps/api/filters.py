from django_filters import rest_framework as filters
from habari.apps.crawl.models import Article


class ArticleFilter(filters.FilterSet):
    source = filters.CharFilter(field_name="news_source", lookup_expr='exact')

    class Meta:
        model = Article
        fields = ['source']