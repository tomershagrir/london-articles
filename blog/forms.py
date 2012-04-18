from london import forms
from blog.models import Post
from blog import signals

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        readonly = ('date', 'text')

    def initialize(self):
        signals.post_form_initialize.send(sender=self)