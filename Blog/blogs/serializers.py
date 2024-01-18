from rest_framework import serializers

from .models import DisLike, Like, Post, Comment, Subscription, UserBadgesTracker
from django.contrib.auth.models import User
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = ['user']

class DisLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisLike
        fields = '__all__'
        read_only_fields = ['user']
        
class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ['subscriber']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class UserBadgesTrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBadgesTracker
        fields = '__all__'