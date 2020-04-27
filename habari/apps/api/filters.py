from django_filters import rest_framework as filters
from habari.apps.crawl.models import Article


class ArticleFilter(filters.FilterSet):
    source = filters.CharFilter(field_name="news_source__slug", lookup_expr='exact')
    title = filters.CharFilter(field_name="title", lookup_expr='icontains')

    class Meta:
        model = Article
        fields = ['source']