from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),  # 登录后的首页
    path('', views.home_view, name='home'),  # 公开的首页

    # 文章相关URL
    path('articles/new/', views.article_create_view, name='article_create'),
    path('articles/<int:pk>/', views.article_detail_view, name='article_detail'),
    path('articles/<int:pk>/edit/', views.article_update_view, name='article_update'),
    path('articles/<int:pk>/delete/', views.article_delete_view, name='article_delete'),

    path('tags/<slug:tag_slug>/', views.article_list_by_tag_view, name='article_list_by_tag'),
]