from london.conf import settings

from blog.views import is_writer 

def basic(request):
    return {'writer': is_writer(request.user)}

