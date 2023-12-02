from django.shortcuts import render
from django.views.generic import ListView, DetailView,
from .models import Post




# Create your views here.
def home(request):
    return render(request, "Blog/home.html")


def about(request):
    return render(
        request,
        "Blog/about.html",
    )

def follow(request):
    return render(request, "Blog/follow.html")

def post_delete(request):
    return render(request, "Blog/post_delete.html")

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'