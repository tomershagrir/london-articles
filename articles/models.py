from london.db import models
from london.utils.slugs import slugify
from london.apps.sites.models import Site
from london.apps.auth.models import User
from london.utils.safestring import mark_safe
from london.urls import reverse

from datetime import datetime

import markdown2

SITES = [(slugify(site['name']), site['name']) for site in Site.query()]

class Category(models.Model):
    class Meta:
        ordering = ('name', )
    name = models.CharField(max_length=50)

class Post(models.Model):
    class Meta:
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
    date = models.DateTimeField(blank=True, null=False, default=datetime.now)    
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
        if source is not None:
            self['text'] = markdown2.markdown(source)

        return super(Post, self).save(**kwargs)

    def get_content(self):
        return mark_safe(self['text'])

class PostCategory(models.Model):
    post = models.ForeignKey(Post, related_name="categories")
    category = models.ForeignKey(Category, related_name="posts")
