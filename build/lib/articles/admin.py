from london.apps import admin

from models import Post
from forms import PostForm

class ModulePost(admin.CrudModule):
    model = Post
    list_display = ('slug', 'name','date', 'text')
    readonly_fields = ('date', 'text')
    form = PostForm

class AppBlog(admin.AdminApplication):
    title = 'Blog'
    modules = (ModulePost,)
