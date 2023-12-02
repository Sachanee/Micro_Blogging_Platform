from django.shortcuts import render


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