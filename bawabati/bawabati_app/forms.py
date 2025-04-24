from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Course, Note

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only admins can change roles
        if not hasattr(kwargs.get('instance', None), 'user') or kwargs['instance'].user.userprofile.role != 'admin':
            self.fields['role'].disabled = True

class UserCreateForm(UserCreationForm):
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role']

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'assigned_teacher']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show teachers in the assigned_teacher dropdown
        self.fields['assigned_teacher'].queryset = User.objects.filter(userprofile__role='teacher')

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'file', 'course'] 