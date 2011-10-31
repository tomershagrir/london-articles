from london.db import models
from london.utils.slugs import slugify
from london.apps.sites.models import Site
from london.apps.auth.models import User

from datetime import datetime

import markdown2

class Category(models.Model):
    class Meta:
        ordering = ('name',)
    name = models.CharField(max_length=50)


class Post(models.Model):
    class Meta:
        ordering = ('date',) 
    name = models.CharField(max_length=255)
    author = models.ForeignKey('auth.User', blank=False, null=False)
    slug = models.SlugField(max_length=255, blank=False, null=False)
    text = models.TextField()
    is_draft = models.BooleanField(default=True, blank=False, null=False)
    source = models.TextField()
    date = models.DateTimeField(blank=False, null=False)
    site = models.ForeignKey(Site, related_name='posts')
    
    def get_categories(self):
        return ",".join(pc['category']['name'] for pc in self['categories'])

    def save(self, **kwargs):
        # TODO: slug field should be unique with site/blog
        # default values for slug and date
        if not self.get('slug', False):
            self['slug'] = slugify(self['name'])

        if self.get('date', None) is None:
            self['date'] = datetime.now()

        if self.get('is_draft', None) is None:
            self['is_draft'] = True

        source = self.get('source',  None)
        if source is not None:
            self['text'] = markdown2.markdown(source)
        return super(Post, self).save(**kwargs)

class PostCategory(models.Model):
    post = models.ForeignKey(Post, related_name="categories")
    category = models.ForeignKey(Category, related_name="posts")

