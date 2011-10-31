# coding: utf-8

import os
from london.shortcuts import get_object_or_404
from london.templates import render_template
from london.http import HttpResponse, HttpResponseRedirect
from london.urls import reverse

from london.apps.themes.registration import register_template
register_template("post_list", mirroring="post_list.html")
register_template("post_view", mirroring="post_view.html")
register_template("post_edit", mirroring="post_edit.html")

from london.apps.ajax import site
site.register_scripts_dir('blog', os.path.join(
                    os.path.dirname(__file__), 'scripts'))

from london.apps.auth.authentication import login_required

from models import Post

@render_template('post_list')
def post_list(request):
    return {'posts': request.site['posts']}

@render_template('post_view')
def post_view(request, slug):
    post = get_object_or_404(request.site['posts'], slug=slug)
    return {'post': post}

@login_required
def post_save_name(request, slug):
    post = get_object_or_404(request.site['posts'], slug=slug)
    post['name'] = request.POST['value']
    post.save()
    return HttpResponse(post['name'])

@login_required
def post_get_markdown(request, slug):
    post = get_object_or_404(request.site['posts'], slug=slug)
    source = post['source'] if post['source'] is not None else ''
    return HttpResponse("")

@login_required
def post_save_text(request, slug):
    post = get_object_or_404(request.site['posts'], slug=slug)
    post['source'] = request.POST['value']
    post.save()
    return HttpResponse(post['text'])

@login_required
def post_create(request):
    if request.method == 'POST':
        post = Post(name=request.POST['name'], 
                    author=request.user, site=request.site)
        post.save()
        return HttpResponseRedirect(
                reverse("post_view", kwargs={'slug': post['slug']}))
    return HttpResponseRedirect(reverse("post_list"))

@login_required
def post_delete(request, slug):
    if request.method == 'POST':
        post = get_object_or_404(request.site['posts'], slug=slug)
        post.delete()
    return HttpResponseRedirect(reverse("post_list"))

