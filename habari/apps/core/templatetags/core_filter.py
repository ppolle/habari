import re
from django import template
register = template.Library()

@register.filter
def author_slug(value):
	val  = value.lower()
	return val.replace(' ','-')

@register.filter
def author_capitalize(value):
	cap_list = ['afp','reuters','bbc','a.p','xinhua','mirror', 'cnn', 'nmg']
	val = value.strip().lower()
	return " ".join(s.upper() if s in cap_list else s.capitalize() for s in val.split())

@register.filter
def startswith(value, starts):
	starts = '/{}/'.format(starts)
	if value.startswith(starts):
		return True
	return False

@register.filter
def title_cap(value):
	return " ".join(s if s.isupper() else s.capitalize() for s in value.split())

def capitalize_words(value):
	pass