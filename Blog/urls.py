from django.urls import path
from . import views
from .views import PostCreateView

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="Blog-about"),
    path("follow/", views.follow, name="Blog-follow"),
    path("postdelete/", views.post_delete, name="Blog-post_delete"),
    path("post/new/", PostCreateView.as_view(), name="post-create"),
]
