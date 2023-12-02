from django.shortcuts import render


from django.views.generic import (
    CreateView,
    DetailView,
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


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'Blog/post_delete.html'
    context_object_name = 'post'
    success_url = '/'

    def test_func(self):
        return is_users(self.get_object().author, self.request.user)


class PostDetailView(DetailView):
    model = Post
    template_name = 'Blog/post_detail.html'
    context_object_name = 'post'
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        comments_connected = Comment.objects.filter(post_connected=self.get_object()).order_by('-date_posted')
        data['comments'] = comments_connected
        data['form'] = NewCommentForm(instance=self.request.user)
        return data

    def post(self, request, *args, **kwargs):
        new_comment = Comment(content=request.POST.get('content'),
                              author=self.request.user,
                              post_connected=self.get_object())
        new_comment.save()

        return self.get(self, request, *args, **kwargs)
    
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


