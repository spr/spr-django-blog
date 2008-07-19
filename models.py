from django.db import models
from django.contrib.auth.models import User
from django.db.models import permalink
from datetime import datetime
from django.core.urlresolvers import reverse

class Tag(models.Model):
    name = models.CharField(max_length=50)
    def __unicode__(self):
        return unicode(self.name)

    @permalink
    def get_absolute_url(self):
        return ('blog.urls.tag_list', (), {
            'tag': self.name})

    @permalink
    def get_rss_feed(self):
        return ('django.contrib.syndication.views.feed', (), {
            'url': '/'.join(('tag', self.name))})

class Entry(models.Model):
    author = models.ForeignKey(User)
    title = models.CharField(max_length=255)
    created_on = models.DateTimeField(default=datetime.now)
    last_updated = models.DateTimeField(editable=False)
    slug = models.SlugField(unique_for_date='created_on')
    content = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True, null=True)
    is_draft = models.BooleanField(default=False)
    def __unicode__(self):
        return unicode(self.title)
    def save(self):
        self.last_updated = datetime.now()
        super(Entry, self).save()

    def get_day_url(self):
        return reverse('entry_day', kwargs={
            'year': self.created_on.year,
            'month': self.created_on.strftime("%b").lower(),
            'day': self.created_on.strftime("%d")})

    @permalink
    def get_absolute_url(self):
        if not self.is_draft:
            return ('blog.views.entry_detail', (), {
                'year': self.created_on.year,
                'month': self.created_on.strftime("%b").lower(),
                'day': self.created_on.strftime("%d"),
                'slug': self.slug})
        else:
            return ('blog_draft_entry', (), {
                'year': self.created_on.year,
                'month': self.created_on.strftime("%b").lower(),
                'day': self.created_on.strftime("%d"),
                'slug': self.slug})

class Comment(models.Model):
    entry = models.ForeignKey(Entry, related_name='comments')
    name = models.CharField(max_length=50, verbose_name='name')
    email = models.EmailField(help_text='Required. Kept Private.')
    website = models.URLField(verify_exists=True, blank=True, null=True)
    ip = models.IPAddressField(blank=True, null=True)
    karma = models.SmallIntegerField(default=0)
    spam = models.BooleanField(default=True)
    date = models.DateTimeField(default=datetime.now)
    comment = models.TextField(help_text='<a href="http://daringfireball.net/projects/markdown/basics">Markdown syntax</a> allowed | (X)HTML tags stripped')
    def __unicode__(self):
        return unicode(self.name) + u" - " + unicode(self.date)
    class Admin:
        list_display = ('entry', 'name', 'email', 'website', 'spam')
        list_filter = ['spam', 'date']

from django.contrib import admin

admin.site.register(Tag)

class EntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_on', 'is_draft')
    list_filter = ['is_draft']
    prepopulated_fields = {'slug': ("title",)}

admin.site.register(Entry, EntryAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('entry', 'name', 'email', 'website', 'spam')
    list_filter = ['spam', 'date']

admin.site.register(Comment, CommentAdmin)
