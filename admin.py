from django.contrib import admin
from blog.models import Entry, Comment, Tag

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

