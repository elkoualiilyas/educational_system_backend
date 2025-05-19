"""
Repository interfaces for the students application.
These define the contract for data access without implementation details.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date

from .entities import StudentProfile, Enrollment, Grade, AcademicRecord
from .value_objects import StudentId, Semester, AssessmentType

class StudentRepository(ABC):
    """Abstract base class for student data access"""
    
    @abstractmethod
    async def get_by_id(self, student_id: StudentId) -> Optional[StudentProfile]:
        """Retrieve a student by their ID"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[StudentProfile]:
        """Retrieve a student by their email"""
        pass

    @abstractmethod
    async def save(self, student: StudentProfile) -> StudentProfile:
        """Save or update a student profile"""
        pass

    @abstractmethod
    async def delete(self, student_id: StudentId) -> bool:
        """Delete a student profile"""
        pass

    @abstractmethod
    async def list_active(self) -> List[StudentProfile]:
        """List all active students"""
        pass

class EnrollmentRepository(ABC):
    """Abstract base class for enrollment data access"""

    @abstractmethod
    async def get_student_enrollments(self, student_id: StudentId) -> List[Enrollment]:
        """Get all enrollments for a student"""
        pass

    @abstractmethod
    async def enroll_student(self, enrollment: Enrollment) -> Enrollment:
        """Create a new enrollment"""
        pass

    @abstractmethod
    async def unenroll_student(self, student_id: StudentId, course_id: int) -> bool:
        """Remove a student's enrollment"""
        pass

    @abstractmethod
    async def is_enrolled(self, student_id: StudentId, course_id: int) -> bool:
        """Check if a student is enrolled in a course"""
        pass

class GradeRepository(ABC):
    """Abstract base class for grade data access"""

    @abstractmethod
    async def get_student_grades(
        self, 
        student_id: StudentId,
        semester: Optional[Semester] = None
    ) -> List[Grade]:
        """Get all grades for a student, optionally filtered by semester"""
        pass

    @abstractmethod
    async def get_course_grades(
        self,
        student_id: StudentId,
        course_id: int,
        assessment_type: Optional[AssessmentType] = None
    ) -> List[Grade]:
        """Get grades for a specific course"""
        pass

    @abstractmethod
    async def save_grade(self, grade: Grade) -> Grade:
        """Save or update a grade"""
        pass

    @abstractmethod
    async def get_academic_record(self, student_id: StudentId) -> AcademicRecord:
        """Get complete academic record for a student"""
        pass

class UnitOfWork(ABC):
    """Abstract base class for managing transactions"""

    students: StudentRepository
    enrollments: EnrollmentRepository
    grades: GradeRepository

    @abstractmethod
    async def __aenter__(self):
        """Start a new transaction"""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """End the transaction"""
        pass

    @abstractmethod
    async def commit(self):
        """Commit the transaction"""
        pass

    @abstractmethod
    async def rollback(self):
        """Rollback the transaction"""
        pass 