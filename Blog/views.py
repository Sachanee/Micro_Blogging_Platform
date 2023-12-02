from django.shortcuts import render
from django.views.generic import (
    CreateView,
)
from Blog.models import Post, Comment, Preference


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


class PostCreateView(CreateView):
    model = Post
    fields = ["content"]
    template_name = "Blog/post_new.html"
    success_url = "/"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["tag_line"] = "Add a new post"
        return data
