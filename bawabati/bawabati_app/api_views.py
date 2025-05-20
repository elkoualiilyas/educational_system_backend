from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import UserProfile, Course, Note, Enrollment, Grade, GradeReport
from .serializers import (
    UserSerializer, UserCreateSerializer, UserProfileSerializer,
    CourseSerializer, NoteSerializer, EnrollmentSerializer,
    GradeSerializer, GradeReportSerializer
)
from rest_framework.permissions import IsAdminUser, IsAuthenticated

# Authentication views
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        # Prevent admin registration through the API
        if serializer.validated_data.get('role') == 'admin':
            return Response(
                {'error': 'Administrator role cannot be assigned through registration.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = serializer.save()
        login(request, user)  # Log the user in after registration
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Please provide both username and password'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user:
        login(request, user)
        return Response({
            'user': UserSerializer(user).data,
            'message': 'Login successful'
        })
    else:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['POST'])
def logout_user(request):
    logout(request)
    return Response({'message': 'Logout successful'})

@api_view(['GET'])
def get_current_user(request):
    if request.user.is_authenticated:
        return Response(UserSerializer(request.user).data)
    return Response(
        {'error': 'Not authenticated'},
        status=status.HTTP_401_UNAUTHORIZED
    )

# User management views
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = User.objects.all()
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(userprofile__role=role)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Prevent admin registration through the API
            if serializer.validated_data.get('role') == 'admin':
                return Response({'error': 'Administrator role cannot be assigned through this form.'}, status=status.HTTP_400_BAD_REQUEST)
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Dashboard data views
@api_view(['GET'])
def admin_dashboard_data(request):
    if not request.user.is_authenticated or request.user.userprofile.role != 'admin':
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    users = User.objects.all()
    admin_count = users.filter(userprofile__role='admin').count()
    teacher_count = users.filter(userprofile__role='teacher').count()
    student_count = users.filter(userprofile__role='student').count()
    courses = Course.objects.all()
    
    return Response({
        'admin_count': admin_count,
        'teacher_count': teacher_count,
        'student_count': student_count,
        'courses': CourseSerializer(courses, many=True).data,
        'users': UserSerializer(users, many=True).data
    })

@api_view(['GET'])
def teacher_dashboard_data(request):
    if not request.user.is_authenticated or request.user.userprofile.role != 'teacher':
        return Response(
            {'error': 'Teacher access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    courses = Course.objects.filter(assigned_teacher=request.user)
    
    return Response({
        'courses': CourseSerializer(courses, many=True).data
    })

@api_view(['GET'])
def student_dashboard_data(request):
    if not request.user.is_authenticated or request.user.userprofile.role != 'student':
        return Response(
            {'error': 'Student access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    enrollments = Enrollment.objects.filter(student=request.user)
    
    return Response({
        'enrollments': EnrollmentSerializer(enrollments, many=True).data
    })

# Course views
@api_view(['GET'])
def course_list(request):
    try:
        specialisation = request.query_params.get('specialisation', None)
        queryset = Course.objects.all()
        
        if specialisation:
            queryset = queryset.filter(specialisation=specialisation)
            
        # Add enrollment status for students
        if request.user.is_authenticated and request.user.userprofile.role == 'student':
            for course in queryset:
                course.can_enroll = not Enrollment.objects.filter(
                    student=request.user,
                    course=course
                ).exists()
        
        serializer = CourseSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def course_detail(request, pk):
    try:
        course = Course.objects.get(pk=pk)
        serializer = CourseSerializer(course, context={'request': request})
        return Response(serializer.data)
    except Course.DoesNotExist:
        return Response(
            {'error': 'Course not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# User profile views
@api_view(['PUT'])
def update_profile(request):
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        user = request.user
        profile = user.userprofile
        
        # Update user fields
        if 'first_name' in request.data:
            user.first_name = request.data['first_name']
        if 'last_name' in request.data:
            user.last_name = request.data['last_name']
        if 'email' in request.data:
            user.email = request.data['email']
        user.save()
        
        # Update profile fields
        if 'phone_number' in request.data:
            profile.phone_number = request.data['phone_number']
        if 'bio' in request.data:
            profile.bio = request.data['bio']
        
        # Update specialisation for teachers and admins
        if profile.role in ['teacher', 'admin'] and 'specialisation' in request.data:
            profile.specialisation = request.data['specialisation']
        
        profile.save()
        
        return Response({
            'message': 'Profile updated successfully',
            'user': UserSerializer(user).data
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Note management views
@api_view(['POST'])
def upload_note(request, course_id):
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        course = Course.objects.get(pk=course_id)
        
        # Check if user is admin or the course teacher
        if not (request.user.userprofile.role == 'admin' or course.assigned_teacher == request.user):
            return Response(
                {'error': 'Only administrators and course teachers can upload notes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate required fields
        if not request.data.get('title'):
            return Response(
                {'error': 'Note title is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not request.FILES.get('file'):
            return Response(
                {'error': 'File is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create note
        note = Note.objects.create(
            course=course,
            title=request.data['title'],
            file=request.FILES['file'],
            uploaded_by=request.user
        )
        
        return Response({
            'message': 'Note uploaded successfully',
            'note': NoteSerializer(note).data
        }, status=status.HTTP_201_CREATED)
    except Course.DoesNotExist:
        return Response(
            {'error': 'Course not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def list_notes(request, course_id):
    try:
        course = Course.objects.get(pk=course_id)
        notes = Note.objects.filter(course=course)
        return Response(NoteSerializer(notes, many=True).data)
    except Course.DoesNotExist:
        return Response(
            {'error': 'Course not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
def delete_note(request, note_id):
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        note = Note.objects.get(pk=note_id)
        
        # Check if user is admin or the note uploader
        if not (request.user.userprofile.role == 'admin' or note.uploaded_by == request.user):
            return Response(
                {'error': 'Only administrators and note uploaders can delete notes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        note.delete()
        return Response({'message': 'Note deleted successfully'})
    except Note.DoesNotExist:
        return Response(
            {'error': 'Note not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_course(request):
    serializer = CourseSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        course = serializer.save()
        # Set enrolled students if provided
        if 'student_ids' in request.data:
            course.students.set(serializer.validated_data.get('students', []))
        return Response(CourseSerializer(course, context={'request': request}).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAdminUser])
def update_course(request, pk):
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = CourseSerializer(course, data=request.data, partial=(request.method == 'PATCH'), context={'request': request})
    if serializer.is_valid():
        course = serializer.save()
        # Set enrolled students if provided
        if 'student_ids' in request.data:
            course.students.set(serializer.validated_data.get('students', []))
        return Response(CourseSerializer(course, context={'request': request}).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_teachers(request):
    teachers = User.objects.filter(userprofile__role='teacher')
    return Response(UserSerializer(teachers, many=True).data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_students(request):
    students = User.objects.filter(userprofile__role='student')
    return Response(UserSerializer(students, many=True).data)

@api_view(['GET'])
def list_grades(request, course_id):
    try:
        course = Course.objects.get(pk=course_id)
        
        # Check permissions
        if request.user.userprofile.role == 'student':
            # Students can only view their own grades
            grades = Grade.objects.filter(course=course, student=request.user)
            reports = GradeReport.objects.filter(course=course, student=request.user)
        elif request.user.userprofile.role == 'teacher':
            # Teachers can view grades for their courses
            if course.assigned_teacher != request.user:
                return Response(
                    {'error': 'You are not authorized to view grades for this course'},
                    status=status.HTTP_403_FORBIDDEN
                )
            grades = Grade.objects.filter(course=course)
            reports = GradeReport.objects.filter(course=course)
        elif request.user.userprofile.role == 'admin':
            # Admins can view all grades
            grades = Grade.objects.filter(course=course)
            reports = GradeReport.objects.filter(course=course)
        else:
            return Response(
                {'error': 'You are not authorized to view grades'},
                status=status.HTTP_403_FORBIDDEN
            )
        
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
        if request.user.userprofile.role == 'student':
            reports = GradeReport.objects.filter(course=course, student=request.user)
        else:
            reports = GradeReport.objects.filter(course=course)
        
        return Response({
            'grades': GradeSerializer(grades, many=True).data,
            'reports': GradeReportSerializer(reports, many=True).data
        })
    except Course.DoesNotExist:
        return Response(
            {'error': 'Course not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_grade(request, course_id, student_id):
    try:
        course = Course.objects.get(pk=course_id)
        student = User.objects.get(pk=student_id)
        # Only allow if user is admin or the assigned teacher
        if not (
            request.user.userprofile.role == 'admin' or
            (request.user.userprofile.role == 'teacher' and course.assigned_teacher == request.user)
        ):
            return Response({'error': 'Not authorized'}, status=403)
        # Check student is enrolled
        if not Enrollment.objects.filter(course=course, student=student).exists():
            return Response({'error': 'Student is not enrolled in this course'}, status=400)
        # Get semester and assessment_type from request data
        semester = request.data.get('semester')
        assessment_type = request.data.get('assessment_type')
        if not semester or not assessment_type:
            return Response({'error': 'Semester and assessment type are required.'}, status=400)
        # Prepare data for serializer (include semester and assessment_type)
        data = {
            'written_grade': request.data.get('written_grade'),
            'participation': request.data.get('participation'),
            'homework': request.data.get('homework'),
            'comments': request.data.get('comments', ''),
            'semester': semester,
            'assessment_type': assessment_type,
        }
        serializer = GradeSerializer(data=data)
        if serializer.is_valid():
            grade = serializer.save(
                course=course,
                student=student,
                graded_by=request.user
            )
            return Response(GradeSerializer(grade).data, status=201)
        return Response(serializer.errors, status=400)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=404)
    except User.DoesNotExist:
        return Response({'error': 'Student not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500) 