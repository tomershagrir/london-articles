# coding: utf-8

import os
from london.shortcuts import get_object_or_404
from london.templates import render_template, render_to_response
from london.http import HttpResponse, HttpResponseRedirect, Http404
from london.urls import reverse
from london.utils.slugs import slugify
from london.apps.ajax.tags import redirect_to
from london.apps.sites.models import Site
from london.apps.auth.authentication import get_request
from london.apps.collections.models import Collection

try:
    from routes import register_for_routes
except ImportError:
    def register_for_routes(view):
        pass

from models import Post


def is_writer(user):
    return user and user.is_authenticated() and (user['is_superuser'] or (user['groups'] and user['groups'].filter(name="writers")))

def user_is_writer(func):
    def _inner(*args, **kwargs):
        request = get_request(*args, **kwargs)
        if not is_writer(request.user):
            return redirect_to(request, "/")
        return func(*args, **kwargs)
    return _inner

@register_for_routes('articles.views.list')
def list(request, template='post_list', site=None, queryset_function=None):
    if isinstance(site, basestring):
        site = Site.query().get(name=site)

    if not site:
        site = request.site

    if callable(queryset_function):
        posts = queryset_function(request)
    else:
        posts = site['posts']

    return render_to_response(request, template, {'posts':posts})

@register_for_routes('articles.views.view')
def view(request, slug, template="post_view", site=None, queryset_function=None, **kwargs):
    if isinstance(site, basestring):
        site = Site.query().get(name=site)

    if not site:
        site = request.site

    if callable(queryset_function):
        posts = queryset_function(request)
    else:
        posts = site['posts']

    collections = Collection.query()
    if 'slug2' in kwargs:
        items = []
        for item in Collection.query().filter(site=site, slug=kwargs['slug2']):
            items.extend(item['items'])
        collections = collections.filter(pk__in=items)
    if 'slug1' in kwargs:
        collection = get_object_or_404(collections, slug=kwargs['slug1'])
        posts = posts.filter(pk__in=collection['items'])
    post = get_object_or_404(posts, slug=slug)
    return render_to_response(request, template, {'post': post})

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
                reverse("articles_views_view", kwargs={'slug': post['slug']}))
    return HttpResponseRedirect(reverse("articles_views_list"))

@user_is_writer
def delete(request, slug):
    if request.method == 'POST':
        post = get_object_or_404(request.site['posts'], slug=slug)
        post.delete()
    return HttpResponseRedirect(reverse("articles_views_list"))

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
    return HttpResponseRedirect(reverse("articles_views_view", kwargs={'slug': post['slug']}))
