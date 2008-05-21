from django.conf.urls.defaults import *
from django.views.generic import date_based, list_detail
from django.views.generic.simple import redirect_to
from django.contrib.syndication.views import feed
from django.contrib.auth.decorators import login_required
from django.http import Http404
from blog.models import Entry, Tag, Comment
from django.conf import settings
from blog.feeds import RecentEntries, EntriesByTag
from blog.views import entry_detail, tag_list

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
        'allow_empty': False,
        'extra_context': {'blog_title': settings.BLOG_TITLE}}

urlpatterns += patterns('',
        (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\d{2})/(?P<slug>[\w-]+)/$',
            entry_detail),
        url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\d{2})/$',
            date_based.archive_day, entry_date, name="entry_day"),
        url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/$',
            date_based.archive_month, entry_date, name="entry_month"),
        (r'^(?P<year>\d{4})/$',
            date_based.archive_year, entry_date),
        (r'^draft/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\d{2})/(?P<slug>[\w-]+)/$',
            login_required(entry_detail), {'draft': True}, "blog_draft_entry"),
        (r'^$',
            date_based.archive_index, entry_date),
)

# Tag List View
urlpatterns += patterns('',
        (r'tags/(?P<tag>[\S ]+)/', tag_list),
)
