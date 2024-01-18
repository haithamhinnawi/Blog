from datetime import date
from django.http import HttpResponse
from better_profanity import profanity
from API.chatgpt import ChatGPTClient
from constants import POSTS_PER_PAGE
from custom_errors import BlockedError
from .forms import CommentForm, PostForm
from django.shortcuts import get_object_or_404, redirect, render
from .models import Comment, DisLike, Like, Notification, Post, Subscription, UserBadgesTracker, Blocks
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.models import User

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('/blogs/')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def add_post(request):
    check_blocked = Blocks.objects.filter(user = request.user)
    if check_blocked:
        check_blocked = check_blocked.get(user = request.user)
    msg = ''
    if request.method == 'POST':
        form = PostForm(request.POST)
        if check_blocked and (check_blocked.blocked_until > timezone.now()):
            msg = f'You are blocked for {check_blocked.blocked_until - timezone.now()}'
        else:
            msg = ''
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                try:
                    post.save()
                except(BlockedError):
                    messages.warning(request, f"You got block.")
                except(PermissionError):
                    messages.warning(request, f"Cant add post, You have reached limit of add posts today.")
                return redirect('/blogs/') 
    else:
        form = PostForm()
    return render(request, 'blogs/add_post.html', {'form': form, 'msg': msg})

@login_required
def edit_post(request, slug):
    msg = ''
    post = get_object_or_404(Post, slug=slug, author=request.user)
    check_blocked = Blocks.objects.filter(user = request.user)
    if check_blocked:
        check_blocked = check_blocked.get(user = request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if check_blocked and (check_blocked.blocked_until > timezone.now()):
            msg = f'You are blocked for {check_blocked.blocked_until - timezone.now()}'
        else:
            msg = ''
            if form.is_valid():
                post = form.save(commit=False)
                post.updated = timezone.now()
                try:
                    post.save()
                except(ValueError):
                    messages.warning(request, f"You got block.")
                return redirect('/blogs/')
    else:
        form = PostForm(instance=post)
    return render(request, 'blogs/edit_post.html', {'form': form, 'post': post, 'msg': msg})

@login_required
def get_all_posts(request):
    '''
    This view to show all posts in the blog.
    '''
    all_posts = Post.get_published.all().order_by('-pub_date')
    notifications = Notification.objects.filter(user=request.user, created_at__date = date.today()).order_by('-created_at')
    top_post_contributors = UserBadgesTracker.objects.order_by('-posts_counter')[:3]
    top_likes_received_contributors = UserBadgesTracker.objects.order_by('-user_likes_counter')[:3]
    top_likes_given_contributors = UserBadgesTracker.objects.order_by('-user_posts_likes_counter')[:3]
    print(f'top post: {top_post_contributors}')
    paginator = Paginator(all_posts, POSTS_PER_PAGE)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    context = {
        'posts': posts,
        'notifications': notifications,
        'top_post_contributors': top_post_contributors,
        'top_likes_received_contributors': top_likes_received_contributors,
        'top_likes_given_contributors': top_likes_given_contributors,
    }
    return render(request, "blogs/get_all_posts.html", context)

@login_required
def get_post(request, slug):
    '''
    This view to show specific post in the blog.
    '''
    error_msg = ''
    post = get_object_or_404(Post, slug=slug)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.name = request.user.username
            comment.email = request.user.email
            body = form.cleaned_data['body']
            body = profanity.censor(body)
            error_msg = comment.save()
            if error_msg == '':
                return redirect('/blogs/' + str(post.slug))
    else:
        form = CommentForm()
    comments = Comment.objects.filter(active = True, post = post.pk)
    likes = Like.objects.filter(post = post, user = request.user)
    dislikes = DisLike.objects.filter(post = post, user = request.user)
    subscriptions = Subscription.objects.filter(subscriber=request.user, user_to_subscribe=post.author)
    not_my_post = True
    if post.author == request.user:
        not_my_post = False
    return render(request, "blogs/get_post.html", {"post": post, 'comments': comments, 'form': form, 'msg': error_msg, 'like': likes, 'dislike': dislikes, 'subscribe': subscriptions, 'not_my_post': not_my_post})

@login_required
def add_dislike(request, slug):
    '''
    This view to show all posts in the blog.
    '''
    post = get_object_or_404(Post, slug=slug)
    check_dislike = DisLike.objects.filter(user = request.user, post = post)
    if check_dislike:
        check_dislike.delete()
    else:
        check_like = Like.objects.filter(user = request.user, post = post)
        if check_like:
            check_like.delete()
        dislike = DisLike(user = request.user, post = post)
        dislike.save()
    return redirect('/blogs/' + str(post.slug))

@login_required
def add_like(request, slug):
    '''
    This view to show all posts in the blog.
    '''
    post = get_object_or_404(Post, slug=slug)
    check_like = Like.objects.filter(user = request.user, post = post)
    if check_like:
        check_like.delete()
    else:
        check_dislike = DisLike.objects.filter(user = request.user, post = post)
        if check_dislike:
            check_dislike.delete()
        like = Like(user = request.user, post = post)
        like.save()
    return redirect('/blogs/' + str(post.slug))

@login_required
def subscribe(request, pk, slug):
    '''
    This view to show all posts in the blog.
    '''
    user_to_subscribe = get_object_or_404(User, pk=pk)
    check_subscription = Subscription.objects.filter(subscriber = request.user, user_to_subscribe = user_to_subscribe)
    if check_subscription:
        check_subscription.delete()
    else:
        subscribe = Subscription(subscriber = request.user, user_to_subscribe = user_to_subscribe)
        subscribe.save()
    return redirect(f'/blogs/{slug}')

@login_required
def create_post_by_chatgpt(request):
    title = request.GET.get('title', '')
    answer = ChatGPTClient.connect(f'Create Blog post about {title} with title and body')
    print(answer)
    split1 = answer.split('Title:')
    title = split1[1].split('Body:')[0]
    split2 = answer.split('Body:')
    body = split2[1]
    try:
        post = Post(title = title, body = body, status = 'published', author = request.user)
        post.save()
    except BlockedError:
        messages.error(request, f"You got block.")
    except PermissionError:
        messages.error(request, f"Cant add post, You have reached limit of add posts today.")
    return redirect('/blogs/') 

@login_required
def summarize_post_by_chatgpt(request, slug):
    post = Post.get_published.filter(slug = slug)
    summary = ChatGPTClient.connect(f'Summarize this post: {post[0].body}')
    return HttpResponse(summary)

@login_required
def fix_post_grammar_by_chatgpt(request, slug):
    post = get_object_or_404(Post, slug = slug)
    grammar_fixed = ChatGPTClient.connect(f'Fix Grammar for "{post.body}"')
    print(grammar_fixed)
    return HttpResponse(grammar_fixed)
