from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views

def logout_view(request):
    auth_logout(request)
    return redirect('login')

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'users', api_views.UserViewSet)

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
    
    # API endpoints
    path('api/auth/register/', api_views.register_user, name='api_register'),
    path('api/auth/login/', api_views.login_user, name='api_login'),
    path('api/auth/logout/', api_views.logout_user, name='api_logout'),
    path('api/auth/user/', api_views.get_current_user, name='api_current_user'),
    path('api/users/profile/', api_views.update_profile, name='api_update_profile'),
    path('api/dashboard/admin/', api_views.admin_dashboard_data, name='api_admin_dashboard'),
    path('api/dashboard/teacher/', api_views.teacher_dashboard_data, name='api_teacher_dashboard'),
    path('api/dashboard/student/', api_views.student_dashboard_data, name='api_student_dashboard'),
    path('api/courses/', api_views.course_list, name='api_course_list'),
    path('api/courses/<int:pk>/', api_views.course_detail, name='api_course_detail'),
    path('api/courses/add/', api_views.create_course, name='api_create_course'),
    path('api/courses/<int:pk>/edit/', api_views.update_course, name='api_update_course'),
    path('api/courses/<int:course_id>/notes/', api_views.list_notes, name='api_list_notes'),
    path('api/courses/<int:course_id>/notes/upload/', api_views.upload_note, name='api_upload_note'),
    path('api/notes/<int:note_id>/', api_views.delete_note, name='api_delete_note'),
    path('api/teachers/', api_views.list_teachers, name='api_list_teachers'),
    path('api/students/', api_views.list_students, name='api_list_students'),
    path('api/courses/<int:course_id>/grades/', api_views.list_grades, name='api_list_grades'),
    path('api/courses/<int:course_id>/students/<int:student_id>/grades/', api_views.add_grade, name='api_add_grade'),
    path('api/', include(router.urls)),
] 