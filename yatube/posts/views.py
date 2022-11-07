from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Group, Post, Comment, Follow
from .utils import paginate_page

from django.views.decorators.cache import cache_page

@cache_page(20)
def index(request):
    page_obj = paginate_page(request, Post.objects.all())
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    page_obj = paginate_page(request, group.posts.all())
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context=context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    page_obj = paginate_page(request, author.posts.all())
    print (Follow.objects.filter(
        user=request.user, author=User.objects.get(username=username)
    ).count())
    if Follow.objects.filter(
        user=request.user, author=User.objects.get(username=username)
    ).count() > 0:
        following = True
    else:
        following = False
    print (following)
    context = {
        'following': following,
        'author': author,
        'page_obj': page_obj,
    }
    print (context)
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post_id)
    comment_form = CommentForm()
    context = {
        'post': post,
        'comments': comments,
        'form': comment_form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user.username)
    context = {
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return redirect('posts:post_detail', post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        post.save()
        return redirect('posts:post_detail', post_id)

    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id
    }

    return render(request, 'posts/create_post.html', context)


def self_profile(request):
    return redirect('posts:profile', request.user.username)

@login_required
def add_comment(request, post_id):
    post = Post.objects.get(id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)

@login_required
def follow_index(request):
    page_obj = paginate_page(
        request, Post.objects.filter(author__following__user=request.user)
    )
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context=context)

@login_required
def profile_follow(request, username):
    Follow.objects.create(
        author=User.objects.get(username=username),
        user=request.user,
    )
    return redirect('posts:follow_index')

@login_required
def profile_unfollow(request, username):
    follow = Follow.objects.get(
        user=request.user, author=User.objects.get(username=username)
    )
    follow.delete()
    return redirect('posts:follow_index')