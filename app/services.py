from .schemas import VacancyCreate, Vacancy, ApplicationCreate, Application, ApplicationStatus, UserCreate, User
from .database import (
    save_user, get_user_by_username, get_user_by_email,
    save_vacancy, get_all_vacancies, get_vacancy,
    save_application, get_applications_by_email, get_all_applications,
    update_application_status, get_application,
    save_chat, get_chat_by_application, get_chats_by_student_email, get_all_chats,
    save_message, get_messages_by_application
)
from fastapi import HTTPException


class JobService:
    @staticmethod
    def create_vacancy(data: VacancyCreate):
        vacancy_id = save_vacancy(
            title=data.title,
            description=data.description,
            department=data.department,
            job_type=data.job_type,
            salary=data.salary,
            employer_id=None
        )
        return {"id": vacancy_id, **data.model_dump()}

    @staticmethod
    def get_all_vacancies(search: str = None):
        return get_all_vacancies(search)

    @staticmethod
    def create_vacancy(data: VacancyCreate):
        vacancy_id = save_vacancy(
        title=data.title,
        description=data.description,
        department=data.department,
        job_type=data.job_type,
        salary=data.salary,
        employer_id=None
    )
        return {"id": vacancy_id, **data.model_dump()}

    @staticmethod
    def create_application(data: ApplicationCreate, user_id: int = None):
        vacancy = JobService.get_vacancy(data.vacancy_id)
        if not vacancy:
            raise HTTPException(status_code=404, detail="Вакансия не существует")
    
        app_id = save_application(
        vacancy_id=data.vacancy_id,
        student_name=data.student_name,
        student_email=data.student_email,
        status='pending'
    )
        return {
        "id": app_id,
        "vacancy_id": data.vacancy_id,
        "student_name": data.student_name,
        "student_email": data.student_email,
        "status": "pending"
    }

    @staticmethod
    def get_application(app_id: int):
        app = get_application(app_id)
        if not app:
            raise HTTPException(status_code=404, detail="Заявка не найдена")
        return app

    @staticmethod
    def get_applications_by_email(email: str):
        return get_applications_by_email(email)

    @staticmethod
    def get_all_applications():
        return get_all_applications()

    @staticmethod
    def update_application_status(app_id: int, new_status: str):
        update_application_status(app_id, new_status)
        return get_application(app_id)

    @staticmethod
    def create_chat(application_id: int, student_email: str, student_name: str, vacancy_id: int, vacancy_title: str):
        save_chat(application_id, student_email, student_name, vacancy_id, vacancy_title)
        return get_chat_by_application(application_id)

    @staticmethod
    def get_chat_by_application(application_id: int):
        return get_chat_by_application(application_id)

    @staticmethod
    def get_chats_by_student_email(email: str):
        return get_chats_by_student_email(email)

    @staticmethod
    def get_all_chats():
        return get_all_chats()

    @staticmethod
    def add_message(application_id: int, sender: str, sender_name: str, text: str):
        save_message(application_id, sender, sender_name, text)
        return {"status": "ok"}

    @staticmethod
    def get_messages_by_application(application_id: int):
        return get_messages_by_application(application_id)


class UserService:
    @staticmethod
    def register(data: UserCreate):
        existing = get_user_by_username(data.username)
        if existing:
            raise HTTPException(status_code=400, detail="Пользователь уже существует")
        existing_email = get_user_by_email(data.email)
        if existing_email:
            raise HTTPException(status_code=400, detail="Email уже используется")
        
        user_id = save_user(data.username, data.email, data.password, 'student')
        return {"id": user_id, "username": data.username, "email": data.email, "role": "student"}

    @staticmethod
    def login(username: str, password: str):
        user = get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        if user["password"] != password:
            raise HTTPException(status_code=401, detail="Неверный пароль")
        return user