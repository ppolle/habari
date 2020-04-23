from django import template
from django.utils import timezone
from django.core.urlresolvers import reverse
register = template.Library()

@register.simple_tag
def day_name(delta):
	today = timezone.now()
	date = today - timezone.timedelta(delta)
	return date.strftime('%A').title()

@register.simple_tag
def day_url(source, delta):
	today = timezone.now()
	date = today - timezone.timedelta(delta)
	return reverse('day', args=(source, str(date.year).zfill(4), str(date.month).zfill(2), str(date.day).zfill(2)))