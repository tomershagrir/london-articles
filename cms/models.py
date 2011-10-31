from london.db import models
from london.utils.slugs import slugify
from london.apps.sites.models import Site
from london.apps.auth.models import User
from london.utils.safestring import mark_safe

from datetime import datetime

class Post(models.Model):
    class Meta:
        ordering = ('date',) 
    name = models.CharField(max_length=255)
    author = models.ForeignKey('auth.User', blank=False, null=False)
    slug = models.SlugField(max_length=255, blank=False, null=False)
    text = models.TextField()
    date = models.DateTimeField(blank=False, null=False)
    site = models.ForeignKey(Site, related_name='posts')

    def __unicode__(self):
        return self['name']

    def save(self, **kwargs):
        # TODO: slug field should be unique with site/blog
        # default values for slug and date
        if not self.get('slug', False):
            self['slug'] = slugify(self['name'])

        if self.get('date', None) is None:
            self['date'] = datetime.now()

        return super(Post, self).save(**kwargs)

    def get_content(self):
        return mark_safe(self['text'])

