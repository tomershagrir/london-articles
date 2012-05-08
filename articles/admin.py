from london.apps import admin

from models import Post
from forms import PostForm

class ModulePost(admin.CrudModule):
    model = Post
    list_display = ('slug', 'name','date', 'text')
    readonly_fields = ('date', 'text')
    form = PostForm

<<<<<<< HEAD
class AppArticles(admin.AdminApplication):
    title = 'Articles'
=======
class AppArticle(admin.AdminApplication):
    title = 'Article'
>>>>>>> 356a46dcdecfd115a0b8f95b61c69634b91ccbf8
    modules = (ModulePost,)

