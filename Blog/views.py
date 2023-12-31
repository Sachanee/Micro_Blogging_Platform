from django.shortcuts import render, get_object_or_404, redirect
from Blog.models import Post, Comment, Preference
from users.models import Follow, Profile
import sys
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from .forms import NewCommentForm
from django.contrib.auth.decorators import login_required
from .serializers import UserSerializer, GroupSerializer, PostSerializer
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status


def is_users(post_user, logged_user):
    return post_user == logged_user


PAGINATION_COUNT = 3


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "Blog/home.html"
    context_object_name = "posts"
    ordering = ["-date_posted"]
    paginate_by = PAGINATION_COUNT

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        all_users = []
        data_counter = (
            Post.objects.values("author")
            .annotate(author_count=Count("author"))
            .order_by("-author_count")[:6]
        )

        for aux in data_counter:
            all_users.append(User.objects.filter(pk=aux["author"]).first())
        # if Preference.objects.get(user = self.request.user):
        #     data['preference'] = True
        # else:
        #     data['preference'] = False
        data["preference"] = Preference.objects.all()
        # print(Preference.objects.get(user= self.request.user))
        data["all_users"] = all_users
        print(all_users, file=sys.stderr)
        return data

    def get_queryset(self):
        user = self.request.user
        qs = Follow.objects.filter(user=user)
        follows = [user]
        for obj in qs:
            follows.append(obj.follow_user)
        return Post.objects.filter(author__in=follows).order_by("-date_posted")


class UserPostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "Blog/user_posts.html"
    context_object_name = "posts"
    paginate_by = PAGINATION_COUNT

    def visible_user(self):
        return get_object_or_404(User, username=self.kwargs.get("username"))

    def get_context_data(self, **kwargs):
        visible_user = self.visible_user()
        logged_user = self.request.user
        print(logged_user.username == "", file=sys.stderr)

        if logged_user.username == "" or logged_user is None:
            can_follow = False
        else:
            can_follow = (
                Follow.objects.filter(
                    user=logged_user, follow_user=visible_user
                ).count()
                == 0
            )
        data = super().get_context_data(**kwargs)

        data["user_profile"] = visible_user
        data["can_follow"] = can_follow
        return data

    def get_queryset(self):
        user = self.visible_user()
        return Post.objects.filter(author=user).order_by("-date_posted")

    def post(self, request, *args, **kwargs):
        if request.user.id is not None:
            follows_between = Follow.objects.filter(
                user=request.user, follow_user=self.visible_user()
            )

            if "follow" in request.POST:
                new_relation = Follow(
                    user=request.user, follow_user=self.visible_user()
                )
                if follows_between.count() == 0:
                    new_relation.save()
            elif "unfollow" in request.POST:
                if follows_between.count() > 0:
                    follows_between.delete()

        return self.get(self, request, *args, **kwargs)


class PostDetailView(DetailView):
    model = Post
    template_name = "Blog/post_detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        comments_connected = Comment.objects.filter(
            post_connected=self.get_object()
        ).order_by("-date_posted")
        data["comments"] = comments_connected
        data["form"] = NewCommentForm(instance=self.request.user)
        return data

    def post(self, request, *args, **kwargs):
        new_comment = Comment(
            content=request.POST.get("content"),
            author=self.request.user,
            post_connected=self.get_object(),
        )
        new_comment.save()

        return self.get(self, request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "Blog/post_delete.html"
    context_object_name = "post"
    success_url = "/"

    def test_func(self):
        return is_users(self.get_object().author, self.request.user)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ["content"]
    template_name = "Blog/post_new.html"
    success_url = "/"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["tag_line"] = "Create a New Tweet"
        return data


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ["content"]
    template_name = "Blog/post_new.html"
    success_url = "/"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return is_users(self.get_object().author, self.request.user)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["tag_line"] = "Edit a Post"
        return data


class FollowsListView(ListView):
    model = Follow
    template_name = "Blog/follow.html"
    context_object_name = "follows"

    def visible_user(self):
        return get_object_or_404(User, username=self.kwargs.get("username"))

    def get_queryset(self):
        user = self.visible_user()
        return Follow.objects.filter(user=user).order_by("-date")

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(**kwargs)
        data["follow"] = "follows"
        return data


class FollowersListView(ListView):
    model = Follow
    template_name = "Blog/follow.html"
    context_object_name = "follows"

    def visible_user(self):
        return get_object_or_404(User, username=self.kwargs.get("username"))

    def get_queryset(self):
        user = self.visible_user()
        return Follow.objects.filter(follow_user=user).order_by("-date")

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(**kwargs)
        data["follow"] = "followers"
        return data


# Like Functionality====================================================================================


@login_required
def post_like(request, postid):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, id=postid)
        if post.likes.filter(id=request.user.id):
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

        return redirect("blog-home")

    else:
        messages.success(request, ("You Must Be Logged In To View That Page..."))
        return redirect("blog-home")


def about(request):
    return render(
        request,
        "Blog/about.html",
    )


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(["GET", "POST", "DELETE"])
def post_list(request):
    if request.method == "GET":
        posts = Post.objects.all()

        title = request.query_params.get("title", None)
        if title is not None:
            posts = posts.filter(title__icontains=title)

        posts_serializer = PostSerializer(posts, many=True)
        return JsonResponse(posts_serializer.data, safe=False)
        # 'safe=False' for objects serialization

    elif request.method == "POST":
        post_data = JSONParser().parse(request)
        post_serializer = PostSerializer(data=post_data)
        if post_serializer.is_valid():
            post_serializer.save()
            return JsonResponse(post_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        count = Post.objects.all().delete()
        return JsonResponse(
            {"message": "{} Posts were deleted successfully!".format(count[0])},
            status=status.HTTP_204_NO_CONTENT,
        )


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = "Blog/comment_delete.html"
    success_url = "/"

    def test_func(self):
        # Ensure only the author of the comment can delete it
        return is_users(self.get_object().author, self.request.user)

    def delete(self, request, *args, **kwargs):
        # Perform additional actions before deleting if needed
        return super().delete(request, *args, **kwargs)


class LikeDetailView(DetailView):
    model = Post
    template_name = "Blog/like_detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        liked_users = post.likes.all()  # Fetch all users who liked this post
        context["liked_users"] = liked_users
        return context


def retweet(request, pk):
    post = get_object_or_404(Post, id=pk)
    if post:
        return render(request, "Blog/retweet.html", {"post": post})
    else:
        messages.success(request, ("That Post Does Not Exist..."))
        return redirect("blog-home")


@login_required
def upload(request):
    if request.method == "POST":
        author = request.user
        content = request.POST.get("content")
        image = request.FILES.get("post_image")

        new_post = Post.objects.create(author=author, content=content, post_image=image)
        new_post.save()

        return redirect("/")
    else:
        return render(request, "blog-home.html")
