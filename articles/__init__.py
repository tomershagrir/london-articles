import os

from london.apps.themes.registration import register_template
register_template("articles_base", mirroring="articles/base.html")
register_template("post_list", mirroring="articles/post_list.html")
register_template("post_view", mirroring="articles/post_view.html")
register_template("post_edit", mirroring="articles/post_edit.html")
register_template("author_view", mirroring="articles/author_view.html")
register_template("author_list", mirroring="articles/author_list.html")

from london.apps.ajax import site
site.register_scripts_dir('articles', os.path.join(
                    os.path.dirname(__file__), 'scripts'))

