from london import forms
from london.apps.admin.modules import BaseModuleForm
from articles.models import Post
from articles import signals

from datetime import datetime

class PostForm(BaseModuleForm):

    class Meta:
        model = Post
        exclude = ('text',)

    def get_initial(self, initial=None):
        initial = initial or super(PostForm, self).get_initial(initial)
        signals.post_form_initialize.send(sender=self, initial=initial)
        return initial
    
    def save(self, commit=True, force_new=False):
        if bool(self.request.POST.get('save_as_new', 0)):
            self.cleaned_data['date'] = datetime.now()
        signals.post_form_pre_save.send(sender=self, instance=self.instance)
        obj = super(PostForm, self).save(commit, force_new)
        signals.post_form_post_save.send(sender=self, instance=obj)
        return obj