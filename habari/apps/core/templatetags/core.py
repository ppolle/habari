from string import capwords
from django import template
register = template.Library()

@register.filter
def author_slug(value):
	val  = value.lower()
	return val.replace(' ','-')

@register.filter
def author_capitalize(value):
	cap_list = ['afp','reuters','bbc','a.p']
	val = value.strip().lower()
	if val in cap_list:
		return value.upper()
	else:
		return capwords(value)
