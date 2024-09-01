from django import template
from django.utils import timezone
from datetime import datetime  

register = template.Library()

@register.filter
def short_timesince(value):
    """Returns a short version of the time since the given datetime."""
    if not isinstance(value, datetime):
        return ""

    now = timezone.now()

    # No idea what's happening here lmao
    if timezone.is_naive(value):
        value = timezone.make_aware(value, timezone.get_default_timezone())
    
    if timezone.is_naive(now):
        now = timezone.make_aware(now, timezone.get_default_timezone())

    time_difference = now - value
    seconds = time_difference.total_seconds()

    # Logic to format the time difference
    if seconds < 60:
        return "%d sec" % seconds
    elif seconds < 3600:
        return "%d min" % (seconds // 60)
    elif seconds < 86400:
        return "%d hr" % (seconds // 3600)
    else:
        return "%d day" % (seconds // 86400)
