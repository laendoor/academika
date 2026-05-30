from app.models.course import Course
from app.models.course_enrollment import CourseEnrollment
from app.models.course_prerequisite import CoursePrerequisite
from app.models.degree import Degree
from app.models.lkp_academic_status import LkpAcademicStatus
from app.models.lkp_enrollment_status import LkpEnrollmentStatus
from app.models.lkp_enrollment_type import LkpEnrollmentType
from app.models.student import Student
from app.models.study_plan import StudyPlan, study_plan_course

__all__ = [
    "Course",
    "CourseEnrollment",
    "CoursePrerequisite",
    "Degree",
    "LkpAcademicStatus",
    "LkpEnrollmentStatus",
    "LkpEnrollmentType",
    "Student",
    "StudyPlan",
    "study_plan_course",
]
