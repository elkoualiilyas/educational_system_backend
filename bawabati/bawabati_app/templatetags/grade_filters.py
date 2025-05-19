from django import template
from django.template.defaultfilters import stringfilter
from django.contrib.auth.models import User
from decimal import Decimal

register = template.Library()

@register.filter
def filter_grades(grades, args):
    """Filter grades by assessment type and semester"""
    assessment_type = args.rstrip(',')  # Remove trailing comma if present
    return [g for g in grades if g.assessment_type == assessment_type]

@register.filter
def filter_grades_by_semester(grades, semester):
    """Filter grades by semester"""
    return [g for g in grades if g.semester == int(semester)]

@register.filter
def filter_reports(reports, args):
    """Filter reports by student and semester"""
    if isinstance(args, str):
        if ',' in args:
            try:
                student_id, semester = args.split(',')
                if isinstance(student_id, User):
                    student = student_id
                else:
                    student = User.objects.get(pk=student_id)
                filtered_reports = [r for r in reports if r.student == student and r.semester == int(semester)]
                return filtered_reports
            except (ValueError, User.DoesNotExist):
                return []
    # If args is a User object
    return [r for r in reports if r.student == args]

@register.filter
def regroup_by(grades, field):
    """Regroup grades by a field"""
    groups = {}
    for grade in grades:
        key = getattr(grade, field)
        if key not in groups:
            groups[key] = []
        groups[key].append(grade)
    
    # Sort keys based on username if grouping by student
    if field == 'student':
        sorted_keys = sorted(groups.keys(), key=lambda x: x.username.lower())
    else:
        sorted_keys = sorted(groups.keys())
    
    return [{'grouper': key, 'list': groups[key]} for key in sorted_keys]

@register.filter
def ordinal(n):
    """Convert number to ordinal string (1st, 2nd, etc.)"""
    n = int(n)
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    return f"{n}{suffix}" 