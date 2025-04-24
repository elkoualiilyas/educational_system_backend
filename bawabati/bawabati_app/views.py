from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from .models import UserProfile, Course, Note, Enrollment
from .forms import UserProfileForm, CourseForm, NoteForm, UserCreateForm
from django.contrib.auth import login

# Helper functions for role checking
def is_admin(user):
    return hasattr(user, 'userprofile') and user.userprofile.role == 'admin'

def is_teacher(user):
    return hasattr(user, 'userprofile') and user.userprofile.role == 'teacher'

def is_student(user):
    return hasattr(user, 'userprofile') and user.userprofile.role == 'student'

# Role mixin classes
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_admin(self.request.user)

class TeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_admin(self.request.user) or is_teacher(self.request.user)

class StudentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_student(self.request.user)

# Authentication Views
def register(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            # By default, new users are students
            profile = user.userprofile
            profile.role = 'student'
            profile.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreateForm()
    return render(request, 'bawabati_app/register.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}
    
    if is_admin(user):
        users = User.objects.all()
        context['users'] = users
        context['admin_count'] = users.filter(userprofile__role='admin').count()
        context['teacher_count'] = users.filter(userprofile__role='teacher').count()
        context['student_count'] = users.filter(userprofile__role='student').count()
        context['courses'] = Course.objects.all()
        return render(request, 'bawabati_app/admin_dashboard.html', context)
    
    elif is_teacher(user):
        context['courses'] = Course.objects.filter(assigned_teacher=user)
        return render(request, 'bawabati_app/teacher_dashboard.html', context)
    
    else:  # student
        context['enrollments'] = Enrollment.objects.filter(student=user)
        return render(request, 'bawabati_app/student_dashboard.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'bawabati_app/profile.html', {'form': form})

# User Management Views (Admin only)
class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'bawabati_app/user_list.html'
    context_object_name = 'users'

class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'bawabati_app/user_form.html'
    success_url = reverse_lazy('user_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Set the role from the form
        role = form.cleaned_data.get('role', 'student')
        self.object.userprofile.role = role
        self.object.userprofile.save()
        return response

class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = UserCreateForm
    template_name = 'bawabati_app/user_form.html'
    success_url = reverse_lazy('user_list')

class UserDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = 'bawabati_app/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')

# Course Views
class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'bawabati_app/course_list.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        user = self.request.user
        if is_admin(user):
            return Course.objects.all()
        elif is_teacher(user):
            return Course.objects.filter(assigned_teacher=user)
        else:  # student
            enrollments = Enrollment.objects.filter(student=user)
            return Course.objects.filter(id__in=[e.course.id for e in enrollments])

class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'bawabati_app/course_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        
        # Add enrolled students if teacher or admin
        if is_admin(self.request.user) or is_teacher(self.request.user):
            context['enrolled_students'] = Enrollment.objects.filter(course=course)
        
        # Add if student is enrolled
        if is_student(self.request.user):
            context['is_enrolled'] = Enrollment.objects.filter(
                student=self.request.user, 
                course=course
            ).exists()
            
        # Add course notes
        context['notes'] = Note.objects.filter(course=course)
        
        return context

class CourseCreateView(AdminRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'bawabati_app/course_form.html'
    success_url = reverse_lazy('course_list')

class CourseUpdateView(AdminRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'bawabati_app/course_form.html'
    success_url = reverse_lazy('course_list')

class CourseDeleteView(AdminRequiredMixin, DeleteView):
    model = Course
    template_name = 'bawabati_app/course_confirm_delete.html'
    success_url = reverse_lazy('course_list')

# Enrollment Views
@login_required
def enroll_course(request, pk):
    if not is_student(request.user):
        return HttpResponseForbidden("Only students can enroll in courses")
    
    course = get_object_or_404(Course, pk=pk)
    
    # Check if already enrolled
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        return redirect('course_detail', pk=pk)
    
    # Create enrollment
    Enrollment.objects.create(student=request.user, course=course)
    return redirect('course_detail', pk=pk)

# Note Views
class NoteCreateView(TeacherRequiredMixin, CreateView):
    model = Note
    form_class = NoteForm
    template_name = 'bawabati_app/note_form.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        
        # Admin can add notes to any course
        if is_admin(user):
            form.fields['course'].queryset = Course.objects.all()
        # Teacher can only add notes to their courses
        else:
            form.fields['course'].queryset = Course.objects.filter(assigned_teacher=user)
            
        return form
    
    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('course_detail', kwargs={'pk': self.object.course.pk})

class NoteDeleteView(TeacherRequiredMixin, DeleteView):
    model = Note
    template_name = 'bawabati_app/note_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('course_detail', kwargs={'pk': self.object.course.pk})
    
    def test_func(self):
        note = self.get_object()
        user = self.request.user
        # Admin can delete any note
        if is_admin(user):
            return True
        # Teacher can only delete their own notes
        return is_teacher(user) and note.uploaded_by == user 