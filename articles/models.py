from london.db import models
from london.utils.slugs import slugify
from london.apps.sites.models import Site
from london.apps.auth.models import User
from london.utils.safestring import mark_safe
from london.urls import reverse

from datetime import datetime

try:
    from images.render import ImagesRender
    image_compiler = ImagesRender()
except:
    image_compiler = None

import markdown2

#SITES = [(slugify(site['name']), site['name']) for site in Site.query()]

class Post(models.Model):
    class Meta:
        ordering = ('-date', )
        unique_together = (('slug','site'),)

    name = models.CharField(max_length=255)
    author = models.ForeignKey('auth.User', blank=False, null=False)
    slug = models.SlugField(max_length=255, blank=True)
    source = models.TextField()
    text = models.TextField()
    teaser = models.TextField()
    is_draft = models.BooleanField(blank=True, null=False, default=True)
    date = models.DateTimeField(blank=True, default=datetime.now)    
    site = models.ForeignKey(Site, related_name='posts')

    def get_url(self):
        return reverse("post_view", kwargs={'slug': self['slug']})

    def __unicode__(self):
        return self['name']

    def save(self, **kwargs):
        if not self.get('slug', False):
            self['slug'] = slugify(self['name'])

        source = self.get('source',  None)
        source = image_compiler.render(source) or source
        if source is not None:
            self['text'] = markdown2.markdown(source)

        return super(Post, self).save(**kwargs)

    def get_content(self):
        return mark_safe(self['text'])
    
    def get_teaser(self):
        return mark_safe(self['teaser'] or '')

    def get_previous_post(self):
        if not hasattr(self, '_previous_post'):
            posts = Post.query().filter(site=self['site'], is_draft=False, date__lt=self['date']).order_by('date')
            try:
                self._previous_post = posts[0]
            except IndexError:
                self._previous_post = None

        return self._previous_post

    def get_next_post(self):
        if not hasattr(self, '_next_post'):
            posts = Post.query().filter(site=self['site'], is_draft=False, date__gt=self['date']).order_by('-date')
            try:
                self._next_post = posts[0]
            except IndexError:
                self._next_post = None

        return self._next_post