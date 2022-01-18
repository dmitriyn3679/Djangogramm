import json
from collections import namedtuple

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.core.paginator import Paginator
from django.urls import reverse
from django.http import JsonResponse

from rest_framework import viewsets
from rest_framework import permissions
from web.serializers import UserSerializer, PostSerializer

from web.models import Post, User, Media, Comment
from web.forms import SignUpForm, PostForm, MediaForm, CommentForm
from web.sql_queries import sql_follows, sql_posts, sql_media, sql_comments
from web.utils import exec_query





@login_required
def feed(request):
    rows = exec_query(sql_follows.format(request.user.id))
    follows = ', '.join([str(item[0]) for item in rows])



    posts = exec_query(sql_posts.format(follows))
    posts_ids = ', '.join([str(item[0]) for item in posts])
    media = exec_query(sql_media.format(posts_ids))
    comments = exec_query(sql_comments.format(posts_ids))

    sorted_posts = []
    post_item = namedtuple('Post', ('post', 'media', 'comments'))
    for post in posts:
        post_media = []
        for image in media:
            if image.post_id == post.id:
                post_media.append(image)
        post_comments = []
        for comment in comments:
            if comment.post_id == post.id:
                post_comments.append(comment)
        sorted_posts.append(post_item(post, post_media, post_comments))
    return render(request, 'web/feed.html', context={'posts': sorted_posts})


@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'web/profile.html', context={'user': user})


@login_required
def post(request, post_id):
    post_obj = get_object_or_404(Post, id=post_id)
    return render(request, 'web/post.html', context={'post': post_obj})


@login_required
def comment_create(request, post_id):
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.post = get_object_or_404(Post, id=post_id)
            comment.save()
            redirect_url = f"{reverse('web:post', kwargs={'post_id': post_id})}#comment_{comment.id}"
            return redirect(redirect_url)
    return redirect('web:post', post_id=post_id)


@login_required
def post_create(request):
    if request.method == 'POST':
        post_form = PostForm(request.POST)
        media_form = MediaForm(request.POST)
        if post_form.is_valid() or media_form.is_valid():
            post = post_form.save(commit=False)
            post.user = request.user
            post.save()
            media = request.FILES.getlist('media')
            for image in media:
                item = Media(media=image, post=post)
                item.save()
            return redirect('web:post', post_id=post.id)
    else:
        post_form = PostForm()
        media_form = MediaForm()
    return render(request, 'web/post_create.html', {'post_form': post_form, 'media_form': media_form})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm()
        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('web:feed')
    else:
        form = SignUpForm()
    return render(request, 'auth/signup.html', context={'form': form})


def like_handler(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequests'
    if is_ajax:
        if request.method == 'POST':
            data = json.load(request)
            payload = data.get('payload')
            if not payload:
                return JsonResponse({1: 1})
            action = payload.get('action')
            post_id = payload.get('post_id')
            if not (action or post_id):
                return JsonResponse({1: 1})
            post = get_object_or_404(Post, id=post_id)
            if action == 'liked':
                post.likes.add(request.user)
            elif action == 'unliked':
                post.likes.remove(request.user)
            else:
                return JsonResponse({1: 1})
            return JsonResponse({'payload': {
                'count': post.likes.count(),
                'post_id': post_id
            }})
    return JsonResponse({})





class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    #permission_classes = [permissions.IsAuthenticated]