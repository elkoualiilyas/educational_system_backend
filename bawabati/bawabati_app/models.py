from django.utils import  timezone
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True)
    
    # Teacher specific fields
    specialisation = models.CharField(max_length=100, blank=True)

    # Student specific fields

    def __str__(self):
        return f"{self.user.username} - {self.role}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        role = 'admin' if instance.is_superuser else 'student'
        UserProfile.objects.create(user=instance, role=role)
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
def get_default_end_date():
    return timezone.now().date() + timedelta(days=90)
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'userprofile__role': 'teacher'})
    students = models.ManyToManyField(User, through='Enrollment', related_name='enrolled_courses', limit_choices_to={'userprofile__role': 'student'})
    created_at = models.DateTimeField(auto_now_add=True)    
    updated_at = models.DateTimeField(auto_now=True)
    specialisation = models.CharField(max_length=100, blank=True)
    capacity = models.PositiveIntegerField(default=30)  # Or whatever default you want
    end_date = models.DateField(default=get_default_end_date)
    start_date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Note(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='notes/', blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='notes')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()  # longtext in MySQL maps to TextField in Django
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'userprofile__role': 'student'}
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'course']
        
    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"

class Grade(models.Model):
    SEMESTER_CHOICES = [
        (1, 'First Semester'),
        (2, 'Second Semester'),
    ]

    ASSESSMENT_TYPE_CHOICES = [
        ('control_1', 'Premier Contrôle'),
        ('control_2', 'Deuxième Contrôle'),
        ('exam', 'Examen Final'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades', limit_choices_to={'userprofile__role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='grades')
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPE_CHOICES)
    
    # Grades for different components
    written_grade = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(20)])
    participation = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(20)], null=True, blank=True)
    homework = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(20)], null=True, blank=True)
    
    # Calculated fields
    final_grade = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(20)])
    
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='grades_given')

    class Meta:
        unique_together = ['student', 'course', 'semester', 'assessment_type']
        ordering = ['semester', 'assessment_type', 'student__username']

    def calculate_final_grade(self):
        """Calculate final grade based on components"""
        weights = {
            'written': Decimal('0.70'),  # 70% written
            'participation': Decimal('0.15'),  # 15% participation
            'homework': Decimal('0.15'),  # 15% homework
        }
        
        final = self.written_grade * weights['written']
        if self.participation:
            final += self.participation * weights['participation']
        if self.homework:
            final += self.homework * weights['homework']
            
        return round(final, 2)

    def save(self, *args, **kwargs):
        self.final_grade = self.calculate_final_grade()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.username} - {self.course.title} - {self.get_assessment_type_display()} - {self.final_grade}/20"

class GradeReport(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grade_reports', limit_choices_to={'userprofile__role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='grade_reports')
    semester = models.IntegerField(choices=Grade.SEMESTER_CHOICES)
    
    # Calculated fields
    continuous_assessment_average = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(20)], null=True, default=0)
    exam_grade = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(20)], default=0)
    final_average = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(20)], null=True, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'course', 'semester']
        ordering = ['semester', 'student__username']

    def calculate_continuous_assessment(self):
        """Calculate average of control grades"""
        controls = Grade.objects.filter(
            student=self.student,
            course=self.course,
            semester=self.semester,
            assessment_type__in=['control_1', 'control_2']
        )
        if not controls.exists():
            return None
        return round(sum(g.final_grade for g in controls) / controls.count(), 2)

    def calculate_final_average(self):
        """Calculate final average (40% continuous assessment + 60% exam)"""
        if self.continuous_assessment_average is None or self.exam_grade is None:
            return None
        return round((self.continuous_assessment_average * Decimal('0.4')) + (self.exam_grade * Decimal('0.6')), 2)

    def save(self, *args, **kwargs):
        # Calculate continuous assessment average
        cont_avg = self.calculate_continuous_assessment()
        self.continuous_assessment_average = cont_avg if cont_avg is not None else 0
        
        # Calculate final average only if we have both components
        if cont_avg is not None and self.exam_grade:
            self.final_average = self.calculate_final_average()
        else:
            self.final_average = None
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.username} - {self.course.title} - S{self.semester} - {self.final_average}/20" 