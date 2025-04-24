from django.contrib import admin
from .models import UserProfile, Course, Note, Enrollment

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_teacher')
    list_filter = ('assigned_teacher',)
    search_fields = ('title', 'description')

class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'uploaded_by', 'upload_date')
    list_filter = ('course', 'uploaded_by')
    search_fields = ('title', 'course__title')
    date_hierarchy = 'upload_date'

class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrollment_date')
    list_filter = ('course', 'enrollment_date')
    search_fields = ('student__username', 'course__title')
    date_hierarchy = 'enrollment_date'

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(Enrollment, EnrollmentAdmin) 