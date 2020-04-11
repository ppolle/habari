from habari.apps.crawl.models import NewsSource

def get_source_names():
	sources = NewsSource.objects.values_list('name', flat=True)
	return {'sources':sources}