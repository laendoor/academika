from app.models.course import Course
from app.schemas.courses import CourseCreate, CourseUpdate
from app.services.base import BaseService


class CourseService(BaseService[Course, CourseCreate, CourseUpdate]):
    model = Course
