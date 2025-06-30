from django.urls import path
from . import views


urlpatterns = [
    path('', views.issue_list, name='issue_list'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('submit/', views.submit_issue, name='submit_issue'),
    path('upvote/<int:issue_id>/', views.upvote_issue, name='upvote_issue'),
    path('resolve/<int:issue_id>/', views.mark_issue_resolved, name='mark_issue_resolved'),  # ✅ NEW
    path('map/', views.issue_map, name='issue_map'),
    path('issue-data/', views.issue_data, name='issue_data'),
    path('my-issues/', views.my_issues, name='my_issues'),
     path('issues/<int:issue_id>/', views.issue_detail, name='issue_detail'),
    path("ajax/post-comment/", views.ajax_post_comment, name="ajax_post_comment"),
   

]


