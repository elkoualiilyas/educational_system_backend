"""
Value objects for the students application.
These are immutable objects that represent concepts in our domain.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import List
from enum import Enum

@dataclass(frozen=True)
class StudentId:
    """Value object representing a student's unique identifier"""
    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Student ID cannot be empty")
        if not self.value.isalnum():
            raise ValueError("Student ID must be alphanumeric")

@dataclass(frozen=True)
class GradePoint:
    """Value object representing a grade point"""
    value: Decimal

    def __post_init__(self):
        if not 0 <= self.value <= 20:
            raise ValueError("Grade must be between 0 and 20")

class AssessmentType(Enum):
    """Enumeration of possible assessment types"""
    CONTROL_1 = 'control_1'
    CONTROL_2 = 'control_2'
    EXAM = 'exam'

    @property
    def display_name(self) -> str:
        """Returns a human-readable name for the assessment type"""
        return {
            'control_1': 'Premier Contrôle',
            'control_2': 'Deuxième Contrôle',
            'exam': 'Examen Final'
        }[self.value]

@dataclass(frozen=True)
class Semester:
    """Value object representing a semester"""
    number: int
    year: int

    def __post_init__(self):
        if self.number not in (1, 2):
            raise ValueError("Semester number must be 1 or 2")
        if not 2000 <= self.year <= 2100:
            raise ValueError("Invalid year")

@dataclass(frozen=True)
class GPA:
    """Value object representing a Grade Point Average"""
    value: Decimal
    total_credits: int
    grades: List[GradePoint]

    def __post_init__(self):
        if not 0 <= self.value <= 20:
            raise ValueError("GPA must be between 0 and 20")
        if self.total_credits < 0:
            raise ValueError("Total credits cannot be negative")

    @classmethod
    def calculate(cls, grades: List[GradePoint], credits: List[int]) -> 'GPA':
        """Calculate GPA from a list of grades and credits"""
        if len(grades) != len(credits):
            raise ValueError("Number of grades must match number of credits")
        
        total_credits = sum(credits)
        if total_credits == 0:
            return cls(Decimal('0'), 0, grades)

        weighted_sum = sum(grade.value * credit for grade, credit in zip(grades, credits))
        gpa_value = weighted_sum / total_credits

        return cls(
            value=round(gpa_value, 2),
            total_credits=total_credits,
            grades=grades
        ) 