# coding: utf-8

from london.shortcuts import get_object_or_404
from london.templates import render_template
from london.http import HttpResponse

from london.apps.themes.registration import register_template
register_template("post_list", mirroring="post_list.html")
register_template("post_view", mirroring="post_view.html")
register_template("post_edit", mirroring="post_edit.html")

import os
from london.apps.ajax import site
site.register_scripts_dir('cms', os.path.join(os.path.dirname(__file__), 'scripts'))

from models import Post

@render_template('post_list')
def post_list(request):
    return {'posts': request.site['posts']}

@render_template('post_view')
def post_view(request, slug):
    post = get_object_or_404(request.site['posts'], slug=slug)
    return {'post': post}

@render_template('post_edit')
def post_edit(request, slug):
    post = get_object_or_404(request.site['posts'], slug=slug)
    return {'post': post}

def post_save_name(request, slug):
    post = get_object_or_404(request.site['posts'], slug=slug)
    post['name'] = request.POST['value']
    post.save()
    return HttpResponse(post['name'])

def post_save_text(request, slug):
    post = get_object_or_404(request.site['posts'], slug=slug)
    post['text'] = request.POST['value']
    post.save()
    return HttpResponse(post['text'])

