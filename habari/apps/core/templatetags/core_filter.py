from string import capwords
from django import template
register = template.Library()

@register.filter
def author_slug(value):
	val  = value.lower()
	return val.replace(' ','-')

@register.filter
def author_capitalize(value):
	cap_list = ['afp','reuters','bbc','a.p','xinhua','mirror']
	val = value.strip().lower()
	return " ".join(s.upper() if s in cap_list else s.title() for s in val.split())

