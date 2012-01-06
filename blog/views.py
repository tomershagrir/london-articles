# coding: utf-8

import os
from london.shortcuts import get_object_or_404
from london.templates import render_template, render_to_response
from london.http import HttpResponse, HttpResponseRedirect
from london.urls import reverse
from london.utils.slugs import slugify
from london.apps.ajax.tags import redirect_to

from london.apps.sites.models import Site

from london.apps.auth.authentication import get_request

from models import Post, Category

def is_writer(user):
    return user.is_authenticated() and (user['is_superuser'] or user['groups'].filter(name="writers"))

def user_is_writer(func):
    def _inner(*args, **kwargs):
        request = get_request(*args, **kwargs)
        if not is_writer(request.user):
            return redirect_to(request, "/")
        return func(*args, **kwargs)
    return _inner

def list(request, template='post_list', site=None, queryset_function=None):
    if isinstance(site, basestring):
        site = Site.query().get(name=site)

    if not site:
        site = request.site

    if callable(queryset_function):
        posts = queryset_function(request)
    else:
        posts = site['posts']

    print 'x'*10, (site['hostname'], posts.count(), request.user.is_authenticated(), [p for p in posts]) # XXX
    return render_to_response(request, template, {'posts':posts})

def view(request, slug, template="post_view"):
    post = get_object_or_404(request.site['posts'], slug=slug)
    return render_to_response(request, template, {'post': post, 
                            'categories': post.get_categories()})

@user_is_writer
def save_name(request, slug):
    post = get_object_or_404(request.site['posts'], slug=slug)
    post['name'] = request.POST['value']
    post.save()
    return HttpResponse(post['name'])

@user_is_writer
def get_markdown(request, slug):
    post = get_object_or_404(request.site['posts'], slug=slug)
    source = post['source'] if post['source'] is not None else ''
    return HttpResponse(source)

@user_is_writer
def save_text(request, slug):
    post = get_object_or_404(request.site['posts'], slug=slug)
    post['source'] = request.POST['value']
    post.save()
    return HttpResponse(post['text'])

@user_is_writer
def create(request):
    if request.method == 'POST':
        post = Post(name=request.POST['name'], 
                    author=request.user, site=request.site)
        post.save()
        return HttpResponseRedirect(
                reverse("post_view", kwargs={'slug': post['slug']}))
    return HttpResponseRedirect(reverse("post_list"))

@user_is_writer
def delete(request, slug):
    if request.method == 'POST':
        post = get_object_or_404(request.site['posts'], slug=slug)
        post.delete()
    return HttpResponseRedirect(reverse("post_list"))

@user_is_writer
def publish(request, slug):
    if request.method == 'POST':
        post = get_object_or_404(request.site['posts'], slug=slug)
        action = request.POST['action']
        if action == 'publish':
            post['is_draft'] = False
        elif action == 'unpublish':
            post['is_draft'] = True
        post.save()
    return HttpResponseRedirect(reverse("post_view", kwargs={'slug': post['slug']}))

@user_is_writer
def save_categories(request, slug):
    if request.method == 'POST':
        post = get_object_or_404(request.site['posts'], slug=slug)
        categories = request.POST['value']
        post['categories'].delete()
        for category in categories.split(","):
            category,created = Category.query().get_or_create(name=category.strip().lower())
            post['categories'].get_or_create(category=category)
    return HttpResponse(post.get_categories())
