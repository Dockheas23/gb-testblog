from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from google.appengine.api import users
from blog.models import *
from blog.forms import PostForm

#
# Decorators
#
def _login_redirect(func):
    '''Checks to ensure that the user is logged in. Will redirect to the login
    page if not'''
    def _decorated(request, *args, **kwargs):
        if not users.get_current_user():
            return redirect(users.create_login_url(request.path))
        return func(request, *args, **kwargs)
    return _decorated

def _poster_or_admin_required(func):
    '''Checks that the current user is either the original poster, or an
    administrator. Returns a 403 Forbidden otherwise'''
    def _decorated(request, post_id, *args, **kwargs):
        blog_post = BlogPost.get_by_id(int(post_id))
        user = users.get_current_user()
        if users.is_current_user_admin() or (user and
                user == blog_post.author):
            return func(request, post_id, *args, **kwargs)
        else:
            return render(request, 'forbidden.html', {
                'auth_string': _get_auth_string('/view/' + post_id),
                'referer': '/view/' + post_id,
                }, status=403)
    return _decorated

def _commenter_or_admin_required(func):
    '''Checks that the current user is either the original commenter, or an
    administrator. Returns a 403 Forbidden otherwise'''
    def _decorated(request, post_id, comment_id, *args, **kwargs):
        blog_post = BlogPost.get_by_id(int(post_id))
        comment = Comment.get_by_id(int(comment_id), blog_post)
        user = users.get_current_user()
        if users.is_current_user_admin() or (user and user == comment.author):
            return func(request, post_id, comment_id, *args, **kwargs)
        else:
            return render(request, 'forbidden.html', {
                'auth_string': _get_auth_string('/view/' + post_id),
                'referer': '/view/' + post_id,
                }, status=403)
    return _decorated

#
# Views
#
def home(request):
    return render(request, 'home.html', {
        'posts': BlogPost.get_last(3),
        'auth_string': _get_auth_string(request.path),
        })

def all_posts(request):
    return render(request, 'all_posts.html', {
        'posts': BlogPost.get_all(),
        'auth_string': _get_auth_string(request.path),
        })

def view_post(request, post_id):
    form = PostForm()
    blog_post = BlogPost.get_by_id(int(post_id))
    if request.method == 'POST':
        submitted_form = PostForm(request.POST)
        if submitted_form.is_valid():
            title = submitted_form.cleaned_data['title']
            body = submitted_form.cleaned_data['body']
            comment = Comment(title=title, body=body,
                    parent=blog_post)
            comment.put()
            return redirect(request.path)
        else:
            form = submitted_form
    comments = Comment.all()
    comments.ancestor(blog_post.key())
    comments.order('-created')
    return render(request, 'post_detail.html', {
        'post': blog_post,
        'comments': comments,
        'form': form,
        'auth_string': _get_auth_string(request.path),
        'current_user': users.get_current_user(),
        'is_admin': users.is_current_user_admin(),
        })

@_login_redirect
def add_post(request):
    form = PostForm()
    if request.method == 'POST':
        submitted_form = PostForm(request.POST)
        if submitted_form.is_valid():
            title = submitted_form.cleaned_data['title']
            body = submitted_form.cleaned_data['body']
            post = BlogPost(title=title, body=body)
            post.put()
            return redirect('/')
        else:
            form = submitted_form

    return render(request, 'post_form.html', {
        'form': form,
        'auth_string': _get_auth_string('/'),
        })

@_login_redirect
@_poster_or_admin_required
def edit_post(request, post_id):
    blog_post = BlogPost.get_by_id(int(post_id))
    form = PostForm({'title': blog_post.title,
        'body': blog_post.body})
    if request.method == 'POST':
        submitted_form = PostForm(request.POST)
        if submitted_form.is_valid():
            title = submitted_form.cleaned_data['title']
            body = submitted_form.cleaned_data['body']
            blog_post.title = title
            blog_post.body = body
            blog_post.put()
            return redirect('/view/' + post_id)
        else:
            form = submitted_form
    return render(request, 'edit_post.html', {
        'form': form,
        'auth_string': _get_auth_string('/view/' + post_id),
        })

@_poster_or_admin_required
def delete_post(request, post_id):
    blog_post = BlogPost.get_by_id(int(post_id))
    blog_post.delete()
    return redirect('/')

@require_POST
def add_comment(request, post_id):
    blog_post = BlogPost.get_by_id(int(post_id))
    submitted_form = PostForm(request.POST)
    if not submitted_form.is_valid():
        raise Http404
    title = submitted_form.cleaned_data['title']
    body = submitted_form.cleaned_data['body']
    comment = Comment(title=title, body=body, parent=blog_post)
    comment.put()
    if request.is_ajax():
        return render(request, 'comment.html', {
            'post': blog_post,
            'comment': comment,
            'current_user': users.get_current_user(),
            'is_admin': users.is_current_user_admin(),
            })
    return redirect('/view/' + post_id)

@_commenter_or_admin_required
def delete_comment(request, post_id, comment_id):
    blog_post = BlogPost.get_by_id(int(post_id))
    comment = Comment.get_by_id(int(comment_id), blog_post)
    if not comment:
        raise Http404
    comment.delete()
    if request.is_ajax():
        return HttpResponse(comment_id)
    return redirect('/view/' + post_id)

#
# Helper functions
#
def _get_auth_string(path):
    '''Returns a greeting string with a link to either login or logout,
    depending on the current login state of the user'''
    user = users.get_current_user()
    if user:
        auth_string = 'Welcome, {0}! <a href="{1}">Logout</a>.'.format(
                user.nickname(), users.create_logout_url(path))
    else:
        auth_string = 'Not logged in, <a href="{0}">Login</a>.'.format(
                users.create_login_url(path))
    return auth_string
