from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("get_posts/", views.ListCreatePosts.as_view(), name="list-posts"),
    path("update_post/<slug:slug>/", views.RetrieveUpdateDestroyPost.as_view(), name="update-post"),
    path("delete_post/<slug:slug>/", views.RetrieveUpdateDestroyPost.as_view(), name="delete-post"),
    path("retireve_post/<slug:slug>/", views.RetrieveUpdateDestroyPost.as_view(), name="get-post"),
    path("create_post/", views.ListCreatePosts.as_view(), name="add-post"),
    path("list-comments/<int:post>/", views.ListCreateComments.as_view(), name="list-comments"),
    path("add-comment/", views.ListCreateComments.as_view(), name="add-comment"),
    path("add-like/", views.ListCreateLikes.as_view(), name="add-like"),
    path("list-like/<int:post>", views.ListCreateLikes.as_view(), name="list-like"),
    path("add-dislike/", views.CreateDisLike.as_view(), name="add-dislike"),
    path("subscribe/", views.ListCreateSubscription.as_view(), name="subscribe"),
    path("list-subscriptions/<int:user_to_subscribe>", views.ListCreateSubscription.as_view(), name="list-subscriptions"),
    path("users/", views.GetUser.as_view(), name="users"),
    path("add-post-by-chatgpt/", views.create_post_by_chatgpt, name="add-post-by-chatgpt"),
    path("summarize-post-by-chatgpt/<slug:slug>/", views.summarize_post_by_chatgpt, name="summarize-post-by-chatgpt"),
    path("fix-post-grammar-by-chatgpt/", views.fix_post_grammar_by_chatgpt, name="fix-post-grammar-by-chatgpt"),
    path("leaderboard/", views.display_leaderboard, name="leaderboard"),
]


    