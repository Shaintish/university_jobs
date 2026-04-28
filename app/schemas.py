from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from enum import Enum

class JobType(str, Enum):
    INTERNSHIP = "internship"
    JOB = "job"

class ApplicationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class VacancyBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Название от 3 до 100 символов")
    description: str = Field(..., min_length=10, max_length=5000, description="Описание от 10 до 5000 символов")
    department: str = Field(..., min_length=2, max_length=50, description="Отдел от 2 до 50 символов")
    job_type: JobType
    salary: Optional[int] = Field(None, ge=0, le=1000000, description="Зарплата от 0 до 1 000 000 ₽")

    # Валидаторы
    @validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Название вакансии не может быть пустым')
        return v.strip()

    @validator('description')
    def description_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Описание не может быть пустым')
        return v.strip()

    @validator('department')
    def department_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Название отдела не может быть пустым')
        return v.strip()

class VacancyCreate(VacancyBase):
    pass

class Vacancy(VacancyBase):
    id: int

class ApplicationCreate(BaseModel):
    vacancy_id: int = Field(..., gt=0, description="ID вакансии должен быть больше 0")
    student_name: str = Field(..., min_length=2, max_length=100, description="Имя от 2 до 100 символов")
    student_email: EmailStr

    @validator('student_name')
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Имя не может быть пустым')
        return v.strip()

class Application(ApplicationCreate):
    id: int
    status: ApplicationStatus

# НОВЫЕ МОДЕЛИ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Логин от 3 до 50 символов")
    email: EmailStr
    password: str = Field(..., min_length=4, max_length=100, description="Пароль от 4 до 100 символов")

    @validator('username')
    def username_valid(cls, v):
        if not v or not v.strip():
            raise ValueError('Имя пользователя не может быть пустым')
        if not v.replace('_', '').isalnum():
            raise ValueError('Имя пользователя может содержать только буквы, цифры и знак подчеркивания')
        return v.strip()

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str
    email: EmailStr