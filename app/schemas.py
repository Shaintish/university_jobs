from pydantic import BaseModel, EmailStr
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
    title: str
    description: str
    department: str
    job_type: JobType
    salary: Optional[int] = None
    
class VacancyCreate(VacancyBase):
    pass

class Vacancy(VacancyBase):
    id: int

class ApplicationCreate(BaseModel):
    vacancy_id: int
    student_name: str
    student_email: EmailStr

class Application(ApplicationCreate):
    id: int
    status: ApplicationStatus