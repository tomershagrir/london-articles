from london.db import models
from london.utils.slugs import slugify
from london.apps.sites.models import Site
from london.apps.collections.models import Collection
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


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_draft=False)

class Post(models.Model):
    class Meta:
        query = 'articles.models.PostQuerySet'
        ordering = ('-date', )
        unique_together = (('slug','site'),)
        verbose_name_plural = 'Articles'
        verbose_name = 'Article'

    name = models.CharField(max_length=255)
    author = models.ForeignKey('auth.User', blank=False, null=False, related_name='posts')
    slug = models.SlugField(max_length=255, blank=True, allow_slashes=True)
    source = models.TextField()
    text = models.TextField()
    teaser = models.TextField()
    is_draft = models.BooleanField(blank=True, null=False, default=True)
    date = models.DateTimeField(blank=True, default=datetime.now)    
    site = models.ForeignKey(Site, related_name='posts')
    
    def publish(self):
        self['is_draft'] = False
        self.save()

    def get_url(self):
        kwargs={'slug': self['slug']}
        collections = Collection.query().filter(site=self['site'], items__contains=str(self['pk']))
        if collections.count():
            kwargs['collection'] = collections[0].get_slug() # TODO: what to do if article belong to more than 1 collection?
        else:
            kwargs['collection'] = 'cant-find' # TODO: shouldn't be empty, but need find better way to fill it
        try: 
            return reverse("articles_views_view", kwargs=kwargs)
        except:
            return self['slug']

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