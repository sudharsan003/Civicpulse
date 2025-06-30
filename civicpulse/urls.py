# civicpulse/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Replace `home` with your actual view name
    path('report/', views.report_issue, name='report_issue'),
    path('issues/', views.issue_list, name='issue_list'),
    path('issue/<int:issue_id>/', views.issue_detail, name='issue_detail'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    # add other views here
]
