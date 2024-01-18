from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path('password_reset/', auth_views.PasswordResetView.as_view(),
         name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
    path("", views.get_all_posts, name="all-posts"),
    path("create-post-by-chatgpt/", views.create_post_by_chatgpt, name="create-post-by-chatgpt"),
    path("summarize-post-by-chatgpt/<slug:slug>/", views.summarize_post_by_chatgpt, name="summarize-post-by-chatgpt"),
    path("fix-post-grammar-by-chatgpt/<slug:slug>", views.fix_post_grammar_by_chatgpt, name="fix-post-grammar-by-chatgpt"),
    path("add_post/", views.add_post, name="add_post"),
    path("<slug:slug>/", views.get_post, name="get_post"),
    path("add_like/<slug:slug>/", views.add_like, name="add_like"),
    path("add_dislike/<slug:slug>/", views.add_dislike, name="add_dislike"),
    path("subscribe/<int:pk>/<slug:slug>/", views.subscribe, name="subscribe"),
    path("edit_post/<slug:slug>/", views.edit_post, name="edit-post"),
    

]
