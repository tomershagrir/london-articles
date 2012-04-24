from london import forms
from blog.models import Post
from blog import signals
from images import ImagesWidget, add_image_field_to_sender_form

signals.post_form_initialize.connect(add_image_field_to_sender_form)

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        readonly = ('date', 'text')

    def initialize(self):
        signals.post_form_initialize.send(sender=self)