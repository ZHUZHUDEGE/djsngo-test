from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from taggit.models import Tag
from .models import Article
from .forms import LoginForm, RegisterForm, ArticleForm
from django.contrib.auth.models import User


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'blog/login.html', {'form': form})


@login_required
def profile_view(request):
    user = request.user
    try:
        profile = user.userprofile
    except:
        # 如果用户还没有profile，创建一个空的
        from .models import UserProfile
        profile = UserProfile.objects.create(user=user)

    context = {
        'user': user,
        'profile': profile
    }
    return render(request, 'blog/profile.html', context)

# def register_view(request):
#     if request.method == 'POST':
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             # 创建用户后自动登录
#             login(request, user)
#             return redirect('home')
#     else:
#         form = RegisterForm()
#     return render(request, 'blog/register.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 自动创建UserProfile
            from .models import UserProfile
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'blog/register.html', {'form': form})



def logout_view(request):
    logout(request)
    return redirect('home')


def home_view(request):
    # 无需登录即可访问的首页
    # articles = Article.objects.filter(published=True).order_by('-created_at')[:5]
    # return render(request, 'blog/home.html', {'articles': articles})

    latest_articles = Article.objects.filter(published=True).order_by('-created_at')[:5]

    article_list = Article.objects.filter(published=True).order_by('-created_at')
    paginator = Paginator(article_list, 10)  # 每页10篇文章
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 获取热门标签 - 使用最多的前10个标签
    popular_tags = Tag.objects.annotate(
        num_articles=Count('taggit_taggeditem_items')
    ).order_by('-num_articles')[:10]

    # 获取最受欢迎的文章 - 按浏览量排序
    popular_articles = Article.objects.filter(published=True).order_by('-views')[:3]

    context = {
        'latest_articles': latest_articles,
        'popular_tags': popular_tags,
        'popular_articles': popular_articles,
        'page_obj': page_obj,
    }
    return render(request, 'blog/home.html', context)


@login_required
def dashboard_view(request):
    # 这是登录后的仪表盘页面
    return render(request, 'blog/dashboard.html')


@login_required
def article_create_view(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            # 显式保存tags
            form.save_m2m()

            # 强制重新查询热门标签
            Tag.objects.annotate(num_articles=Count('taggit_taggeditem_items')).order_by('-num_articles')

            return redirect('article_detail', pk=article.pk)
    else:
        form = ArticleForm()
    return render(request, 'blog/article_form.html', {'form': form})


def article_detail_view(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.increment_views()
    return render(request, 'blog/article_detail.html', {'article': article})


@login_required
def article_update_view(request, pk):
    article = get_object_or_404(Article, pk=pk, author=request.user)
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return redirect('article_detail', pk=article.pk)
    else:
        form = ArticleForm(instance=article)
    return render(request, 'blog/article_form.html', {'form': form})


@login_required
def article_delete_view(request, pk):
    article = get_object_or_404(Article, pk=pk, author=request.user)
    if request.method == 'POST':
        article.delete()
        return redirect('home')
    return render(request, 'blog/article_confirm_delete.html', {'article': article})


def article_list_by_tag_view(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    articles = Article.objects.filter(published=True, tags__in=[tag]).order_by('-created_at')

    context = {
        'tag': tag,
        'articles': articles,
    }
    return render(request, 'blog/article_list_by_tag.html', context)


# def article_list_view(request):
#     article_list = Article.objects.filter(published=True).order_by('-created_at')
#     paginator = Paginator(article_list, 10)  # 每页10篇文章
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     return render(request, 'blog/home.html', {'page_obj': page_obj})