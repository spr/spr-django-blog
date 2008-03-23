from django import template
import re
from datetime import datetime
from blog.models import Tag

register = template.Library()

@register.inclusion_tag('blog/list_tags.html')
def list_tags():
    tags = Tag.objects.all()
    return {'tags': tags}

@register.inclusion_tag('blog/entry.html')
def render_entry(entry):
    return {'entry': entry}

@register.inclusion_tag('blog/entry_abbv.html')
def render_abbv_entry(entry):
    return {'entry': entry}

@register.inclusion_tag('blog/comment_form.html')
def render_comment_form(entry, form):
    return {'e': entry, 'form': form}

@register.inclusion_tag('blog/comments.html')
def render_comments(entry):
    return {'entry': entry}

@register.filter
def lessthanxdays(value, arg):
    try:
        days = int(arg)
    except ValueError:
        return value
    diff = datetime.now() - value
    if diff.days <= days:
        return True
    else:
        return False

@register.filter
def morewordsthan_html(value, arg):
    try:
        length = int(arg)
    except ValueError:
        return value
    if not isinstance(value, basestring):
        value = str(value)
    if count_words_html(value) > length:
        return True
    else:
        return False

def count_words_html(string):
    # Set up regular expressions
    re_words = re.compile(r'&.*?;|<.*?>|([A-Za-z0-9][\w-]*)')
    # Count non-HTML words
    pos = 0
    words = 0
    while True:
        m = re_words.search(string, pos)
        if not m:
            # Checked through whole string
            break
        pos = m.end(0)
        if m.group(1):
            # It's an actual non-HTML word
            words += 1
            continue
    return words
