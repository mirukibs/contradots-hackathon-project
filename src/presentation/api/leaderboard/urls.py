"""URL configuration for leaderboard API endpoints."""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_leaderboard, name='get_leaderboard'),
    path('my-profile/', views.get_my_profile, name='get_my_profile'),
    path('my-rank/', views.get_my_rank, name='get_my_rank'),
]