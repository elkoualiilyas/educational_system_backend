from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from .models import UserProfile, Course, Note, Enrollment, Grade, GradeReport
from .forms import UserProfileForm, CourseForm, NoteForm, UserCreateForm, GradeForm
from django.contrib.auth import login
from django.contrib import messages

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
            # Get the role before saving
            role = form.cleaned_data['role']
            # Prevent admin registration through the form
            if role == 'admin':
                form.add_error('role', 'Administrator role cannot be assigned through registration.')
                return render(request, 'bawabati_app/register.html', {'form': form})
            
            user = form.save()
            # Set the role from the form
            profile = user.userprofile
            profile.role = role
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
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    
    context = {
        'form': form,
        'user': request.user,
        'is_teacher': is_teacher(request.user),
        'is_student': is_student(request.user),
    }
    
    if is_teacher(request.user):
        context['courses'] = Course.objects.filter(assigned_teacher=request.user)
    elif is_student(request.user):
        context['enrolled_courses'] = request.user.enrolled_courses.all()
    
    return render(request, 'bawabati_app/profile.html', context)

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

# Grade Views
class GradeCreateView(TeacherRequiredMixin, CreateView):
    model = Grade
    form_class = GradeForm
    template_name = 'bawabati_app/grade_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
        student = get_object_or_404(User, pk=self.kwargs['student_pk'])
        context.update({
            'course': course,
            'student': student,
            'semester': self.kwargs['semester'],
            'assessment_type': self.kwargs['assessment_type']
        })
        return context
    
    def get(self, request, *args, **kwargs):
        # Check if grade already exists
        course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
        student = get_object_or_404(User, pk=self.kwargs['student_pk'])
        semester = self.kwargs['semester']
        assessment_type = self.kwargs['assessment_type']
        
        existing_grade = Grade.objects.filter(
            student=student,
            course=course,
            semester=semester,
            assessment_type=assessment_type
        ).first()
        
        if existing_grade:
            # Redirect to update view if grade exists
            return redirect('grade_update', pk=existing_grade.pk)
            
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
        student = get_object_or_404(User, pk=self.kwargs['student_pk'])
        
        # Verify teacher is assigned to this course
        if not is_admin(self.request.user) and course.assigned_teacher != self.request.user:
            return HttpResponseForbidden("You are not authorized to grade this course")
        
        # Check if grade already exists
        existing_grade = Grade.objects.filter(
            student=student,
            course=course,
            semester=self.kwargs['semester'],
            assessment_type=self.kwargs['assessment_type']
        ).first()
        
        if existing_grade:
            # Update the existing grade instead of creating a new one
            existing_grade.written_grade = form.cleaned_data['written_grade']
            existing_grade.participation = form.cleaned_data['participation']
            existing_grade.homework = form.cleaned_data['homework']
            existing_grade.comments = form.cleaned_data['comments']
            existing_grade.graded_by = self.request.user
            existing_grade.save()
            
            # Get or create grade report and update it
            report, created = GradeReport.objects.get_or_create(
                student=student,
                course=course,
                semester=existing_grade.semester,
                defaults={'exam_grade': 0}
            )
            
            # Update exam_grade if this is an exam grade
            if existing_grade.assessment_type == 'exam':
                report.exam_grade = existing_grade.final_grade
            
            report.save()  # This will recalculate continuous_assessment_average and final_average
            
            # Redirect to course detail page
            return redirect('course_detail', pk=course.pk)
        
        # If no existing grade, proceed with normal creation
        form.instance.course = course
        form.instance.student = student
        form.instance.semester = self.kwargs['semester']
        form.instance.assessment_type = self.kwargs['assessment_type']
        form.instance.graded_by = self.request.user
        
        response = super().form_valid(form)
        
        # Get or create grade report and update it
        report, created = GradeReport.objects.get_or_create(
            student=student,
            course=course,
            semester=form.instance.semester,
            defaults={'exam_grade': 0}
        )
        
        # Update exam_grade if this is an exam grade
        if form.instance.assessment_type == 'exam':
            report.exam_grade = form.instance.final_grade
        
        report.save()  # This will recalculate continuous_assessment_average and final_average
        
        return response
    
    def get_success_url(self):
        return reverse_lazy('course_detail', kwargs={'pk': self.kwargs['course_pk']})

class GradeUpdateView(TeacherRequiredMixin, UpdateView):
    model = Grade
    form_class = GradeForm
    template_name = 'bawabati_app/grade_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        grade = self.get_object()
        context.update({
            'course': grade.course,
            'student': grade.student,
            'semester': grade.semester,
            'assessment_type': grade.assessment_type
        })
        return context
    
    def form_valid(self, form):
        grade = self.get_object()
        
        # Verify teacher is assigned to this course
        if not is_admin(self.request.user) and grade.course.assigned_teacher != self.request.user:
            return HttpResponseForbidden("You are not authorized to modify this grade")
            
        response = super().form_valid(form)
        
        # Get or create grade report and update it
        report, created = GradeReport.objects.get_or_create(
            student=grade.student,
            course=grade.course,
            semester=grade.semester,
            defaults={'exam_grade': 0}
        )
        
        # Update exam_grade if this is an exam grade
        if grade.assessment_type == 'exam':
            report.exam_grade = grade.final_grade
        
        report.save()  # This will recalculate continuous_assessment_average and final_average
        
        return response
    
    def get_success_url(self):
        return reverse_lazy('course_detail', kwargs={'pk': self.object.course.pk})

@login_required
def view_grades(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    
    # Students can only view their own grades and must be enrolled
    if is_student(request.user):
        # Check if student is enrolled
        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            return HttpResponseForbidden("You must be enrolled in this course to view grades")
            
        grades = Grade.objects.filter(student=request.user, course=course)
        reports = GradeReport.objects.filter(student=request.user, course=course)
    # Teachers can view grades for their courses
    elif is_teacher(request.user) and course.assigned_teacher == request.user:
        grades = Grade.objects.filter(course=course)
        reports = GradeReport.objects.filter(course=course)
    # Admins can view all grades
    elif is_admin(request.user):
        grades = Grade.objects.filter(course=course)
        reports = GradeReport.objects.filter(course=course)
    else:
        return HttpResponseForbidden("You are not authorized to view these grades")
    
    # Ensure reports exist for all students with grades
    students_with_grades = set(grades.values_list('student', 'semester').distinct())
    for student_id, semester in students_with_grades:
        report, created = GradeReport.objects.get_or_create(
            student_id=student_id,
            course=course,
            semester=semester,
            defaults={'exam_grade': 0}
        )
        if not created:
            # Force recalculation of averages
            report.save()
    
    # Refresh reports queryset after potential updates
    if is_student(request.user):
        reports = GradeReport.objects.filter(student=request.user, course=course)
    else:
        reports = GradeReport.objects.filter(course=course)
    
    context = {
        'course': course,
        'grades': grades,
        'reports': reports,
        'is_teacher': is_teacher(request.user) or is_admin(request.user),
    }
    
    return render(request, 'bawabati_app/grade_list.html', context) 