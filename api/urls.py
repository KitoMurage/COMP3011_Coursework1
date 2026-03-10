from django.urls import path
from . import views

urlpatterns = [
    path('players/<int:player_id>/', views.get_player, name='get_player'),
    path('scouting-reports/', views.create_report, name='create_report'),
    path('scouting-reports/<int:report_id>/', views.manage_report, name='manage_report'),
    path('analytics/leaderboard/', views.get_leaderboard, name='get_leaderboard'),
    path('analytics/team-summary/', views.get_team_summary, name='get_team_summary'),
]