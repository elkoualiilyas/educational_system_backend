"""
Domain entities for the students application.
These are pure Python classes that represent the core business objects.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional, List
from decimal import Decimal

@dataclass
class StudentProfile:
    """Core student profile entity"""
    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    student_id: str
    date_of_birth: date
    phone_number: Optional[str] = None
    address: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    profile_image: Optional[str] = None

    @property
    def full_name(self) -> str:
        """Returns the student's full name"""
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self) -> int:
        """Calculate student's age"""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

@dataclass
class Enrollment:
    """Student enrollment in a course"""
    id: int
    student_id: int
    course_id: int
    enrollment_date: date

@dataclass
class Grade:
    """Student grade for an assessment"""
    id: int
    student_id: int
    course_id: int
    semester: int
    assessment_type: str
    written_grade: Decimal
    participation: Optional[Decimal] = None
    homework: Optional[Decimal] = None
    final_grade: Optional[Decimal] = None
    comments: Optional[str] = None
    graded_by: int = None
    created_at: date = None
    updated_at: date = None

@dataclass
class AcademicRecord:
    """Student's complete academic record"""
    student: StudentProfile
    enrollments: List[Enrollment]
    grades: List[Grade]
    gpa: Decimal

    def calculate_semester_average(self, semester: int) -> Optional[Decimal]:
        """Calculate the average grade for a specific semester"""
        semester_grades = [g.final_grade for g in self.grades 
                         if g.semester == semester and g.final_grade is not None]
        if not semester_grades:
            return None
        return sum(semester_grades) / len(semester_grades)

    def get_course_grades(self, course_id: int) -> List[Grade]:
        """Get all grades for a specific course"""
        return [g for g in self.grades if g.course_id == course_id] 