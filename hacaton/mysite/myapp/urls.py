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
    path('users/update-day-advice/', views.update_day_advice_subscriber, name='update_day_advice'),
    path('csrf/', views.get_csrf_token, name='get_csrf'),
    path('userinfo/create/', views.create_user_info, name='create_user_info'),
    path('userinfo/', views.get_all_user_info, name='get_all_user_info'),  # Оба метода на один URL
    path('userinfo/<int:info_id>/', views.get_user_info_by_id, name='get_user_info_by_id'),
    path('question/add/', views.add_question, name='add_question'),
    path('question/<int:question_id>/solve/', views.update_question_solved, name='update_solved'),
    path('questions/all/', views.list_all_questions, name='list_all_questions'),
    path('questions/unsolved/', views.list_unsolved_questions, name='list_unsolved_questions'),
    path('questions/answer', views.answer_question, name='answer_question'),
    path('events/create', views.create_event, name='create_event'),
    path('events/delete/<int:event_id>/', views.delete_event, name='delete_event'),
] 