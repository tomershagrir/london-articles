import re

from london.db import models
from london.utils.slugs import slugify
from london.apps.sites.models import Site
from london.apps.collections.models import Collection
from london.apps.auth.models import User
from london.utils.safestring import mark_safe
from london.urls import reverse

from datetime import datetime
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
        
    RENDER_TYPE_RAW = 'raw'
    RENDER_TYPE_MARKDOWN = 'markdown'
    RENDER_TYPE_CHOICES = (
            (RENDER_TYPE_RAW, 'Raw HTML'),
            (RENDER_TYPE_MARKDOWN, 'Markdown'),
            )

    name = models.CharField(max_length=255)
    author = models.ForeignKey('auth.User', blank=False, null=False, related_name='posts')
    slug = models.SlugField(max_length=255, blank=True, allow_slashes=True)
    source = models.TextField()
    markup = models.CharField(max_length=20, blank=True, choices=RENDER_TYPE_CHOICES, default=RENDER_TYPE_RAW)
    text = models.TextField()
    teaser = models.TextField()
    template_name = models.CharField(max_length=100, blank=True)
    is_draft = models.BooleanField(blank=True, null=False, default=True)
    date = models.DateTimeField(blank=True, default=datetime.now)    
    site = models.ForeignKey(Site, related_name='posts')
    
    def publish(self):
        self['is_draft'] = False
        self.save()

    def get_url(self):
        kwargs = {}
        collections = Collection.query().filter(site=self['site'], items__contains=str(self['pk']))
        if collections.count():
            kwargs = collections[0].get_slugs() # TODO: what to do if article belong to more than 1 collection?
        kwargs['slug'] = self['slug']
        
        try:
            from routes import dynamic_url_patterns
            url_patterns = dynamic_url_patterns[self['site']['name']] if self['site']['name'] in dynamic_url_patterns else []
        except ImportError:
            url_patterns = []
        
        try: 
            return reverse("articles_views_view", kwargs=kwargs, dynamic_url_patterns=url_patterns)
        except:
            return '/'+self['slug']

    def __unicode__(self):
        return self['name']

    def save(self, **kwargs):
        if not self.get('slug', False):
            self['slug'] = slugify(self['name'])

        source = self.get('source',  None)
        
        if self['markup'] == self.RENDER_TYPE_MARKDOWN:
            self['text'] = markdown2.markdown(source or '')
        else:
            self['text'] = source or ''
        
        return super(Post, self).save(**kwargs)

    def get_content(self):
        regex = re.compile("\{(IMAGE|COLLECTION|ALL):(.*?)\}")
        return mark_safe(regex.sub('', self['text']))
    
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