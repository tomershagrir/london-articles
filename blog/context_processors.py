from london.apps.sites.models import Site

from blog.views import is_writer 

def basic(request):
    return {'writer': is_writer(request.user),
            'sites': Site.query().filter(is_active=True)}

