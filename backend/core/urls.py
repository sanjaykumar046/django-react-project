from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_root, name='api-root'),
    path('login/', views.login_view, name='login'),
    path('staff/', views.staff_list, name='staff-list'),
    path('projects/', views.projects_list, name='projects-list'),
    path('assignments/', views.assignments_list, name='assignments-list'),
    path('assign-project/', views.assign_project, name='assign-project'),
    path('my-assignments/', views.my_assignments, name='my-assignments'),
    path('unlock-project/', views.unlock_project, name='unlock-project'),
]