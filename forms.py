from django.forms import ModelForm
from blog.models import Entry, Tag, Comment

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields=('name', 'email', 'website', 'comment')

