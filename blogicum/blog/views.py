from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Count
from django.core.mail import send_mail


from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, UserEditForm

User = get_user_model()


def paginate(request, queryset, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    now = timezone.now()

    posts = Post.objects.filter(
        is_published=True,
        pub_date__lte=now,
        category__is_published=True
    ).select_related(
        'author', 'category', 'location'
    ).annotate(
        comment_count=Count('comment')
    ).order_by('-pub_date')

    page_obj = paginate(request, posts)

    return render(request, 'blog/index.html', {
        'page_obj': page_obj
    })


def post_detail(request, id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'category', 'location'),
        pk=id,
    )

    now = timezone.now()

    is_visible = (
        post.is_published and
        post.pub_date <= now and
        post.category and post.category.is_published
    )

    is_author = (request.user == post.author)

    if not is_visible and not is_author:
        raise Http404

    comments = post.comment_set.select_related('author').order_by('created_at')

    return render(request, 'blog/detail.html', {
        'post': post,
        'comments': comments,
        'form': CommentForm(),
    })

@login_required
def create_post(request):
    form = PostForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)

    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect('blog:post_detail', id=post.id)

    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post
    )

    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', id=post.id)

    return render(request, 'blog/create.html', {
        'form': form,
        'is_edit': True,
        'post': post
    })


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect('blog:post_detail', id=post.id)

    form = PostForm(instance=post)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)

    return render(request, 'blog/create.html', {
        'form': form,
        'post': post,
        'is_delete': True
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('blog:post_detail', id=post.id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)

    if comment.author != request.user:
        raise Http404

    form = CommentForm(request.POST or None, instance=comment)

    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', id=post_id)

    return render(request, 'blog/comment.html', {
        'form': form,
        'comment': comment,
    })


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)

    if comment.author != request.user:
        raise Http404

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id=post_id)

    return render(request, 'blog/comment.html', {
        'comment': comment,
    })


def profile(request, username):
    user = get_object_or_404(User, username=username)
    now = timezone.now()

    if request.user == user:
        posts = Post.objects.filter(author=user)
    else:
        posts = Post.objects.filter(
            author=user,
            is_published=True,
            pub_date__lte=now,
            category__is_published=True
        )

    posts = posts.select_related(
        'author', 'category', 'location'
    ).annotate(
        comment_count=Count('comment')
    ).order_by('-pub_date')

    page_obj = paginate(request, posts)

    return render(request, 'blog/profile.html', {
        'profile': user,
        'page_obj': page_obj,
    })


@login_required
def edit_profile(request):
    form = UserEditForm(request.POST or None, instance=request.user)

    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)

    return render(request, 'blog/user.html', {'form': form})


def registration(request):
    form = UserCreationForm(request.POST or None)

    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('blog:profile', username=user.username)

    return render(request, 'registration/registration_form.html', {'form': form})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    posts = Post.objects.filter(
        category=category,
        is_published=True,
        pub_date__lte=timezone.now()
    ).select_related(
        'author', 'location', 'category'
    ).annotate(
        comment_count=Count('comment')
    ).order_by('-pub_date')

    page_obj = paginate(request, posts)

    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': page_obj,
    })


send_mail(
    subject='Тестовое письмо',
    message='Привет! Это тест.',
    from_email='test@example.com',
    recipient_list=['user@example.com'],
    fail_silently=False,
)