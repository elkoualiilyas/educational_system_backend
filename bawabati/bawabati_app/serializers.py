from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Course, Note, Enrollment, Grade, GradeReport

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['role', 'profile_image', 'phone_number', 'bio', 'specialisation']

class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'userprofile']
        read_only_fields = ['id']

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role']
    
    def create(self, validated_data):
        role = validated_data.pop('role')
        user = User.objects.create_user(**validated_data)
        user.userprofile.role = role
        user.userprofile.save()
        return user

class EnrolledStudentSerializer(serializers.ModelSerializer):
    enrollment_date = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'enrollment_date']

    def get_enrollment_date(self, obj):
        course = self.context.get('course')
        if course:
            enrollment = Enrollment.objects.filter(student=obj, course=course).first()
            if enrollment:
                return enrollment.enrollment_date
        return None

class CourseSerializer(serializers.ModelSerializer):
    assigned_teacher = UserSerializer(read_only=True)
    assigned_teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(userprofile__role='teacher'),
        source='assigned_teacher',
        write_only=True,
        required=True
    )
    student_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(userprofile__role='student'),
        source='students',
        many=True,
        write_only=True,
        required=False
    )
    enrolled_students = serializers.SerializerMethodField()
    current_user = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'specialisation', 'capacity',
            'start_date', 'end_date', 'created_at', 'assigned_teacher',
            'assigned_teacher_id', 'student_ids', 'enrolled_students', 'current_user'
        ]

    def get_enrolled_students(self, obj):
        enrollments = Enrollment.objects.filter(course=obj)
        students = [enrollment.student for enrollment in enrollments]
        return EnrolledStudentSerializer(students, many=True, context={'course': obj}).data

    def get_current_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return {
                'id': request.user.id,
                'userprofile': {
                    'role': request.user.userprofile.role
                }
            }
        return None

class NoteSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        source='course',
        write_only=True
    )
    
    class Meta:
        model = Note
        fields = ['id', 'title', 'file', 'course', 'course_id', 'uploaded_by', 
                 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'uploaded_by', 'created_at', 'updated_at']

class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(userprofile__role='student'),
        source='student',
        write_only=True
    )
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        source='course',
        write_only=True
    )
    
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'student_id', 'course', 'course_id', 'enrollment_date']
        read_only_fields = ['id', 'enrollment_date']

class GradeSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    graded_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Grade
        fields = ['id', 'student', 'course', 'semester', 'assessment_type', 
                 'written_grade', 'participation', 'homework', 'final_grade', 
                 'comments', 'created_at', 'updated_at', 'graded_by']
        read_only_fields = ['id', 'final_grade', 'created_at', 'updated_at', 'graded_by', 'student', 'course']

class GradeReportSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    
    class Meta:
        model = GradeReport
        fields = ['id', 'student', 'course', 'semester', 'continuous_assessment_average', 
                 'exam_grade', 'final_average', 'created_at', 'updated_at']
        read_only_fields = ['id', 'continuous_assessment_average', 'final_average', 
                           'created_at', 'updated_at'] 