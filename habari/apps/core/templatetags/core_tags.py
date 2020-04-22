from django import template
from django.utils import timezone

register = template.Library()

@register.simple_tag
def day_name(delta):
	today = timezone.now()
	date = today - timezone.timedelta(delta)
	return date.strftime('%A').title()