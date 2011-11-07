import os

from london.apps.themes.registration import register_template
register_template("post_list", mirroring="post_list.html")
register_template("post_view", mirroring="post_view.html")
register_template("post_edit", mirroring="post_edit.html")

from london.apps.ajax import site
site.register_scripts_dir('blog', os.path.join(
                    os.path.dirname(__file__), 'scripts'))

