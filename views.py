from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic import list_detail
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from calendar import month_abbr
from django.conf import settings
from blog.models import Entry, Tag, Comment
from blog.forms import CommentForm
from blog.comment_filters import akismet
from django.core.mail import send_mail
import datetime
import time

def entry_detail(request, year, month, day, slug, draft=False):
    date = datetime.date(*time.strptime(year+month+day, '%Y'+'%b'+'%d')[:3])
    entry = get_object_or_404(Entry, slug=slug,
            created_on__range=(
                datetime.datetime.combine(date, datetime.time.min),
                datetime.datetime.combine(date, datetime.time.max)
            ), is_draft=draft)

    if request.method == 'POST' and entry.comments_allowed():
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment(**form.cleaned_data)
            comment.entry = entry
            if request.META['REMOTE_ADDR'] != '':
                comment.ip = request.META['REMOTE_ADDR']
            else:
                comment.ip = request.META['REMOTE_HOST']
            comment.date = datetime.datetime.now()
            comment.karma = 0
            comment.spam = akismet(request, comment)
            comment.save()
            if (not comment.spam) and settings.BLOG_COMMENT_EMAIL:
                comment_email = "%s\n--\n%s\n%s\n%s" % (comment.comment,
                        comment.name, comment.email, comment.website)
                send_mail('[Blog] %s' % entry.title, comment_email,
                        comment.email, [entry.author.email], fail_silently=True)
            return HttpResponseRedirect(entry.get_absolute_url())
    else:
        form = CommentForm()

    return render_to_response('blog/entry_detail.html',
            {'blog_title': settings.BLOG_TITLE, 'tags': Tag.objects.all(),
                'object': entry, 'comment_form': form},
                context_instance=RequestContext(request))

def tag_list(request, **kwargs):
    try:
        dict = {'queryset': Entry.objects.filter(tags__name=kwargs['tag'], is_draft=False).order_by('-created_on'),
                'paginate_by': 5, 'template_object_name': 'entry',
                'template_name': 'blog/tag_list.html',
                'extra_context': {'blog_title': settings.BLOG_TITLE,
                    'thetag': Tag.objects.get(name=kwargs['tag'])}}
    except Tag.DoesNotExist:
        raise Http404
    return list_detail.object_list(request, **dict)

def year_view(request, year, **kwargs):
    entries_months = []
    for month in xrange(1, 13):
        entries_months.append(
                (kwargs['queryset'].filter(created_on__year=year, 
                                      created_on__month=month),
                 datetime.datetime(year=int(year), month=month, day=1)))

    prior_year, next_year = (None, None)
    if len(kwargs['queryset'].filter(created_on__year=(int(year) - 1))) > 0:
        prior_year = unicode(int(year) - 1)
    if len(kwargs['queryset'].filter(created_on__year=(int(year) + 1))) > 0:
        next_year = unicode(int(year) + 1)

    return render_to_response('blog/entry_archive_year.html',
        {'blog_title': settings.BLOG_TITLE, 'tag': Tag.objects.all(),
            'entries_months': entries_months, 'year': year,
            'prior_year': prior_year, 'next_year': next_year},
            context_instance=RequestContext(request))
