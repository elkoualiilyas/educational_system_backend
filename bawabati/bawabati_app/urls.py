from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect
from . import views

def logout_view(request):
    auth_logout(request)
    return redirect('login')

urlpatterns = [
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='bawabati_app/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Dashboard & Profile
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # User Management (Admin)
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/add/', views.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/update/', views.UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
    
    # Course Management
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('courses/add/', views.CourseCreateView.as_view(), name='course_create'),
    path('courses/<int:pk>/update/', views.CourseUpdateView.as_view(), name='course_update'),
    path('courses/<int:pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),
    
    # Enrollment
    path('courses/<int:pk>/enroll/', views.enroll_course, name='enroll_course'),
    
    # Notes
    path('notes/add/', views.NoteCreateView.as_view(), name='note_create'),
    path('notes/<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note_delete'),
    
    # Grade URLs
    path('course/<int:course_pk>/grades/', views.view_grades, name='view_grades'),
    path('course/<int:course_pk>/student/<int:student_pk>/grade/<int:semester>/<str:assessment_type>/add/', 
         views.GradeCreateView.as_view(), name='grade_create'),
    path('grade/<int:pk>/edit/', views.GradeUpdateView.as_view(), name='grade_update'),
] 