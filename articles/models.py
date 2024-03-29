from london.db import models
from london.utils.slugs import slugify
from london.apps.sites.models import Site
from london.apps.auth.models import User
from london.utils.safestring import mark_safe
from london.urls import reverse
from london.apps.collections.models import Collection

from datetime import datetime

try:
    from images.render import ImagesRender
    image_compiler = ImagesRender()
except:
    image_compiler = None

import markdown2

try:
    SITES = [(slugify(site['name']), site['name']) for site in Site.query()]
except:
    SITES = []

class Category(models.Model):
    class Meta:
        ordering = ('name', )
    name = models.CharField(max_length=50)

class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_draft=False)
    
    def by_collection(self, collection_name):
        try:
            collection = Collection.query().get(name = collection_name)
            items = collection['items']
        except Collection.DoesNotExist:
            items = []
        return self.filter(pk__in = items)
    
    def except_collection(self, collection_name):
        try:
            collection = Collection.query().get(name = collection_name)
            items = collection['items']
        except Collection.DoesNotExist:
            items = []
        return self.filter(pk__notin = items)
    

class Post(models.Model):
    class Meta:
        query = 'articles.models.PostQuerySet'
        ordering = ('-date', )
        permissions = tuple(
                ('can_post_to_%s' % site_name[0],
                 'User can post to site %s' % site_name[1])
                for site_name in SITES
            )

    name = models.CharField(max_length=255)
    author = models.ForeignKey('auth.User', blank=False, null=False)
    slug = models.SlugField(max_length=255, blank=True)
    source = models.TextField()
    text = models.TextField()
    teaser = models.TextField()
    is_draft = models.BooleanField(blank=True, null=False, default=True)
    created_date = models.DateTimeField(blank=True, null=False, default=datetime.now)    
    date = models.DateTimeField(blank=True, null=False, verbose_name='Updated Date')
    site = models.ForeignKey(Site, related_name='posts')

    def get_categories(self):
        return ",".join(pc['category']['name'] for pc in self['categories'])

    def get_url(self):
        return reverse("post_view", kwargs={'slug': self['slug']})

    def __unicode__(self):
        return self['name']

    def save(self, **kwargs):
        # TODO: slug field should be unique with site/articles
        if not self.get('slug', False):
            self['slug'] = slugify(self['name'])

        source = self.get('source',  None)
        source = image_compiler.render(source) or source
        if source is not None:
            self['text'] = markdown2.markdown(source)
        self['date'] = datetime.now()

        return super(Post, self).save(**kwargs)

    def get_content(self):
        return mark_safe(self['text'])
    
    def get_teaser(self):
        return mark_safe(self['teaser'])

    def get_previous_post(self, collection_name):
        if not hasattr(self, '_previous_post'):
            posts = Post.query().filter(site=self['site'], is_draft=False, created_date__lt=self['created_date']).order_by('-created_date').by_collection(collection_name)
            try:
                self._previous_post = posts[0]
            except IndexError:
                self._previous_post = None

        return self._previous_post

    def get_next_post(self, collection_name):
        if not hasattr(self, '_next_post'):
            posts = Post.query().filter(site=self['site'], is_draft=False, created_date__gt=self['created_date']).order_by('created_date').by_collection(collection_name)
            try:
                self._next_post = posts[0]
            except IndexError:
                self._next_post = None

        return self._next_post

class PostCategory(models.Model):
    post = models.ForeignKey(Post, related_name="categories")
    category = models.ForeignKey(Category, related_name="posts")
