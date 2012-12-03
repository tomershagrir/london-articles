# coding: utf-8

import os
from london.shortcuts import get_object_or_404
from london.templates import render_template, render_to_response
from london.http import HttpResponse, HttpResponseRedirect, Http404
from london.exceptions import MultipleObjectsReturned
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
    
try:
    from userprofiles.models import UserProfile
except ImportError:
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
def list(request, template='post_list', site=None, queryset_function=None, **kwargs):
    if isinstance(site, basestring):
        site = Site.query().get(name=site)

    if not site:
        site = request.site

    if callable(queryset_function):
        posts = queryset_function(request)
    else:
        posts = site['posts']
        
    breadcrumbs = []
    collections = Collection.query()
    if 'slug2' in kwargs:
        items = []
        excluding_pks = []
        for pk_items in collections.values_list('items', flat=True):
            excluding_pks.extend(pk_items)
        for item in Collection.query().filter(site=site, slug=kwargs['slug2'], pk__notin=excluding_pks):
            collection = item
            items.extend(item['items'])
        collections = collections.filter(pk__in=items)
        breadcrumbs.append((collection['title'] or collection['name'], collection.get_url()))
    if 'slug1' in kwargs:
        collection = get_object_or_404(collections, slug=kwargs['slug1'].lower())
        breadcrumbs.append((collection['title'] or collection['name'], collection.get_url()))
        posts = posts.filter(pk__in=collection['items'])
    if request.breadcrumbs:
        request.breadcrumbs(breadcrumbs)
    return render_to_response(request, template, {'posts':posts, 'category':collection or None})

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
    breadcrumbs = []
    if 'slug2' in kwargs:
        items = []
        excluding_pks = []
        for pk_items in collections.values_list('items', flat=True):
            excluding_pks.extend(pk_items)
        for item in Collection.query().filter(site=site, slug=kwargs['slug2'], pk__notin=excluding_pks):
            collection = item
            items.extend(item['items'])
        breadcrumbs.append((collection['title'] or collection['name'], collection.get_url()))
        collections = collections.filter(pk__in=items)
    if 'slug1' in kwargs:
        collection = get_object_or_404(collections, slug=kwargs['slug1'].lower())
        breadcrumbs.append((collection['title'] or collection['name'], collection.get_url()))
        posts = posts.filter(pk__in=collection['items'])
    post = get_object_or_404(posts, slug=slug)
    breadcrumbs.append((post['name'], post.get_url()))
    request.breadcrumbs(breadcrumbs)
    return render_to_response(request, template, {'post': post})

@register_for_routes('articles.views.author_view')
def author_view(request, slug):
    if not UserProfile:
        return Http404
    parts = map(lambda x: x.capitalize(), slug.split('-'))
    firstname = parts[0]
    lastname = parts[1] if len(parts) > 1 else ''
    try:
        author = get_object_or_404(UserProfile, firstname=firstname, lastname=lastname)
    except MultipleObjectsReturned:
        author = UserProfile.query().filter(firstname=firstname, lastname=lastname)[0]
    
    return render_to_response(request, 'author_view', {'author': author['user']})

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
