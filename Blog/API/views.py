from datetime import date
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from constants import READ_POST_LIMIT
from custom_errors import BlockedError, ReachedLimitError
from .permissions import IsAuthor
from django.db.models import Q
from .chatgpt import ChatGPTClient
from blogs.models import DisLike, Like, Post, Comment, PostsRead, Subscription, UserBadgesTracker
from blogs.serializers import DisLikeSerializer, LikeSerializer, PostSerializer, CommentSerializer, SubscriptionSerializer, UserBadgesTrackerSerializer, UserSerializer

class SignupView(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password or not username:
            return Response({'error': 'Invalid input. Username, email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(Q(username=username) | Q(email=email)).exists():
            return JsonResponse({"error": "Username or email is already exists"})
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            return JsonResponse({'message': 'User created successfully'})

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({'error': 'Invalid input. Both username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            token = Token.objects.get(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'detail': 'Invalid username and password'}, status=status.HTTP_401_UNAUTHORIZED)

class ListCreatePosts(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    queryset = Post.get_published.all()
    def perform_create(self, serializer):
        try:
            serializer.save(author=self.request.user)
        except BlockedError:
            serializer._data = {'Error': 'You are blocked'}
        except ReachedLimitError:
            serializer._data = {'Error': 'Cant add post, You have reached limit of add posts today.'}

class RetrieveUpdateDestroyPost(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAuthor]
    queryset = Post.get_published.all()
    serializer_class = PostSerializer
    lookup_field = 'slug'
    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except(BlockedError):
            return Response({'Error': 'You are blocked.'})

class ListCreateComments(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer
    def get_queryset(self):
        qs = Comment.objects.all()
        pk = self.kwargs['post']
        return qs.filter(post__id=pk)
    
class ListCreateLikes(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializer

    def get_queryset(self):
        qs = Like.objects.all()
        pk = self.kwargs['post']
        return qs.filter(post__id=pk)
    
    def create(self, request, *args, **kwargs):
        pk = request.data['post']
        check_like = Like.objects.filter(user = request.user, post = pk)
        if check_like:
            check_like.delete()
            return Response({'message': 'Unlike'})
        else:
            check_dislike = DisLike.objects.filter(user = request.user, post = pk)
            if check_dislike:
                check_dislike.delete()
            return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)

class CreateDisLike(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = DisLikeSerializer

    def get_queryset(self):
        qs = DisLike.objects.all()
        pk = self.kwargs['post']
        return qs.filter(post__id=pk)
    
    def create(self, request, *args, **kwargs):
        pk = request.data['post']
        check_dislike = DisLike.objects.filter(user = request.user, post = pk)
        if check_dislike:
            check_dislike.delete()
            return Response({'message': 'Unlike'})
        else:
            check_like = Like.objects.filter(user = request.user, post = pk)
            if check_like:
                check_like.delete()
            return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)

class ListCreateSubscription(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        qs = Subscription.objects.all()
        pk = self.kwargs['user_to_subscribe']
        return qs.filter(user_to_subscribe__id=pk)
    
    def create(self, request, *args, **kwargs):
        pk = request.data.get('user_to_subscribe')
        if not pk:
            return Response({"error":"Missing user id"}, status=status.HTTP_400_BAD_REQUEST)
        check_subscription = Subscription.objects.filter(subscriber = request.user, user_to_subscribe = pk)
        if check_subscription:
            check_subscription.delete()
            return Response({'message': 'Unsubscribe'})
        else:
            return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(subscriber = self.request.user)

class GetUser(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_post_by_chatgpt(request):
    title = request.GET.get('title', '')
    answer = ChatGPTClient.connect(f'Create Blog post about {title} with title and body')
    split1 = answer.split('Title:')
    title = split1[1].split('Body:')[0]
    split2 = answer.split('Body:')
    body = split2[1]
    try:
        post = Post(title = title, body = body, status = 'published', author = request.user)
        post.save()
        serializer = PostSerializer(post)
        return JsonResponse({'message': 'Post created successfully', 'post': serializer.data}, status = status.HTTP_200_OK)
    except KeyError:
        print(Exception)
        return JsonResponse({"error": "Error creating the blog post"}, status=status.HTTP_400_BAD_REQUEST)
    except(BlockedError):
        return JsonResponse({'Error': 'You are blocked'})
    except(ReachedLimitError):
        return JsonResponse({'Error': 'Cant add post, You have reached limit of add posts today.'})
    
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def summarize_post_by_chatgpt(request, slug):
    try:
        today = date.today()
        check_count_posts = PostsRead.objects.filter(user = request.user, read_at__date = today).count()
        print(check_count_posts)
        if check_count_posts == READ_POST_LIMIT:
            return JsonResponse({'message': 'You have reached limit of posts to read today'})
        else:
            post = Post.get_published.filter(slug = slug)
            if post:
                summary = ChatGPTClient.connect(f'Summarize this post: {post[0].body}')
                return JsonResponse({'Summarized post': summary}, status = status.HTTP_200_OK)
    except KeyError:
        print(Exception)
        return JsonResponse({"error": "Error summarizing the blog post"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def fix_post_grammar_by_chatgpt(request, slug):
    post = get_object_or_404(Post, slug = slug)
    try:
        fixed_text = ChatGPTClient.connect(f'Fix grammar in "{post.body}"')
        return JsonResponse({'Fixed post': fixed_text}, status = status.HTTP_200_OK)
    except KeyError:
        print(Exception)
        return JsonResponse({"error": "Error fixing of post grammar"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def display_leaderboard(request):
    try:
        top_post_contributors = UserBadgesTracker.objects.order_by('-posts_counter')[:3]
        top_likes_received_contributors = UserBadgesTracker.objects.order_by('-user_likes_counter')[:3]
        top_likes_given_contributors = UserBadgesTracker.objects.order_by('-user_posts_likes_counter')[:3]
        top_post_contributors_serializer = UserBadgesTrackerSerializer(top_post_contributors, many=True).data
        top_likes_received_contributors_serializer = UserBadgesTrackerSerializer(top_likes_received_contributors, many=True).data
        top_likes_given_contributors_serializer = UserBadgesTrackerSerializer(top_likes_given_contributors, many=True).data
        return JsonResponse({
            'Top post contributors': top_post_contributors_serializer,
            'Top likes received contributors': top_likes_received_contributors_serializer,
            'Top likes given contributors':top_likes_given_contributors_serializer
            }, status = status.HTTP_200_OK)
    except KeyError:
        print(Exception)
        return JsonResponse({"error": "Error get leaderboard"}, status=status.HTTP_400_BAD_REQUEST)
