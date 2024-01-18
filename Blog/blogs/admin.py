from django.contrib import admin
from .models import Badges, Blocks, Comment, Like, LoginStreak, Notification, Post, PostsRead, UserBadgesTracker, Warnings
from django.contrib import messages

class PostAdmin(admin.ModelAdmin):
   """ Customizing the Comment Admin interface """
   list_display = ['title', 'body', 'author', 'created', 'pub_date']
   
   def message_user(self, request, message, level=messages.INFO, extra_tags='',
        fail_silently=False):
        pass

   def save_model(self, request, obj, form, change):
      try:
         super().save_model(request, obj, form, change)
         messages.success(request, "Done.")
      except ValueError:
         messages.error(request, "You cant add or edit post, you are blocked!")
      
    
         

admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
admin.site.register(Blocks)
admin.site.register(Warnings)
admin.site.register(PostsRead)
admin.site.register(Like)
admin.site.register(UserBadgesTracker)
admin.site.register(Badges)
admin.site.register(Notification)
admin.site.register(LoginStreak)