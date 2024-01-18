from datetime import date
import math
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from better_profanity import profanity
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from constants import ADD_POST_LIMIT, BLOCK_DAYS_COUNT, TIME_BETWEEN_COMMENTS, WARNINGS_NUMBER_TO_GET_BLOCK
from custom_errors import BlockedError, ReachedLimitError
from .methods import unique_slug_generator, check_bad_words
from django.db.models import F, Case, When, IntegerField

def check_warnings(count, user):
    blocked_user = Blocks.objects.filter(user=user)
    if blocked_user and blocked_user[0].blocked_until > timezone.now():
        return True
    if count > 0:
        warning = Warnings.objects.filter(user=user)
        if warning:
            warning.update(bad_words_count=F('bad_words_count') + count)
            warning.update(warnings_count=Case(
                When(bad_words_count__gte=WARNINGS_NUMBER_TO_GET_BLOCK, then=F('warnings_count') + F('bad_words_count') / WARNINGS_NUMBER_TO_GET_BLOCK), default=F('warnings_count'), output_field=IntegerField()))
            warning.update(bad_words_count = Case(
                When(bad_words_count__gte=WARNINGS_NUMBER_TO_GET_BLOCK, then=F('bad_words_count') - ((F('bad_words_count')/WARNINGS_NUMBER_TO_GET_BLOCK)*WARNINGS_NUMBER_TO_GET_BLOCK)), default=F('bad_words_count'), output_field=IntegerField()))
            if warning[0].warnings_count >= WARNINGS_NUMBER_TO_GET_BLOCK:
                warning.update(warnings_count = F('warnings_count') - WARNINGS_NUMBER_TO_GET_BLOCK)
                blocked_user = Blocks.objects.filter(user=user)
                if blocked_user:
                    blocked_user.update(blocked_at = timezone.now(), blocked_until = timezone.now() + timezone.timedelta(days=BLOCK_DAYS_COUNT))
                else:
                    block = Blocks(user=user)
                    block.save()
        else:
            if count >= WARNINGS_NUMBER_TO_GET_BLOCK:
                warnings = int(count/WARNINGS_NUMBER_TO_GET_BLOCK)
                bad_words = count - warnings
                warning = Warnings(
                    user=user, bad_words_count=bad_words, warnings_count=warnings)
            else:
                warning = Warnings(
                    user=user, bad_words_count=count, warnings_count=0)
            warning.save()
    return False

class PostManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published')

class Post(models.Model):
    status_choice = [
        ('published', 'Published'),
        ('draft', 'Draft')
    ]
    title = models.CharField(max_length=200)
    body = models.TextField()
    pub_date = models.DateTimeField(
        'date published', default=None, null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    slug = models.SlugField(unique=True, null=True)
    created = models.DateTimeField('date created', auto_now_add = True)
    updated = models.DateTimeField('date updated', auto_now_add = True)
    status = models.CharField(choices=status_choice, max_length=15)
    
    objects = models.Manager()
    get_published = PostManager()

    def save(self, *args, **kwargs):
        today = date.today()
        check_count_posts = Post.objects.filter(author = self.author, created__date = today).count()
        if check_count_posts >= ADD_POST_LIMIT:
            raise ReachedLimitError('reached limit')
        if self.status == 'published' and not self.pub_date:
            self.pub_date = timezone.now()
        self.slug = unique_slug_generator(self, slugify(self.title))
        count = check_bad_words(self.body)
        self.body = profanity.censor(self.body)
        check = check_warnings(count, self.author)
        self.updated = timezone.now()
        if not check:
            super().save(*args, **kwargs)
        else:
            raise BlockedError('You are blocked')

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(
        Post, related_name="comments", on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created_time = models.DateTimeField("Created", auto_now_add = True)
    updated_time = models.DateTimeField("Updated", auto_now_add = True)
    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        msg = ''
        self.body = profanity.censor(self.body)
        last_comment = Comment.objects.filter(
            post=self.post,
            email=self.email,
            created_time__lt=self.created_time
        ).order_by('-created_time').first()
        if last_comment:
            time_between_comments = self.created_time - last_comment.created_time
            if time_between_comments.seconds < TIME_BETWEEN_COMMENTS:
                msg = f'You need to wait {TIME_BETWEEN_COMMENTS} seconds between comment and the other, remaining '
                msg += str(TIME_BETWEEN_COMMENTS - time_between_comments.seconds) + 's'
                return msg
        super().save(*args, **kwargs)
        return msg

class Warnings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bad_words_count = models.PositiveIntegerField(default=0)
    warnings_count = models.PositiveIntegerField(default=0)

class Blocks(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    blocked_at = models.DateTimeField('Blocked at', auto_now_add = True)
    blocked_until = models.DateTimeField('Blocked until', default=(
        timezone.now() + timezone.timedelta(days=10)))
    
class PostsRead(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(
        Post, related_name="post_read", on_delete=models.CASCADE)
    read_at = models.DateTimeField('Read at', auto_now_add = True)

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

class DisLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

class Subscription(models.Model):
    subscriber = models.ForeignKey(User, related_name = 'subscriber', on_delete=models.CASCADE)
    user_to_subscribe = models.ForeignKey(User, related_name = 'user_to_subscribe', on_delete=models.CASCADE)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class Badges(models.Model):
    type_choices = [
        ('post', 'Post'),
        ('likes_did', 'Likes did'),
        ('likes_recieved', 'Likes recieved'),
        ('login_streak', 'Login streaks'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length = 50)
    type = models.CharField(max_length=25, choices=type_choices, default = 'post')

class UserBadgesTracker(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    posts_counter = models.PositiveIntegerField(default = 0)
    user_likes_counter = models.PositiveIntegerField(default = 0)
    user_posts_likes_counter = models.PositiveIntegerField(default = 0)

class LoginStreak(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    last_login = models.DateField(auto_now_add=True)
    streak_count = models.PositiveIntegerField(default = 1)

@receiver(post_save, sender=Post)
def create_notification(sender, instance, created, **kwargs):
    if created:
        subscribers = Subscription.objects.filter(user_to_subscribe=instance.author)
        for subscriber in subscribers:
            Notification.objects.create(user=subscriber.subscriber, message=f"{instance.author.username} has posted a new post.")

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

def update_counter(user, field_name, threshold, badge_suffix, message_suffix, badge_type):
    UserBadgesTracker.objects.filter(user=user).update(**{field_name: F(field_name) + 1})
    count = UserBadgesTracker.objects.get_or_create(user=user)[0].__getattribute__(field_name)
    print(count)
    condition = False
    if field_name == 'posts_counter':
        condition = math.log10(count).is_integer()
    else:
        condition = True if count % threshold == 0 else False
    if condition:
        badge_name = f'{count} {badge_suffix}'
        Badges.objects.update_or_create(user=user, description=badge_name, type = badge_type)
        Notification.objects.update_or_create(user=user, message=f"You've got {count} {message_suffix}.")
    print(f'Count {field_name} of {user} is: {count}, {badge_suffix}')

@receiver(post_save, sender=Post)
def increment_user_posts_count(sender, instance, created, **kwargs):
    if created:
        update_counter(instance.author, 'posts_counter', 10, 'Posts Badge', 'Posts Badge', 'post')

@receiver(post_delete, sender=Post)
def decrement_user_posts_count(sender, instance, **kwargs):
    UserBadgesTracker.objects.filter(user=instance.author).update(**{'posts_counter': F('posts_counter') - 1})

@receiver(post_save, sender=Like)
def increment_user_likes_counter(sender, instance, created, **kwargs):
    if created:
        update_counter(instance.user, 'user_likes_counter', 100, 'Likes did Badge', 'Likes did Badge', 'likes_did')

@receiver(post_delete, sender=Like)
def decrement_user_posts_count(sender, instance, **kwargs):
    UserBadgesTracker.objects.filter(user=instance.user).update(**{'user_likes_counter': F('user_likes_counter') - 1})

@receiver(post_save, sender=Like)
def increment_user_posts_likes_counter(sender, instance, created, **kwargs):
    if created:
        update_counter(instance.post.author, 'user_posts_likes_counter', 500, 'Posts Likes Badge', 'Posts Likes Badge', 'likes_recieved')

@receiver(post_delete, sender=Like)
def decrement_user_posts_likes_counter(sender, instance, **kwargs):
    UserBadgesTracker.objects.filter(user=instance.post.author).update(**{'user_posts_likes_counter': F('user_posts_likes_counter') - 1})
