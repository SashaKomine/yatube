from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.cache import cache_page

from .utils import get_paginator
from .forms import CommentForm, PostForm
from .models import Group, Post, Comment, Follow


User = get_user_model()


@cache_page(20)
def index(request):
    title = 'Последние обновления на сайте'
    posts = Post.objects.select_related('group', 'author')
    page_obj = get_paginator(posts, request)
    context = {
        'page_obj': page_obj,
        'title': title,
        'posts': posts,
        'index': True}
    template_path = 'posts/index.html'
    return render(request, template_path, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = (
        group
        .posts
        .select_related('author'))
    description = group.description
    page_obj = get_paginator(posts, request)
    context = {
        'page_obj': page_obj,
        'description': description,
        'group': group}
    template_path = 'posts/group_list.html'
    return render(request, template_path, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = (
        author
        .posts
        .select_related('group'))
    page_obj = get_paginator(author_posts, request)
    template_path = 'posts/profile.html'
    context = {'author': author,
               'page_obj': page_obj}
    if request.user.is_authenticated:
        follow = Follow.objects.filter(author=author, user=request.user)
        following = follow.exists()
        context['following'] = following
    return render(request, template_path, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    template_path = 'posts/post_detail.html'
    form = CommentForm(request.POST or None)
    comments = Comment.objects.select_related('post')
    context = {'post': post,
               'form': form,
               'comments': comments}
    return render(request, template_path, context)


@login_required
def post_create(request):
    template_path = 'posts/create_post.html'
    title = 'Cоздание записи'
    form = PostForm(request.POST or None)
    if form.is_valid():
        user = request.user
        post = form.save(commit=False)
        post.author = user
        post.save()
        return redirect('posts:profile', request.user.username)
    else:
        context = {'title': title,
                   'form': form}
        return render(request, template_path, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    title = 'Редактировать запись'
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    template_path = 'posts/create_post.html'
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    else:
        context = {'title': title,
                   'is_edit': True,
                   'form': form,
                   'post': post}
        return render(request, template_path, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    title = 'Авторы, на которых вы подписаны'
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = get_paginator(posts, request)
    context = {
        'page_obj': page_obj,
        'title': title,
        'posts': posts,
        'follow': True}
    template_path = 'posts/follow.html'
    return render(request, template_path, context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.get_or_create(user=user, author=author)
    return redirect(reverse('posts:profile', args=[username]))


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect(reverse('posts:profile', args=[username]))
