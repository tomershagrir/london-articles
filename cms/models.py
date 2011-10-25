from london.db import models
from london.utils.slugs import slugify
from london.apps.sites.models import Site
from london.apps.auth.models import User

from datetime import datetime

class Post(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=False, null=False, unique=True)
    text = models.TextField()
    date = models.DateTimeField(blank=False, null=False)
    site = models.ForeignKey(Site, related_name='posts')

    def save(self, **kwargs):
        # default values for slug and date
        if self.get('slug', '') == '':
            self['slug'] = slugify(self['name'])

        if self.get('date', None) is None:
            self['date'] = datetime.now()

        return super(Post, self).save(**kwargs)


