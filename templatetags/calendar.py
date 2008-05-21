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
    """
    Produce the navigation links between months on the calendar.

    Defaults to today, and will generate the previous link. Optionally takes a ``datetime.date`` as for a month, a ``datetime.date`` for last month, and a ``datetime.date`` for next month.

    Example usage::

        <h2>Calendar</h2>
        <div class="box">
        {% month_navigation current previous next %}
        </div>

    Example output::

        <a href="/blog/2008/mar/">&lt;&lt;</a>
        <a href="/blog/2008/apr/">April</a>
        <a href="/blog/2008/may/">&gt;&gt;</a>
    """
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
    """
    Produce a table of dates for the current month, with links to entries.

    Defaults to this month's calendar. Optionally accepts a string of the year (``datetime.date.today().year``) and a string for the month (``datetime.date.today().month``).

    Example Usage::

        <h2>Calendar</h2>
        <div class="box>
        {% month_navigation previous_month next_month %}
        {% month_cal month.year month.month %}
        </div>

    Example output::

        <table>
        <tr>
        <th>Mo</th><th>Tu</th><th>We</th><th>Th</th><th>Fr</th><th>Sa</th><th>Su</th>
        </tr>
        <tr>
        <td style="color:gray;">28</td>
        <td style="color:gray;">29</td>
        <td style="color:gray;">30</td>
        <td><a href="/blog/2008/may/01/entry1/">1</a></td>
        <td>2</td>
        ...
    """
    event_list = Entry.objects.filter(created_on__year=year,
            created_on__month=month, is_draft=False)

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
