from datetime import date
import math
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import resolve
from rest_framework import status
from constants import ADD_POST_LIMIT, READ_POST_LIMIT, STREAK_COUNT_FOR_BADGE
from .models import Badges, Blocks, LoginStreak, Notification, Post, PostsRead
from django.contrib import messages
from django.db.models import F
from django.utils import timezone

class PostSubmissionLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and (resolve(request.path_info).url_name == 'add_post' or resolve(request.path_info).url_name == 'add-post'):
            if self.has_blocked(request.user):
                if resolve(request.path_info).url_name == 'add-post':
                    return JsonResponse({'error': 'You are blocked from middleware'}, status=status.HTTP_403_FORBIDDEN)
                else:
                    messages.error(request, 'You are blocked')
                    return redirect('/blogs/')
            elif self.has_reached_submission_limit(request.user):
                if resolve(request.path_info).url_name == 'add-post':
                    return JsonResponse({'error': 'You have reached the limit of posts submission today'}, status=status.HTTP_403_FORBIDDEN)
                else:
                    messages.error(request, 'You have reached the limit of posts to submit today')
                    return redirect('/blogs/')
        response = self.get_response(request)
        return response

    def has_reached_submission_limit(self, user):
        today = date.today()
        check_count_posts_submitted = Post.objects.filter(author=user, created__date=today).count()
        return check_count_posts_submitted >= ADD_POST_LIMIT
    
    def has_blocked(self, user):
        check_blocking = Blocks.objects.filter(user = user)
        if check_blocking:
            return True
        return False
    
class PostReadLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and (resolve(request.path_info).url_name == 'get_post' or resolve(request.path_info).url_name == 'get-post'):
            today = date.today()
            print('pass')
            check_count_posts_read = PostsRead.objects.filter(user = request.user, read_at__date = today).count()
            print(check_count_posts_read)
            print(request.user)
            if check_count_posts_read > READ_POST_LIMIT:
                if resolve(request.path_info).url_name == 'get-post':
                    return JsonResponse({'error': 'You have reached the limit of posts to read today'}, status=status.HTTP_403_FORBIDDEN)
                else:
                    messages.error(request, 'You have reached the limit of posts to read today')
                    return redirect('/blogs/')
            slug = resolve(request.path_info).kwargs.get('slug')
            post = get_object_or_404(Post, slug=slug)
            read_post = PostsRead(user = request.user, post = post)
            read_post.save()
        response = self.get_response(request)
        return response
    
class LoginStreaksMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated and resolve(request.path_info).url_name == 'login':
            today = timezone.now().date()
            check_user_login_strike = LoginStreak.objects.get_or_create(user=request.user)
            if not check_user_login_strike[1]:
                time_between_logins = today - check_user_login_strike[0].last_login
                if time_between_logins.days == 1:
                    check_user_login_strike[0].streak_count = F('streak_count') + 1
                elif time_between_logins.days > 1:
                    if check_user_login_strike[0].streak_count >= STREAK_COUNT_FOR_BADGE:
                        num_weeks = check_user_login_strike[0].streak_count / STREAK_COUNT_FOR_BADGE
                        num_weeks = math.floor(num_weeks)
                        badge = Badges.objects.filter(user=request.user, type = 'login_streak')
                        if badge:
                            weeks_badge = int(badge[0].description.split()[0])
                            if num_weeks > weeks_badge:
                                badge[0].description = f'{num_weeks} weeks strike badge'
                                badge[0].save()
                                Notification.objects.create(user=request.user, message=f"You've got {num_weeks} weeks strike badge.")
                        else:
                            badge = Badges(user=request.user, description=f'{num_weeks} weeks streak badge', type='login_streak')
                            badge.save()
                            Notification.objects.create(user=request.user, message=f"You've got {num_weeks} weeks strike badge.")

                    check_user_login_strike[0].streak_count = 1
                check_user_login_strike[0].last_login = today
                check_user_login_strike[0].save()
        return response
