# org src: http://www.djangosnippets.org/snippets/129/
# Template tag
from datetime import date, timedelta

from django import template
from django.core.urlresolvers import reverse
from blog.models import Entry # You need to change this if you like to add your own events to the calendar

register = template.Library()


from datetime import date, timedelta

def get_last_day_of_month(year, month):
    if (month == 12):
        year += 1
        month = 1
    else:
        month += 1
    return date(year, month, 1) - timedelta(1)

@register.inclusion_tag('blog/month_nav.html')
def month_navigation(this_month=date.today(), prev=None, next=None):
    now = {'name': this_month.strftime('%b'),
            'link': reverse('entry_month', kwargs={
                    'year': this_month.year,
                    'month': this_month.strftime("%b").lower()})}
    if not prev:
        prev = this_month - timedelta(this_month.day)
    prev_c = {'name': prev.strftime('%b'),
            'link': reverse('entry_month', kwargs={
                    'year': prev.year,
                    'month': prev.strftime("%b").lower()})}
    if not next:
        next = this_month + timedelta(
                get_last_day_of_month(this_month.year, this_month.month).day
                - this_month.day + 1)
        print next
    if next <= date.today():
        next_c = {'name': next.strftime('%b'),
                'link': reverse('entry_month', kwargs={
                        'year': next.year,
                        'month': next.strftime("%b").lower()})}
    else:
        next_c = None
    return {'now': now, 'prev': prev_c, 'next': next_c}

@register.inclusion_tag('blog/calendar.html')
def month_cal(year=date.today().year, month=date.today().month):
    event_list = Entry.objects.filter(created_on__year=year,
            created_on__month=month)

    first_day_of_month = date(year, month, 1)
    last_day_of_month = get_last_day_of_month(year, month)
    first_day_of_calendar = first_day_of_month - timedelta(first_day_of_month.weekday())
    last_day_of_calendar = last_day_of_month + timedelta(7 - last_day_of_month.weekday())

    month_cal = []
    week = []
    week_headers = []

    i = 0
    day = first_day_of_calendar
    while day <= last_day_of_calendar:
        if i < 7:
            week_headers.append(day)
        cal_day = {}
        cal_day['day'] = day
        cal_day['event'] = False
        for event in event_list:
            if day == event.created_on.date():
                cal_day['event'] = True
                cal_day['link'] = event.get_day_url()
        if day.month == month:
            cal_day['in_month'] = True
        else:
            cal_day['in_month'] = False  
        week.append(cal_day)
        if day.weekday() == 6:
            month_cal.append(week)
            week = []
        i += 1
        day += timedelta(1)

    return {'calendar': month_cal, 'headers': week_headers}


"""
Example usage:
{% block calendar %}
{% month_navigation %}
{% month_cal %}
{% endblock calendar %}
"""
