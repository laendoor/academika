from app.models.student import Student
from app.schemas.students import StudentCreate, StudentUpdate
from app.services.base import BaseService


class StudentService(BaseService[Student, StudentCreate, StudentUpdate]):
    model = Student
