# coding: utf-8

import os
from london.shortcuts import get_object_or_404
from london.templates import render_template, render_to_response
from london.http import HttpResponse, HttpResponseRedirect
from london.urls import reverse
from london.apps.sites.models import Site

from london.apps.themes.registration import register_template
register_template("post_list", mirroring="post_list.html")
register_template("post_view", mirroring="post_view.html")
register_template("post_edit", mirroring="post_edit.html")

from london.apps.ajax import site
site.register_scripts_dir('blog', os.path.join(
                    os.path.dirname(__file__), 'scripts'))

from london.apps.auth.authentication import login_required

from models import Post, Category

def post_list(request, template='post_list', site=None):
    if isinstance(site, basestring):
        site = Site.query().get(name=site)

    if not site:
        site = request.site

    posts = site['posts']
    if not request.user.is_authenticated():
        posts = posts.filter(is_draft=False)

    return render_to_response(request, template, {'posts': posts})

@render_template('post_view')
def post_view(request, slug):
    post = get_object_or_404(request.site['posts'], slug=slug)
    return {'post': post, 'categories': post.get_categories()}

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
    return HttpResponse(source)

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

@login_required
def post_publish(request, slug):
    if request.method == 'POST':
        post = get_object_or_404(request.site['posts'], slug=slug)
        action = request.POST['action']
        if action == 'publish':
            post['is_draft'] = False
        elif action == 'unpublish':
            post['is_draft'] = True
        post.save()
    return HttpResponseRedirect(reverse("post_view", kwargs={'slug': post['slug']}))

@login_required
def save_categories(request, slug):
    if request.method == 'POST':
        post = get_object_or_404(request.site['posts'], slug=slug)
        categories = request.POST['value']
        post['categories'].delete()
        for category in categories.split(","):
            category,created = Category.query().get_or_create(name=category.strip().lower())
            post['categories'].get_or_create(category=category)
    return HttpResponse(post.get_categories())
