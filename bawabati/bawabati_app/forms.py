from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Course, Note, Grade, GradeReport

from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_image', 'phone_number', 'bio', 'role', 'specialisation']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')

        # Only admins can change roles
        if not instance or getattr(instance, 'role', None) != 'admin':
            self.fields['role'].disabled = True

        # Only show 'specialisation' for teachers
        if instance and getattr(instance, 'role', None) != 'teacher':
            self.fields['specialisation'].widget = forms.HiddenInput()


class UserCreateForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=[('teacher', 'Teacher'), ('student', 'Student')],
        required=True
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role']

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'assigned_teacher', 'students']
        widgets = {
            'students': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show teachers in the assigned_teacher dropdown
        self.fields['assigned_teacher'].queryset = User.objects.filter(userprofile__role='teacher')
        # Only show students in the students selection
        self.fields['students'].queryset = User.objects.filter(userprofile__role='student')

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'file', 'course']

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['written_grade', 'participation', 'homework', 'comments']
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if isinstance(self.fields[field], forms.DecimalField):
                self.fields[field].widget.attrs.update({
                    'min': '0',
                    'max': '20',
                    'step': '0.25'
                })
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class GradeReportForm(forms.ModelForm):
    class Meta:
        model = GradeReport
        fields = ['exam_grade']
        widgets = {
            'exam_grade': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '20',
                'step': '0.25'
            })
        } 