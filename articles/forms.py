from london import forms
from articles.models import Post
from articles import signals

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        readonly = ('date', 'text')

    def get_initial(self, initial=None):
        initial = initial or super(PostForm, self).get_initial(initial)
        signals.post_form_initialize.send(sender=self, initial=initial)
        return initial
    
    def save(self, commit=True, force_new=False):
        signals.post_form_pre_save.send(sender=self, instance=self.instance)
        obj = super(PostForm, self).save(commit, force_new)
        signals.post_form_post_save.send(sender=self, instance=obj)
        return obj