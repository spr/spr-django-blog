from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic import list_detail
from django.template import RequestContext
from django.newforms import form_for_model
from django.http import HttpResponseRedirect, Http404
from datetime import datetime
from calendar import month_abbr
from django.conf import settings
from blog.models import Entry, Tag, Comment
from blog.comment_filters import akismet

def entry_detail(request, year, month, day, slug, draft=False):
    entry = get_object_or_404(Entry, slug=slug, created_on__year=year,
            created_on__month=list(month_abbr).index(month.title()),
                created_on__day=day, is_draft=draft)
    CommentForm = form_for_model(Comment,
            fields=('name', 'email', 'website', 'comment'))
    diff = datetime.now() - entry.created_on

    if request.method == 'POST' and diff.days <= 10:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment(**form.cleaned_data)
            comment.entry = entry
            if request.META['REMOTE_ADDR'] != '':
                comment.ip = request.META['REMOTE_ADDR']
            else:
                comment.ip = request.META['REMOTE_HOST']
            comment.date = datetime.now()
            comment.karma = 0
            comment.spam = akismet(request, comment)
            comment.save()
            return HttpResponseRedirect(entry.get_absolute_url())
    else:
        form = CommentForm()

    return render_to_response('blog/entry_detail.html',
            {'blog_title': settings.BLOG_TITLE, 'tags': Tag.objects.all(),
                'object': entry, 'comment_form': form},
                context_instance=RequestContext(request))

def tag_list(request, **kwargs):
    try:
        dict = {'queryset': Entry.objects.filter(tags__name=kwargs['tag']).order_by('-created_on'),
                'paginate_by': 5, 'template_object_name': 'entry',
                'template_name': 'blog/tag_list.html',
                'extra_context': {'blog_title': settings.BLOG_TITLE,
                    'thetag': Tag.objects.get(name=kwargs['tag'])}}
    except Tag.DoesNotExist:
        raise Http404
    return list_detail.object_list(request, **dict)
