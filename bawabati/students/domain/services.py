"""
Domain services for the students application.
These handle complex business logic that doesn't naturally fit within entities.
"""

from datetime import date
from typing import List, Optional
from decimal import Decimal

from bawabati.bawabati_app.models import Course

from .entities import Enrollment, StudentProfile, Grade, AcademicRecord
from .value_objects import StudentId, GradePoint, Semester, AssessmentType
from .repositories import UnitOfWork

class GradeCalculationService:
    """Service for handling complex grade calculations"""

    @staticmethod
    def calculate_continuous_assessment(grades: List[Grade]) -> Optional[Decimal]:
        """Calculate continuous assessment average from control grades"""
        control_grades = [g.final_grade for g in grades 
                        if g.assessment_type in (AssessmentType.CONTROL_1.value, AssessmentType.CONTROL_2.value)
                        and g.final_grade is not None]
        
        if not control_grades:
            return None
            
        return round(sum(control_grades) / len(control_grades), 2)

    @staticmethod
    def calculate_final_average(continuous_assessment: Decimal, exam_grade: Decimal) -> Decimal:
        """Calculate final average using 40% continuous assessment and 60% exam"""
        return round((continuous_assessment * Decimal('0.4')) + (exam_grade * Decimal('0.6')), 2)

class AcademicRecordService:
    """Service for managing student academic records"""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_student_record(self, student_id: StudentId) -> AcademicRecord:
        """Get complete academic record for a student"""
        async with self.uow:
            student = await self.uow.students.get_by_id(student_id)
            if not student:
                raise ValueError(f"Student {student_id.value} not found")

            enrollments = await self.uow.enrollments.get_student_enrollments(student_id)
            grades = await self.uow.grades.get_student_grades(student_id)
            
            # Calculate GPA
            grade_points = [GradePoint(g.final_grade) for g in grades if g.final_grade is not None]
            credits = [1] * len(grade_points)  # Assuming 1 credit per course for simplicity
            gpa = GradePoint.calculate(grade_points, credits)

            return AcademicRecord(
                student=student,
                enrollments=enrollments,
                grades=grades,
                gpa=gpa.value
            )

class EnrollmentService:
    """Service for managing student enrollments"""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def enroll_student(self, student_id: StudentId, course_id: int) -> bool:
        """Enroll a student in a course"""
        async with self.uow:
            # Check if student exists
            student = await self.uow.students.get_by_id(student_id)
            if not student:
                raise ValueError(f"Student {student_id.value} not found")

            # Check if already enrolled
            if await self.uow.enrollments.is_enrolled(student_id, course_id):
                return False

            # Create enrollment
            enrollment = Enrollment(
                id=None,  # Will be set by repository
                student_id=student_id.value,
                course_id=course_id,
                enrollment_date=date.today()
            )
            
            await self.uow.enrollments.enroll_student(enrollment)
            await self.uow.commit()
            return True

    async def get_student_courses(self, student_id: StudentId) -> List[Course]:
        """Get all courses a student is enrolled in"""
        async with self.uow:
            enrollments = await self.uow.enrollments.get_student_enrollments(student_id)
            return [e.course for e in enrollments] 