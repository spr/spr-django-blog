from django.contrib.syndication.feeds import Feed
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from blog.models import Entry, Tag
from django.conf import settings

class RecentEntries(Feed):
    title = settings.BLOG_TITLE
    link = settings.BLOG_PATH
    description = "Recent Posts on " + title
    author_name = settings.BLOG_AUTHOR
    author_email = settings.BLOG_AUTHOR_EMAIL
    copyright = settings.BLOG_COPYRIGHT

    def items(self):
        return Entry.objects.filter(is_draft=False).order_by('-created_on')[:5]

    def categories(self):
        return [tag.name for tag in Tag.objects.all()]

    def item_pubdate(self, item):
        return item.created_on

    def item_categories(self, item):
        return [tag.name for tag in item.tags.all()]

class EntriesByTag(Feed):
    author_name = settings.BLOG_AUTHOR
    author_email = settings.BLOG_AUTHOR_EMAIL
    copyright = settings.BLOG_COPYRIGHT
    title_template = "feeds/latest_title.html"
    description_template = "feeds/latest_description.html"

    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return Tag.objects.get(name=bits[0])

    def items(self, obj):
        return Entry.objects.filter(tags__name=obj.name).order_by('-created_on')[:5]

    def title(self, obj):
        return "%s - Tag %s" % (settings.BLOG_TITLE, obj.name)

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return "Recent entries tagged with %s" % obj.name

    def item_pubdate(self, item):
        return item.created_on

    def categories(self, obj):
        return (obj.name,)
