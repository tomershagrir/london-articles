from london.apps import admin

from models import Post

class ModulePost(admin.CrudModule):
    model = Post
    list_display = ('slug', 'name','date', 'text')

class AppBlog(admin.AdminApplication):
    title = 'Blog'
    modules = (ModulePost,)

