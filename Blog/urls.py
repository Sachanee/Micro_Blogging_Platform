from django.urls import path
from . import views
from .views import (
    PostDetailView,
    PostCreateView,
    PostDeleteView,)


urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="Blog-about"),
    path("follow/", views.follow, name="Blog-follow"),
    path('post/<int:pk>/del/', PostDeleteView.as_view(), name='post-delete'),

    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),

    path("postdetails/", views.post_details, name="Blog-post_details"),

    path("post/new/", PostCreateView.as_view(), name="post-create"),
    path("postdetails/", views.post_details, name="Blog-post_details"),

