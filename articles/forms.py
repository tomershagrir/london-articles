from london import forms
from london.apps.admin.modules import BaseModuleForm
from articles.models import Post
from articles import signals
from images import ImagesWidget, add_image_field_to_sender_form

signals.post_form_initialize.connect(add_image_field_to_sender_form)

class PostForm(BaseModuleForm):

    class Meta:
        model = Post
        #readonly = ('date',)
        exclude = ('text',)

    def initialize(self):
        signals.post_form_initialize.send(sender=self)
