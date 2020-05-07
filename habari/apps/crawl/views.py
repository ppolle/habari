from rest_framework.generics import ListAPiView
from .serializers import ArticleSerializer
from habari.apps.crawl.models import Article

# Create your views here.

class ArticleList(ListApiView):
	queryset = Article.objects.all()
	serializer_class = ArticleSerializer