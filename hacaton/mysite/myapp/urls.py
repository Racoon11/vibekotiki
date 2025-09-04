from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.questions, name='questions'),
    path('events/', views.events, name='events'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),
    path('users/', views.get_users, name='get_users'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/<int:user_id>/', views.get_user, name='get_user'),
    path('csrf/', views.get_csrf_token, name='get_csrf'),
    path('userinfo/create/', views.create_user_info, name='create_user_info'),
    path('userinfo/', views.get_all_user_info, name='get_all_user_info'),  # Оба метода на один URL
    path('userinfo/<int:info_id>/', views.get_user_info_by_id, name='get_user_info_by_id'),
] 