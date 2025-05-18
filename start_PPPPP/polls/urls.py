from django.urls import path
from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_question, name='create_question'),
    path('<int:question_id>/add_choices/', views.add_choices, name='add_choices'),
    path('<int:question_id>/', views.detail, name='detail'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('<int:question_id>/results/', views.results, name='results'),
]