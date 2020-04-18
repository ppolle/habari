from habari.apps.crawl.models import NewsSource

def get_source_names(request):
	sources = NewsSource.objects.values('name', 'slug')
	return {'sources':sources}