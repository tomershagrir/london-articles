from london.apps import admin

from models import Post
from forms import PostForm

class ModulePost(admin.CrudModule):
    model = Post
    list_display = ('slug','name','date',)
    readonly_fields = ('date','text')
    exclude = ('text',)
    form = PostForm
    search_fields = ('name',)

class AppArticles(admin.AdminApplication):
    title = 'Blog'
    modules = (ModulePost,)

