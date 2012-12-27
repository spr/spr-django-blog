import datetime, time
from django.conf.urls.defaults import *
from django.views.generic import date_based, list_detail
from django.views.generic.simple import redirect_to
from django.contrib.syndication.views import feed
from django.contrib.auth.decorators import login_required
from django.http import Http404
from blog.models import Entry, Tag, Comment
from django.conf import settings
from blog.feeds import RecentEntries, EntriesByTag
from blog.views import entry_detail, tag_list, year_view

# Defining RSS Feeds
feed_dict = {
        'latest': RecentEntries,
        'tag': EntriesByTag
}

urlpatterns = patterns('',
        (r'^feeds/tag/$', list_detail.object_list, 
            {'queryset': Tag.objects.all(), 'template_name': 'blog/tags.html',
                'extra_context': {'blog_title': settings.BLOG_TITLE}}
            ),
        (r'^feeds/(?P<url>.*)/$', feed, {'feed_dict': feed_dict}),
)

# Entry Generic Views
entry_date = {'queryset': Entry.objects.filter(is_draft=False),
        'date_field': 'created_on',
        'allow_empty': True,
        'extra_context': {'blog_title': settings.BLOG_TITLE}}

if len(Entry.objects.all()) != 0:
    first_entry_date = Entry.objects.order_by('created_on')[0].created_on
else:
    first_entry_date = datetime.datetime.now()

def archive_month_wrapper(request, **kwargs):
    kwargs['allow_empty'] = True
    month = datetime.date(*time.strptime(kwargs['month'], '%b')[:3]).month
    if first_entry_date.year < int(kwargs['year']):
        return date_based.archive_month(request, **kwargs)
    if first_entry_date.month < month:
        return date_based.archive_month(request, **kwargs)
    if first_entry_date.month == month:
        kwargs['allow_empty'] = False
        return date_based.archive_month(request, **kwargs)
    raise Http404

urlpatterns += patterns('',
        (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\d{2})/(?P<slug>[\w-]+)/$',
            entry_detail),
        url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\d{2})/$',
            date_based.archive_day, entry_date, name="entry_day"),
        url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/$',
            archive_month_wrapper, entry_date, name="entry_month"),
        (r'^(?P<year>\d{4})/$',
            year_view, entry_date),
        (r'^draft/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\d{2})/(?P<slug>[\w-]+)/$',
            login_required(entry_detail), {'draft': True}, "blog_draft_entry"),
        (r'^$',
            date_based.archive_index, entry_date),
)

# Tag List View
urlpatterns += patterns('',
        (r'tags/(?P<tag>[\S ]+)/', tag_list),
)
