
from london.urls.defining import patterns

urls = patterns('cms.views',
        (r'^$', 'post_list', {}, "post_list"),
        (r'^create-post/$', 'post_create', {}, "post_create"),
        (r'^(?P<slug>[\w-]+)/$', 'post_view', {}, "post_view"),
        (r'^(?P<slug>[\w-]+)/save-name/$', 'post_save_name', {}, "post_save_name"),
        (r'^(?P<slug>[\w-]+)/save-text/$', 'post_save_text', {}, "post_save_text"),
        (r'^(?P<slug>[\w-]+)/save-text/$', 'post_save_text', {}, "post_save_text"),
        (r'^(?P<slug>[\w-]+)/delete/$', 'post_delete', {}, "post_delete"),
)
