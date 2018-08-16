from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponseRedirect, Http404
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.utils import timezone
from django.db.models import Q


# Create your views here.
from .forms import PostForm
from .models import Post


def posts_create(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        messages.success(request, "Post Created")
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "form": form,
    }
    return render(request, "post_form.html", context)

def posts_detail(request, slug):
    instance = get_object_or_404(Post, slug=slug)
    if instance.publish > timezone.now().date() or instance.draft:
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404
    context = {
        "title": "Detail",
        "instance": instance
    }

    return render(request, "post_detail.html", context)

def posts_list(request):
    today = timezone.now().date()
    queryset_list = Post.posts.active()
    if request.user.is_staff or not request.user.is_superuser:
        queryset_list = Post.posts.all()

    query = request.GET.get("q")
    if query:
        queryset_list = queryset_list.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(user__first_name__icontains=query)
        ).distinct()

    paginator = Paginator(queryset_list, 10)  # Show 25 contacts per page
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.get_page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)

    if request.user.is_authenticated:
        context = {
            "object_list": queryset,
            "title": "My list",
            "page_request_var": page_request_var,
            "today": today,
        }
    else:
        context = {
            "title": "List"
        }


    return render(request, "post_list.html", context)

def posts_update(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, slug=slug)
    form = PostForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "Post Updated")
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "title": instance.title,
        "content": instance.content,
        "form": form,
    }
    return render(request, "post_form.html", context)

def posts_delete(request, slug=None):
    instance = get_object_or_404(Post, slug=slug)
    instance.delete()
    messages.success(request, "Post Deleted")
    return redirect('posts:list')







