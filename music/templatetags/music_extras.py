from django import template
import datetime

register = template.Library()

@register.filter(name='timeformat')
def timeformat(value):
    if isinstance(value, datetime.timedelta):
        # Ottiene il numero totale di secondi dal timedelta
        total_seconds = int(value.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"
    else:
        return "Invalid input type"
